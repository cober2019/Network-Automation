"""Function for getting CPU data from a device"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}


def get_cpu_usages(ip, port, username, password, show_proccess=False) -> tuple:
    """Gets real time CPU statistics using restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage"""

    cpu_stats = {}
    memory_stats = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        cpu_stats = json.loads(response.text)
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes/control-process"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        converted_json = json.loads(response.text)
        get_keys = dict.fromkeys(converted_json)
        parent_key = list(get_keys.keys())[0]
        memory_stats = converted_json[parent_key]
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass
    
    if cpu_stats:
        print("{0:<15}{1:<15}\n{2:<15}{3:<16}\n{4:<15}{5:<5}".format('Five Seconds:', cpu_stats['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['five-seconds'],
                                                                 'One Minute:',cpu_stats['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['one-minute'],
                                                                 'Five Minutes:', cpu_stats['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['five-minutes']))
        if show_proccess:
            print("{0:<5}{1:<55}{2:<20}{3:<10}{4:<10}{5:<10}{6:<10}".format('PID', 'Name', 'TTY', 'Avg-Run', 'Five Sec.', 'One Min.', 'Five Min.'))
            print('-' * 130)
            for i in cpu_stats['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['cpu-usage-processes']['cpu-usage-process']:
                print("{0:<5}{1:<55}{2:<20}{3:<10}{4:<10}{5:<10}{6:<10}".format(i.get('pid'), i.get('name'), i.get('tty'), i.get('avg-run-time'), 
                                                                            i.get('five-seconds'), i.get('one-minute'), i.get('five-minutes')))
    return cpu_stats, memory_stats

if __name__ == '__main__':
    
    try:
        get_dp_neighbors()
    except TypeError:
        input('Input credentials')
