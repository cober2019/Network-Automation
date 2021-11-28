from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import os
import json
import requests
import devicecalls as GetThisDataFromDevice
import device_call_backup as InCaseRestDoesntWork
import GetRibData as GetRibs


headers_ios = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}
#ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#ctx.load_cert_chain(f'{os.getcwd()}/domainame.crt', f'{os.getcwd()}/domainame.key')


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

rib_session = {}

def parse_config(config, parent_key):
    """Collect config and all keys for next config options"""

    leafs = []
    data = []

    if isinstance(config[parent_key], list):
        lists = [k for k in config[parent_key]]
        leafs = [leaf for leaf in lists[0].keys()]
        data = [i.get(leafs[0]) for i in lists]
    elif isinstance(config[parent_key], dict):
        data = [k for k in config[parent_key].keys()]

    return data, leafs

@app.route('/token', methods=['POST', 'GET'])
def token() -> dict:
    token = create_access_token(identity=request.json.get('username'))
    return jsonify(token)

@app.route('/login', methods=['POST', 'GET'])
def ios_xe_login() -> dict:
    """Authenticates credentials to device. Check device capabilities"""

    global rib_session
    
    # Reset our rib status object
    auth_dict = {'status': 'null'}
    print(request.json)

    try:
        response = requests.get(f"https://{request.json.get('ip', {})}:{request.json.get('port', {})}/restconf/data/netconf-state/capabilities",
            headers=headers_ios, verify=False, auth=(request.json.get('username', {}), request.json.get('password', {})))
        print(response.status_code)
        if response.status_code == 200:
            model_serial = InCaseRestDoesntWork.get_model(request.json.get('username'), request.json.get('password'), request.json.get('ip'))
            auth_dict['status'] = 200
            auth_dict['model'] = model_serial[0]
            auth_dict['serial'] = model_serial[1]
            auth_dict['uptime'] = model_serial[2]
            auth_dict['software'] = model_serial[3]
            rib_session_obj = GetRibs.Routing()
            rib_session[request.json.get('ip')] = {'username': request.json.get('username'), 
                                                        'password':request.json.get('password'), 
                                                        'port': 443, 
                                                        'session':rib_session_obj}
        elif response.status_code == 400:
            auth_dict['status'] = 400
        elif response.status_code == 401:
            auth_dict['status'] = 401
        elif response.status_code == 404:
            auth_dict['status'] = 404
        elif response.status_code == 204:
            auth_dict['status'] = 204
        elif response.status_code == 500:
            auth_dict['status'] = 500

    except (json.decoder.JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, UnboundLocalError):
        auth_dict['status'] = 500

    return auth_dict


