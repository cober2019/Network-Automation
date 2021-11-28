"""Collection of functions that get data from a device using Restconf"""

from json.decoder import JSONDecodeError
import requests
import json
import warnings
import ipaddress
import device_call_backup as InCaseRestDoesntWork

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def _check_api_error(response) -> bool:

    is_error = False

    try:
        if list(response.keys())[0] == 'errors':
            is_error = True
    except IndexError:
        pass
    
    return is_error

def get_poe(ip, port, username, password) -> list:
    """Collects poe port information"""

    poe_ports = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-poe-oper:poe-oper-data"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        poe = json.loads(response.text)

        check_error = _check_api_error(poe)

        if check_error:
            raise AttributeError
    
        poe_ports = poe.get('Cisco-IOS-XE-poe-oper:poe-oper-data', {}).get('poe-port', {})

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, AttributeError) as e:
        pass

    return poe_ports

def get_sfps(ip, port, username, password) -> list:
    """Collects device transcievers"""

    transceiver_ports = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-transceiver-oper:transceiver-oper-data"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        transceivers = json.loads(response.text)

        check_error = _check_api_error(transceivers)

        if check_error:
            raise AttributeError
    
        transceiver_ports = transceivers.get('Cisco-IOS-XE-transceiver-oper:transceiver-oper-data', {}).get('transceiver', {})

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, AttributeError) as e:
        pass

    return transceiver_ports

def get_arps(ip, port, username, password) -> list:
    """Collects arp for the matching"""

    entries = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        arp_entries = json.loads(response.text, strict=False)

        check_error = _check_api_error(arp_entries)

        if check_error:
            raise AttributeError

        try:
            for i in  arp_entries.get('Cisco-IOS-XE-arp-oper:arp-vrf'):
                for entry in i.get('arp-oper'):
                    entry.pop('interface')
                    entry['vrf'] = i.get('vrf')
                    entry['interface'] = 'n/a'
                    entry['time'] = entry.get('time').split('.')[0].strip('T00')
                    entries.append(entry)
        except (TypeError, AttributeError):
            pass

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, AttributeError):
        entries = InCaseRestDoesntWork.get_arp(username, password, ip)

    return entries

def get_ip_sla(ip, port, username, password) -> list:
    """Collects ip sla statuses"""

    sla_stats = []

    try:
        uri = f"https://{ip}:443/restconf/data/Cisco-IOS-XE-ip-sla-oper:ip-sla-stats"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        slas = json.loads(response.text)

        check_error = _check_api_error(slas)

        if check_error:
            raise AttributeError
        
        sla_stats = slas.get('Cisco-IOS-XE-ip-sla-oper:ip-sla-stats', {}).get('sla-oper-entry', {})
    
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, AttributeError) as e:
        pass

    return sla_stats

def get_interfaces(ip, port, username, password) -> dict:
    """Gets real time interface statistics using IOS-XE\n
        Cisco-IOS-XE-interfaces-oper:interfaces and live arp data via Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"""

    data = {}
    interface_data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        interface_data = json.loads(response.text).get('Cisco-IOS-XE-interfaces-oper:interfaces').get('interface')
        check_error = _check_api_error(interface_data)

        if check_error:
            raise AttributeError

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass
    
    if interface_data:
        try:
            uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"
            response = requests.get(uri, headers=headers, verify=False, auth=(username, password))

            for interface in interface_data:
                #Collect inter qos statistics. Commence policy breakdown
                qos_stats = collect_qos_stats(interface, ip, port, username, password)
                convert_bandwidth = convert_to_mbps(interface)
                data[interface.get('name')] = {'interface': interface.get('name'), 'data': convert_bandwidth, 'qos': qos_stats}
                
        except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            for interface in interface_data:
                convert_bandwidth = convert_to_mbps(interface)
                data[interface.get('name')] = {'interface': interface.get('name'), 'data': convert_bandwidth, 'qos': [[]]}

    return data

