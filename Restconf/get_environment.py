"""Function that gets device enviromental stats"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}


def get_envirmoment(ip, port, username, password) -> dict:
    """Gets real time enviroment statistics using restconf/data/Cisco-IOS-XE-environment-oper:environment-sensors"""

    data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-environment-oper:environment-sensors"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        data = json.loads(response.text)

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass
    
    if data:
        print("{0:<17}{1:<13}{2:<18}{3:<10}{4:<5}".format('Name', 'Location', 'State', 'Current', 'Measurement'))
        print("-" * 70 )
        for i in test['Cisco-IOS-XE-environment-oper:environment-sensors']['environment-sensor']:
            print("{0:<20}{1:<10}{2:<20}{3:<10}{4:<5}".format(i.get('name'), i.get('location'), i.get('state'), i.get('current-reading'), i.get('sensor-units')))

    return data

if __name__ == '__main__':
    
    try:
        get_envirmoment()
    except TypeError:
        input('Input credentials')