@app.route('/pollIndexPage', methods=['POST', 'GET'])
def index_page() -> dict:
    """Get data for Index page , interfaces, dp neighbors, arps, and hsrp"""

    interfaces = GetThisDataFromDevice.get_interfaces(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    neighbors = GetThisDataFromDevice.get_dp_neighbors(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    arps = GetThisDataFromDevice.get_arps(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    hsrp = InCaseRestDoesntWork.get_hsrp_status(request.json.get('username'), request.json.get('password'), request.json.get('ip'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))


    return {'interfaces': interfaces, 'arps': arps, 'dp': neighbors, 'hsrp': hsrp, 'cpu': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/pollEnv', methods=['POST', 'GET'])
def environment_page() -> dict:
    """Get data for environment page. CPU and memory"""

    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    env_status = GetThisDataFromDevice.get_envirmoment(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    poe_status = GetThisDataFromDevice.get_poe(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    transceivers = GetThisDataFromDevice.get_sfps(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'cpu': cpu_status[0], 'env': env_status, 'mem': cpu_status[1], 'poe': poe_status, 'transceivers': transceivers, 'mem': cpu_status[1]}

@app.route('/pollL2Page', methods=['POST', 'GET'])
def layer_2__page() -> dict:
    """Get daya for layer two page. inerfaces, vlans, dp neighbors, macs, span-tree"""

    interfaces = GetThisDataFromDevice.get_switch(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    vlans = GetThisDataFromDevice.get_vlans(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    neighbors = GetThisDataFromDevice.get_dp_neighbors(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    mac_addresses = GetThisDataFromDevice.get_bridge(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    span_table = GetThisDataFromDevice.get_span_tree(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'trunks': interfaces[0], 'access': interfaces[1], 'dpNeighbors': neighbors, 'vlans': vlans, 'mac_addresses': mac_addresses, 'span': span_table[0], 
            'globalSpan': span_table[1], 'cpu': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/pollRouting', methods=['POST', 'GET'])
def routing_page() -> dict:
    """Get data for routing page. OSPF, and BGP"""

    ospf = GetThisDataFromDevice.get_ospf(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    bgp = GetThisDataFromDevice.get_bgp_status(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    prefix_lists = GetThisDataFromDevice.get_prefix_list(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    route_maps = GetThisDataFromDevice.get_route_maps(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'ospf': ospf[0], 'ospfInts': ospf[1], 'bgp': bgp[0], 'bgpDetails': bgp[1], 'bgpTopology': bgp[2], 'ospfTopology': ospf[2], 'cpu': cpu_status[0], 'mem': cpu_status[1], 
            'prefixLists': prefix_lists, 'routeMaps': route_maps}

@app.route('/getDmvpn', methods=['POST', 'GET'])
def dmvpn() -> dict:
    """Gets DMVPN topology information. HUB/Spoke, interfaces, tunnel interfaces, topology info"""

    dmvpn = InCaseRestDoesntWork.get_dmvpn( request.json.get('username'), request.json.get('password'), request.json.get('ip'))
    dmvpn_ints  = GetThisDataFromDevice.get_dmvpn_ints(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    ospf = GetThisDataFromDevice.get_ospf(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'dmvpn': dmvpn[0], 'dmvpnInts': dmvpn_ints, 'hubs': dmvpn_ints[3], 'location': dmvpn[1], 'ospfInts': ospf[1], 'ospfTopology': ospf[2], 'ospf': ospf[0], 
            'cpu': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/getipsla', methods=['POST', 'GET'])
def ipslas() -> dict:
    """Gets IP SLA data from device"""

    sla_stats = GetThisDataFromDevice.get_ip_sla(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'slas': sla_stats, 'cpu': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/policies', methods=['POST', 'GET'])
def policies() -> dict:
    """Gets policy based configurations. i.e. route-maps, acls, prefix-lists"""

    prefix_lists = GetThisDataFromDevice.get_prefix_list(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    route_maps = GetThisDataFromDevice.get_route_maps(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'prefixLists': prefix_lists, 'routeMaps': route_maps}

@app.route('/ribStatus', methods=['POST', 'GET'])
def rib_status():
    """Get rib and flapping routes"""

    global rib_session

    routing_information =[[],[],[]]
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    try:
        routing_information = rib_session.get(request.json.get('ip')).get('session').get_routing_info(
                                                                request.json.get('ip'),443,
                                                                request.json.get('username'),
                                                                request.json.get('password'))
    except (TypeError, AttributeError):
        pass

    return {'ribsEntries': routing_information[1], 'protocols': routing_information[0], 'flaps': routing_information[2], 'cpu': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/liveinterfaces', methods=['POST', 'GET'])
def live_interfaces():
    """Get device interfaces"""

    interfaces = GetThisDataFromDevice.get_interfaces(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))
    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'interfaces': interfaces, 'cpu': cpu_status[0], 'mem': cpu_status[1]}


@app.route('/modifyconfig', methods=['POST', 'GET'])
def modify_interface():
    """Send new configuration options to Ansible"""

    config_status = 'Failed'

    if request.json.get('data').get('type') == 'interface':
        print(request.json.get('data', {}))
    elif request.json.get('data').get('type') == 'bgp':
        print(request.json.get('data', {}))

    return {'data': config_status}


@app.route('/cpustatus', methods=['POST', 'GET'])
def get_cpu_status():
    """Get CPU status"""

    cpu_status = GetThisDataFromDevice.get_cpu_usages(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': cpu_status[0], 'mem': cpu_status[1]}

@app.route('/hardwarestatus', methods=['POST', 'GET'])
def get_hardware_status():
    """Get hardware status"""

    cpu_status = GetThisDataFromDevice.get_hardware_status(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': cpu_status}

@app.route('/getenvirmoment', methods=['POST', 'GET'])
def get_environment():
    """Get environmntal status"""

    env_status = GetThisDataFromDevice.get_envirmoment(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': env_status}

@app.route('/getcomponents', methods=['POST', 'GET'])
def get_components():
    """Get device sompenent status"""

    components = GetThisDataFromDevice.get_components(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': components}

@app.route('/neighbors', methods=['POST', 'GET'])
def get_dp_neigh():
    """Gey DP neighbors"""

    neighbors = GetThisDataFromDevice.get_dp_neighbors(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': neighbors}


@app.route('/vlans', methods=['POST', 'GET'])
def get_vlans():
    """Get Vlans"""

    vlans = GetThisDataFromDevice.get_vlans(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': vlans}

@app.route('/layertwointerfaces', methods=['POST', 'GET'])
def get_layertwo_interfaces():
    """Get switching interfaces"""

    interfaces = GetThisDataFromDevice.get_switch(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'trunks': interfaces[0], 'access': interfaces[1]}

@app.route('/bgpstatus', methods=['POST', 'GET'])
def get_bgp_status():
    """Get BGP statuses"""

    cpu_status = GetThisDataFromDevice.get_bgp_status(request.json.get('ip'), request.json.get('port'), request.json.get('username'), request.json.get('password'))

    return {'data': cpu_status}

@app.route('/apistatus', methods=['POST', 'GET'])
def get_api_status():
    """Get API status"""

    return "<h4>API Is Up</h4>"

@app.route('/query', methods=['POST', 'GET'])
def device_query() -> dict:
    """Querys device for yang model. Return data, keys for next query"""

    response_dict = {}
    print(request.json)

    response = requests.get(request.json.get('url'), 
                            headers=headers_ios, verify=False,
                            auth=(request.json.get('username'),
                            request.json.get('password')))
    print(response.text)
    if response.status_code == 200:
        try:
            converted_json = json.loads(response.text, strict=False)
            get_keys = dict.fromkeys(converted_json)
            parent_key = list(get_keys.keys())[0]
            config = parse_config(converted_json, parent_key)
            response_dict['status'] = 200
            response_dict['data'] = config[0]
            response_dict['leafs'] = config[1]
            response_dict['parent'] = list(get_keys.keys())[0]
            response_dict['config'] = response.text
        except json.decoder.JSONDecodeError:
            response_dict['status'] = 500
    else:
        response_dict['status'] = response.status_code

    return response_dict

if __name__ == '__main__':
    app.run()