def collect_qos_stats(interface, ip, port, username, password) -> list:
    """Collect interface service policies, breaks down policy."""

    qos = []

    # The following code will compare two sets of data. Interface queue stats and service policy config. Unfortunently we cant get this data as one

    for policy in interface.get('diffserv-info', {}):
        try:
            #Get qos policy map details using rest and a name filter in out url path
            uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/policy/policy-map={policy.get('policy-name')}"
            response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
            check_error = _check_api_error(json.loads(response.text))

            if check_error:
                raise AttributeError

            #Get policy detials. Type, Allocation etc.
            allocation = _get_qos_bandwidth(json.loads(response.text))

            if not policy.get('diffserv-target-classifier-stats'):
                qos = []
            elif isinstance(policy.get('diffserv-target-classifier-stats'), list):
                #Use list comp to get out queue details, also map other details

                if not allocation:
                    qos = []
                elif len(allocation) == 1:
                    qos = [{'interface_policy': policy.get('policy-name', {}), 'allocation': allocation[0].get('allocation', {}), 
                    'direction': policy.get('direction', {}).split('-')[1], 'queues': _map_queues(allocation[0], policy)}]
                else:
                    qos = [
                        
                        {'interface_policy': policy.get('policy-name', {}), 'allocation': i.get('allocation', {}), 
                        'direction': policy.get('direction', {}).split('-')[1], 'queues': _map_queues(i, policy)}
                        
                        for i in allocation
                    
                        ]
        except AttributeError:
             pass

    return qos

def _get_qos_bandwidth(policy) -> list:
    """Break down each child policy"""

    parent_queues = []

    #Get parent policy actions and action type. ie.e bandwdith, service-policy, fair-queue etc.
    for queue in policy.get('Cisco-IOS-XE-policy:policy-map', {}).get('class', {}):
        try:
            if isinstance(queue.get('action-list', {}), list):
                allocation = [_allocation_type(action) for action in queue.get('action-list', {})]
                if len(allocation) == 1 and str(allocation) != '[(\'---\', \'---\')]':
                    parent_queues.append({'queue': queue.get('name'), 'allocation': allocation[0][0], 'type': allocation[0][1]})
                elif len(allocation) == 2:
                    parent_queues.append({'queue': queue.get('name'), 'allocation': allocation[0][0], 'type': allocation[1]})
        except IndexError:
            pass

    return parent_queues

def _allocation_type(action) -> tuple:
    """Get details of child policy"""

    allocation = '---'
    action_type = '---'

    if action.get("action-type",{}) == 'shape':
        if 'bit-rate' in action.get('shape',{}).get('average',{}):
            allocation = str(round(int(action.get("shape",{}).get("average",{}).get("bit-rate",{})) / 1e+6)) + " Mbps"
        elif 'percent' in action.get('shape',{}).get('average'):
            allocation = str(action.get("shape",{}).get("average",{}).get("percent",{})) + "%"

    elif action.get("action-type",{}) == 'bandwidth':
        if 'kilo-bits' in action.get('bandwidth', {}):
            allocation = str(round(int(action.get("bandwidth",{}).get("kilo-bits",{})) * 1000 / 1e+6)) + " Mbps"
        elif 'percent' in action.get('bandwidth', {}):
            allocation = str(action.get("bandwidth",{}).get("percent",{})) + '%'

    if action.get("action-type",{}) == 'service-policy':
        action_type = 'service-policy'
    elif action.get("action-type",{}) == 'fair-queue':
        action_type = 'fair-queue'

    return allocation, action_type
    
