"""Simple script that checks for global BGP prefixes in the public internet and notifies via Email"""

from paramiko.ssh_exception import PasswordRequiredException
from netmiko import ConnectHandler, ssh_exception
from ntc_templates.parse import parse_output
from datetime import date
import concurrent.futures
import smtplib, ssl
import requests

SMTP_SERVER = ""
SMTP_SEVER_USERNAME = ''
SMTP_SERVER_PASSWORD = ''
FROM_EMAIL = ''
TO_EMAIL = ''
YOUR_PUBLIC_PREFIXES = []

def _send_command(command, hostname, username, password,  device_type) -> list:
    """Logs into device and returns a reponse to the caller """
    
    response = 'not found'
    
    #Match router server auth/no auth
    if username is None and password is None:
        credentials = {
            'device_type': device_type,
            'host': hostname,
            'port': 23,
            'session_log': 'my_file.out'}
    elif password is None:
        credentials = {
            'device_type': device_type,
            'host': hostname,
            'username': username,
            'port': 23,
            'session_log': 'my_file.out'}
    else:
         credentials = {
            'device_type': device_type,
            'host': hostname,
            'username': username,
            'password': password,
            'port': 23,
            'session_log': 'my_file.out'}

    try:
        with ConnectHandler(**credentials) as connection:
            response = connection.send_command(command)
    except (ssh_exception.AuthenticationException, EOFError, ssh_exception.NetmikoTimeoutException, PasswordRequiredException):
        pass
    finally:
        return response

def _asn_lookup(asn:str):
    """Queries ARIN for  ASN lookup"""
    
    response = ''
    
    try:  
          
        request = requests.get(f" https://whois.arin.net/rest/asn/AS{asn}", headers={"Content-Type": 'text/plain', 'Accept': 'text/plain'})
        
        #ARIN doesnt return response codes. If not found, return text/html, else return text/plain
        if request.text.splitlines()[0].startswith('<!DOCTYPE'):
            response = f'\nASN {asn} not found in the ARIN registery'
        else:
            response = 'ASNumber: ' + request.text.split('ASNumber')[1].split('ARIN')[0]
            
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        pass
    finally:
        return response

def send_email(results:str) -> None:
    """Send email use SMTP credentials"""

    with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=ssl.create_default_context()) as server:
        
        try:
            message = 'Subject: {}\n\n{}'.format('ASN Check', results)
            server.login(SMTP_SEVER_USERNAME, SMTP_SERVER_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, message)
        except smtplib.SMTPException:
            pass
    
def check_global_prefixes_cli(hostname:str, username:str, password:str, device_type:str) -> list:
    """Connects to router server and searches for public prefix"""
    
    matching_prefixes = []

    for subnet in YOUR_PUBLIC_PREFIXES:
        
        get_prefix = _send_command(command=f"show ip bgp {subnet} bestpath", hostname=hostname, username=username, password=password, device_type=device_type)
        
        if len(get_prefix.split(' ')) > 10 or get_prefix == 'not found':
            
            output = ''
            as_path =''
            prefix_detail = get_prefix.splitlines()
            
            for index, line in enumerate(prefix_detail):
                try:
                    if 'Not advertised to any peer' not in line and 'BGP Bestpath' not in line:
                        output += line + '\n'
                    if 'Refresh' in prefix_detail[index - 1]:
                        as_path += line
                except IndexError:
                    pass
                
                data = _asn_lookup(as_path.split(' ')[-1]).replace('#', '')

            matching_prefixes.append({'hostname': hostname, 'subnet': subnet, 'result': output, 'as': as_path, 'arin_info': data})
                
    return matching_prefixes
    
if __name__ == '__main__':

    route_servers = [{'device_type': 'cisco_ios_telnet', 'hostname': 'route-views.routeviews.org', 'username': "rviews", 'password': None},
                     {'device_type': 'cisco_ios_telnet', 'hostname': 'public-route-server.is.co.za', 'username': 'rviews', 'password': 'rviews'},
                     {'device_type': 'cisco_ios_telnet', 'hostname': 'route-server.ip-plus.net', 'username': None, 'password': None},
                     {'device_type': 'cisco_ios_telnet', 'hostname': 'lg.sp.ptt.br', 'username': None, 'password': None}]
    
    #Creates thread for faster proccessing
    results = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        get_data = {executor.submit(check_global_prefixes_cli, server['hostname'], server['username'], server['password'], server['device_type']) for server in route_servers}
        for future in concurrent.futures.as_completed(get_data):
            try:
                results.append(future.result())
            except Exception:
                pass

    messages = []
    seperator = '-' * 40
    
    for i in results:
      for result in i:
        messages.append(f'''\n\nSource Table: {result['hostname']}\n\n{result['result']}\n\n{result['arin_info']}\n{seperator}''')
    
    if messages:
        send_email('\n'.join(messages))