def _map_queues(i, policy) -> list:
    
    queues = []

    # Check if policy type is service policy. When then can get our queue detiials
    if 'service-policy' in i.get('type'):
        for queue in policy.get('diffserv-target-classifier-stats', {}):
            #Parent path provided allows use to check if the queue is a child queue. 1st path part is Parent Policy, second is a paren queue, anything after is child
            if len(queue.get('parent-path').split()) != 2:
                queues.append({'queue-name': queue.get('classifier-entry-name'), 'parent': " ".join(queue.get('parent-path').split(" ")[0:2]),
                'rate': queue.get('classifier-entry-stats').get('classified-rate'), 'bytes': queue.get('classifier-entry-stats').get('classified-bytes'),
                'pkts': queue.get('classifier-entry-stats').get('classified-pkts'), 'drops': queue.get('queuing-stats').get('drop-bytes'), 
                'tail-drops': queue.get('queuing-stats').get('wred-stats').get('tail-drop-bytes')})
            elif len(queue.get('parent-path').split()) == 2 and queue.get('classifier-entry-name') == i.get('queue'):
                queues.append({'queue-name': f'Parent Queue: {queue.get("classifier-entry-name")}'})

    elif '---' in i.get('type'):
        # This maps if the queue is not service policy. A single queue with no child
        queues = [
                    {'queue-name': f'Parent Queue: {queue.get("classifier-entry-name")}'} 
                    for queue in policy.get('diffserv-target-classifier-stats', {}) 
                    if len(queue.get('parent-path').split()) == 2 and queue.get('classifier-entry-name') == i.get('queue')
                ]
    return queues


def convert_to_mbps(interface) -> dict:
    """Convert Kbps to Mbps"""

    interface['statistics']['tx-kbps'] = int(interface['statistics']['tx-kbps']) / 1000
    interface['statistics']['rx-kbps'] = int(interface['statistics']['rx-kbps']) / 1000
    if interface['oper-status'] == 'if-oper-state-ready':
        interface['oper-status'] = 'up'
    else:
        interface['oper-status'] = 'down'

    return interface

def get_cpu_usages(ip, port, username, password) -> tuple:
    """Gets real time CPU statistics using restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage"""

    cpu_stats = {}
    memory_stats = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        cpu_stats = json.loads(response.text)
        check_error = _check_api_error(cpu_stats)

        if check_error:
            raise AttributeError

    except Exception:
        cpu_stats = {'Cisco-IOS-XE-process-cpu-oper:cpu-utilization': {'cpu-usage-processes': {'cpu-usage-process': []},'five-seconds': 'Err', 'one-minute': 'Err', 'five-minutes': 'Err'}}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes/control-process"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        memory_stats = json.loads(response.text)

        check_error = _check_api_error(cpu_stats)

        if check_error:
            raise AttributeError

        memory_stats = memory_stats.get('Cisco-IOS-XE-platform-software-oper:control-process')[0].get('memory-stats', {})

    except Exception:
        memory_stats = {'memory-status': 'Err'}
    
    return cpu_stats, memory_stats

def get_hardware_status(ip, port, username, password) -> dict:
    """Gets CPU memory statuses IOS-XE\n
        Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes/control-process"""

    ###### Future Use

    data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes/control-process"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        hardware_status = json.loads(response.text)

        check_error = _check_api_error(hardware_status)
        
        if check_error:
            raise AttributeError

        get_keys = dict.fromkeys(hardware_status)
        parent_key = list(get_keys.keys())[0]
        data = hardware_status[parent_key]

    except AttributeError:
        pass

    return data


def get_envirmoment(ip, port, username, password) -> dict:
    """Gets real time enviroment statistics using restconf/data/Cisco-IOS-XE-environment-oper:environment-sensors"""

    env_data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-environment-oper:environment-sensors"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        env = json.loads(response.text)

        check_error = _check_api_error(env)
        
        if check_error:
            raise AttributeError

        env_data = env.get('Cisco-IOS-XE-environment-oper:environment-sensors', {}).get('environment-sensor')

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return env_data

def get_prefix_list(ip, port, username, password) -> list:
    """Gets prefix-lists from device"""

    prefix_data = [{'name': 'No Prefix-lists Found'}]
    asr_uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/ip/prefix-list"
    csr_uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/ip/prefix-lists"

    try:
        response = requests.get(asr_uri, headers=headers, verify=False, auth=(username, password))
        
        if response.status_code == 204:
            response = requests.get(csr_uri, headers=headers, verify=False, auth=(username, password))
            prefix_lists = json.loads(response.text)
            check_error = _check_api_error(prefix_lists)

            if check_error:
                raise AttributeError
            else:
                prefix_data = prefix_lists.get('Cisco-IOS-XE-native:prefix-lists', {}).get('prefixes')
        else:
            prefix_lists = json.loads(response.text)
            check_error = _check_api_error(prefix_lists)
        
            if check_error:
                raise AttributeError

            prefix_data = prefix_lists.get('Cisco-IOS-XE-native:prefix-list', {}).get('prefixes')

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, TypeError):
        pass

    return prefix_data

def get_route_maps(ip, port, username, password) -> list:
    """Gets route-maps from device"""

    route_map_data = [{'name': 'No Route-maps Found'}]

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/route-map"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        route_maps = json.loads(response.text)

        check_error = _check_api_error(route_maps)
        
        if check_error or len(route_maps.get('Cisco-IOS-XE-native:route-map', {})) == 0:
            raise AttributeError

        route_map_data = route_maps.get('Cisco-IOS-XE-native:route-map', {})

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return route_map_data

def get_components(ip, port, username, password) -> dict:
    """Gets device components /restconf/data/openconfig-platform:components"""

    data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/openconfig-platform:components"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        data = json.loads(response.text)
    except (JSONDecodeError, requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return data

def get_ospf(ip, port, username, password) -> tuple:
    """Gets device ospf operational data"""

    ospf_neighbors = []
    ospf_interfaces = []
    topology = [{}]

    try:

        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/ospf-instance"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        ospf = json.loads(response.text)

        check_error = _check_api_error(ospf)

        if check_error:
            raise AttributeError

        for instance in ospf.get('Cisco-IOS-XE-ospf-oper:ospf-instance', {}):
            try:
                topology.append(str(ipaddress.IPv4Address(instance.get('router-id', {}))))
            except ValueError:
                pass

            for area in instance.get('ospf-area', {}):
                if isinstance(area.get('ospf-interface', {}), list):
                    for interface in area.get('ospf-interface', {}):
                        interface['area'] = area.get('area-id', {})
                        for neighbor in interface.get('ospf-neighbor', {}):
                            interface['neighbor-state'] = neighbor
                            neighbor['area'] = area.get('area-id', {})
                            ospf_neighbors.append(neighbor)
                            ospf_interfaces.append(interface)

        for i in ospf_interfaces:
            topology[0][i.get('neighbor-state').get('neighbor-id')] = None

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, TypeError):
        pass
    
    return ospf_neighbors, ospf_interfaces, topology

def get_bridge(ip, port, username, password) -> list:
    """Gets device components /restconf/data/openconfig-platform:components"""

    mac_table = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-matm-oper:matm-oper-data"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        bridge_data = json.loads(response.text)

        check_error = _check_api_error(bridge_data)
        
        if check_error or response.status_code == 404:
            raise AttributeError

        for i in bridge_data['Cisco-IOS-XE-matm-oper:matm-oper-data']['matm-table']:
            if i.get('matm-mac-entry', {}):
                [mac_table.append(i) for i in i.get('matm-mac-entry', {})]
                
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        mac_table = InCaseRestDoesntWork.get_mac_table(username, password, ip)
    
    return mac_table

def get_span_tree(ip, port, username, password) -> tuple:
    """Gets device components /restconf/data/openconfig-platform:components"""

    span_data = []
    span_global_data = []

    try:
        span_response = requests.get(f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-spanning-tree-oper:stp-details", headers=headers, verify=False, auth=(username, password))
        span_table = json.loads(span_response.text)

        check_error = _check_api_error(span_table)
        
        if check_error:
            raise AttributeError

        span_data = span_table.get('Cisco-IOS-XE-spanning-tree-oper:stp-details', {}).get('stp-detail', {})

        span_global_response = requests.get(f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-spanning-tree-oper:stp-details/stp-global", headers=headers, verify=False, auth=(username, password))
        span_global_table = json.loads(span_global_response.text)

        check_error = _check_api_error(span_global_table)
        
        if check_error:
            raise AttributeError

        span_global_data = span_global_table.get('Cisco-IOS-XE-spanning-tree-oper:stp-global', {})

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return span_data, span_global_data


def get_dp_neighbors(ip, port, username, password) -> list:
    """Gets device components restconf/data/Cisco-IOS-XE-cdp-oper:cdp-neighbor-details"""

    dp_neighbors = {'cdp': [], 'lldp': []}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-cdp-oper:cdp-neighbor-details"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        cdp_data = json.loads(response.text)

        check_error = _check_api_error(cdp_data)
        
        if check_error:
            raise AttributeError

        dp_neighbors['cdp'] = [neighbor for neighbor in cdp_data.get('Cisco-IOS-XE-cdp-oper:cdp-neighbor-details', {}).get('cdp-neighbor-detail', {})]

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
         pass
   

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        lldp_data = json.loads(response.text)

        check_error = _check_api_error(lldp_data)
        
        if check_error:
            raise AttributeError

        dp_neighbors['lldp'] = [neighbor for neighbor in lldp_data.get('Cisco-IOS-XE-lldp-oper:lldp-entries', {}).get('lldp-entry', {})]
           
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return dp_neighbors['cdp'], dp_neighbors['lldp']


def get_vlans(ip, port, username, password) -> list:
    """Gets device components /restconf/data/openconfig-platform:components"""

    vlan_data = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-vlan-oper:vlans"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        vlans = json.loads(response.text)

        check_error = _check_api_error(vlans)
        
        if check_error:
            raise AttributeError

        for i in vlans.get('Cisco-IOS-XE-vlan-oper:vlans', {}).get('vlan', {}):
            try:
                if i.get('vlan-interfaces'):
                    vlan_data.append({"id": i.get('id'), "name": i.get('name'), "status": i.get('status'), "interfaces": ", ".join([interface.get('interface') for interface in i.get('vlan-interfaces')])})
                else:
                    vlan_data.append({"id": i.get('id'), "name": i.get('name'), "status": i.get('status'), "interfaces": []})
            except TypeError:
                pass

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
         pass
        
    return vlan_data

def get_switch(ip, port, username, password) -> tuple:
    """Gets device components /restconf/data/openconfig-platform:components"""

    data = {}
    trunk =[]
    access = []

    try:
        interfaces_configs = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/interface"
        interface_status = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
        config_response = requests.get(interfaces_configs, headers=headers, verify=False, auth=(username, password))
        config_json = json.loads(config_response.text)
        check_error = _check_api_error(config_json)
        
        if check_error:
            raise AttributeError

        stats_response = requests.get(interface_status, headers=headers, verify=False, auth=(username, password))
        interface_stats = json.loads(stats_response.text)
        check_error = _check_api_error(interface_stats)
        
        if check_error:
            raise AttributeError

        for interface, v in config_json['Cisco-IOS-XE-native:interface'].items():
            if isinstance(v, list):
                mapped = [map_switchports(config, interface, interface_stats) for config in v]
                data[interface] = list(mapped)

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, KeyError, AttributeError):
        pass

    if data:
        for v in data.values():
            for i in v:
                if i[0].get('mode') == 'trunk':
                    i[0]
                    trunk.append(i[0])
                elif i[0].get('mode') == 'access':
                    access.append(i[0])
                    
    return trunk, access

def map_switchports(config, interface, interfaces_statuses) -> list:

    complete_interface = f"{interface}{config.get('name')}"
    interface_mode = False
    data = []
    statistics = next((interface for interface in interfaces_statuses['Cisco-IOS-XE-interfaces-oper:interfaces']['interface'] if interface['name'] == complete_interface), None)

    if config.get('switchport', {}).get('Cisco-IOS-XE-switch:mode', {}):
        interface_mode =  list(config.get('switchport', {}).get('Cisco-IOS-XE-switch:mode', {}).keys())[0]

    if interface_mode == 'access':
        access_vlan = config.get('switchport').get('Cisco-IOS-XE-switch:access').get('vlan').get('vlan')
        data.append({'mode': 'access','interface': complete_interface, 'vlan': access_vlan, 'status': statistics['oper-status'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn':int(statistics['statistics']['rx-kbps'])/1000})

    elif interface_mode == 'trunk':
        if config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {}):
            trunked_vlans = config.get("switchport", {}).get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {})
            native = config.get("switchport", {}).get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        elif config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
            trunked_vlans = config.get('switchport', {}).get('Cisco-IOS-XE-switch:trunk', {}).get('allowed', {}).get('vlan').get('add')
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        elif config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get('vlans', {}):
            trunked_vlans = config.get('switchport', {}).get('Cisco-IOS-XE-switch:trunk', {}).get('allowed', {}).get('vlan').get('vlans', {})
            native = config.get("switchport", {}).get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        else:
            trunked_vlans = 'all'
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})

        data.append({'mode': 'trunk', 'interface': complete_interface, 'vlans': trunked_vlans, 'native': native, 'status': statistics['oper-status'], 'speed': statistics['speed'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn': int(statistics['statistics']['rx-kbps'])/1000})
    else:
        data.append({'mode': None, 'interface': complete_interface, 'status': statistics['oper-status'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn': int(statistics['statistics']['rx-kbps'])/1000})

    return data

def get_bgp_status(ip, port, username, password) -> list:
    """Gets BGP neighbor statuses IOS-XE\n
        Cisco-IOS-XE-bgp-oper:bgp-state-data/address-families/address-family"""

    bgp_neighbors = []
    bgp_details = []
    bgp_topology = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-bgp-oper:bgp-state-data/address-families/address-family"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        bgp_data = json.loads(response.text)

        check_error = _check_api_error(bgp_data)
        
        if check_error:
            raise AttributeError

        get_keys = dict.fromkeys(bgp_data)
        parent_key = list(get_keys.keys())[0]

        if isinstance (bgp_data[parent_key], list):
            for i in bgp_data[parent_key]:
                
                bgp_details.append(i.get('local-as'))
                bgp_details.append(i.get('vrf-name'))
                bgp_details.append(i.get('router-id'))
                bgp_details.append(i.get('bgp-table-version'))
                bgp_details.append(i.get('routing-table-version'))
                bgp_details.append(i.get('prefixes').get('total-entries'))
                bgp_details.append(i.get('prefixes').get('memory-usage'))
                bgp_details.append(i.get('vrf-name'))
                bgp_details.append(i.get('path').get('total-entries'))
                bgp_details.append(i.get('path').get('memory-usage'))
                bgp_details.append(i.get('as-path').get('total-entries'))
                bgp_details.append(i.get('as-path').get('memory-usage'))
                bgp_details.append(i.get('route-map').get('total-entries'))
                bgp_details.append(i.get('route-map').get('memory-usage'))
                bgp_details.append(i.get('filter-list').get('total-entries'))
                bgp_details.append(i.get('filter-list').get('memory-usage'))
                bgp_details.append(i.get('activities').get('prefixes'))
                bgp_details.append(i.get('activities').get('paths'))
                bgp_details.append(i.get('activities').get('scan-interval'))
                bgp_details.append(i.get('total-memory'))

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, KeyError, AttributeError) as e:
        pass
    
    try:

        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-bgp-oper:bgp-state-data/neighbors"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        bgp_data = json.loads(response.text)

        check_error = _check_api_error(bgp_data)
        
        if check_error:
            raise AttributeError

        for i in bgp_data.get('Cisco-IOS-XE-bgp-oper:neighbors', {}).get('neighbor', {}):

            bgp_topology[i.get('neighbor-id', {})] = i.get('as')

            bgp_neighbors.append({  'remote-as': i.get('as'),
                                    'neighbor-id': i.get('neighbor-id', {}),
                                    'localIp': i.get('transport').get('local-host'), 
                                    'remote-ip': i.get('transport').get('foreign-host', {}),
                                    'local-port': i.get('transport').get('local-port'),
                                    'remote-port': i.get('transport').get('foreign-port'),
                                    'last-reset': i.get('connection').get('last-reset'), 
                                    'state': i.get('connection').get('state'),
                                    'prefixes-sent': i.get('prefix-activity').get('sent').get('current-prefixes'),
                                     'received-prefixes': i.get('prefix-activity').get('received').get('current-prefixes'),
                                     'installed-prefixes': i.get('installed-prefixes', {})})



    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, KeyError, AttributeError) as e:
        pass

    return bgp_neighbors, bgp_details, bgp_topology 

def get_dmvpn_ints(ip, port, username, password) -> tuple:
    """Gets device components /restconf/data/openconfig-platform:components"""

    config_table = []
    interf_op_table = []
    tunnels = []
    hubs = []

    try:
        response = requests.get(f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces", headers=headers, verify=False, auth=(username, password))
        interface_data = json.loads(response.text)

        if _check_api_error(interface_data):
           pass
        else:
            [interf_op_table.append(interface) for interface in interface_data.get('Cisco-IOS-XE-interfaces-oper:interfaces').get('interface') if 'Tunnel' in interface.get('name', {})]

        response = requests.get(f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/interface/Tunnel", headers=headers, verify=False, auth=(username, password))
        config_data = json.loads(response.text)

        if _check_api_error(config_data):
            pass
        else:
            for details in config_data.values():
                if isinstance(details, dict):
                    tunnels.append({
                                 'name': f'Tunnel{detail.get("name", {})}',
                                'mss': detail.get('ip',{}).get("tcp", {}).get('adjust-mss', {}),
                                'mtu': detail.get('ip',{}).get("mtu", {}),
                                'source': detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('source', {}),
                                'mode': f"{list(detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('mode', {}).keys())[0]} {list(list(detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('mode', {}).values())[0].keys())[0]}",
                                'protection': detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('protection', {}).get('Cisco-IOS-XE-crypto:ipsec', {}).get('profile', {}),
                                'authentication': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('authentication', {}),
                                'holdtime': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('holdtime', {}),
                                'netwrok-id': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('map', {}).get('network-id', {})})

                    hubs = _map_dmvpn_hubs(detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('map', {}))

                else:
                    for detail in details:
                        tunnels.append({
                                'name': f'Tunnel{detail.get("name", {})}',
                                'mss': detail.get('ip',{}).get("tcp", {}).get('adjust-mss', {}),
                                'mtu': detail.get('ip',{}).get("mtu", {}),
                                'source': detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('source', {}),
                                'mode': f"{list(detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('mode', {}).keys())[0]} {list(list(detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('mode', {}).values())[0].keys())[0]}",
                                'protection': detail.get('Cisco-IOS-XE-tunnel:tunnel', {}).get('protection', {}).get('Cisco-IOS-XE-crypto:ipsec', {}).get('profile', {}),
                                'authentication': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('authentication', {}),
                                'holdtime': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('holdtime', {}),
                                'network-id': detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('network-id', {})})

                        hubs = _map_dmvpn_hubs(detail.get('ip',{}).get('Cisco-IOS-XE-nhrp:nhrp', {}).get('map', {}))

                
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    return config_table, interf_op_table, tunnels, hubs

def _map_dmvpn_hubs(hub_details) -> list:

    hubs = []

    for i in hub_details.get('dest-ipv4', {}):
    
        if isinstance(i.get('nbma-ipv4', {}), list):
            hubNbma = ", ".join([hub.get('nbma-ipv4', {}) for hub in i.get('nbma-ipv4', {})])
        else:
            hubNbma = i.get('nbma-ipv4', {})

        hubs.append({'tunnel': i.get('dest-ipv4', {}), 'hubNbma': hubNbma})

    return hubs
