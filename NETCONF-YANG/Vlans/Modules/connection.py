"""NCClient connection funtion"""

from ncclient import manager
import logging
import socket
from Modules import main_funtions
from ncclient.operations import RPCError
import lxml.etree as ET
import xml.etree.cElementTree as xml
from Modules import config_build
from netmiko import ConnectHandler, ssh_exception
logging.basicConfig(filename='Logging/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def netmiko_login(username, password, host) -> object:
    """Logs into device and returns a connection object to the caller. """

    credentials = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'session_log': 'my_file.out'}

    try:
        device_connect = ConnectHandler(**credentials)
    except ssh_exception.AuthenticationException:
        raise ConnectionError(f"Could not connect to device {host}")
        main_funtions.main()
    except OSError:
        raise ConnectionError(f"Could not connect to device {host}")
        main_funtions.main()

    return device_connect


def create_netconf_connection(username, password, host) -> manager:
    """Creates device connection"""

    try:

        netconf_session = manager.connect(host=host, port=830, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})

        logging.exception(f"User {username} logged into {host}. Session: {netconf_session.session_id}")

    except manager.operations.errors.TimeoutExpiredError as error:
        logging.exception(f"Connection to {host} failed", exc_info=True)
        print(f"Connection to {self._host} failed")
        main_funtions.main()
    except manager.transport.AuthenticationError as error:
        logging.exception(f"Invalid Credentials", exc_info=True)
        print("Invalid Credentials")
        main_funtions.login()
    except socket.gaierror as error:
        logging.exception(f"Invalid IPs", exc_info=True)
        print("Invalid IP")
        main_funtions.main()
    except manager.operations.TimeoutExpiredError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SSHError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SessionCloseError:
        logging.exception(f"Session Error, Session Has Been Closed", exc_info=True)
        print("Session Error, Session Has Been Closed")
        main_funtions.main()

    return netconf_session


def save_running_config(netconf_session) -> None:
    """Save new configuration to running config"""

    save_payload = """
                       <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                       """
    try:
        response = netconf_session.dispatch(ET.fromstring(save_payload)).xml
    except RPCError as error:
        logging.exception("Config not saved: An error has occured, please try again!", exc_info=True)
        print("\nAn error has occured, pleqase try again!")


def send_configuration(config, netconf_session, build_object, db_ops, op_type=None, op_cat=None) -> None:
    """Send configuration via NETCONF"""


    try:
        netconf_session.edit_config(config, target="running")
        main_funtions.database_write(op_type, op_cat)
        build_object.get_netmiko_vlans(db_ops)

    except manager.operations.errors.TimeoutExpiredError as error:
        logging.exception(f"Connection to {host} failed", exc_info=True)
        print(f"Connection to {self._host} failed")
        main_funtions.main()
    except manager.transport.AuthenticationError as error:
        logging.exception(f"Invalid Credentials", exc_info=True)
        print("Invalid Credentials")
        main_funtions.login()
    except socket.gaierror as error:
        logging.exception(f"Invalid IPs", exc_info=True)
        print("Invalid IP")
        main_funtions.main()
    except manager.operations.TimeoutExpiredError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SSHError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SessionCloseError:
        logging.exception(f"Session Error, Session Has Been Closed", exc_info=True)
        print("Session Error, Session Has Been Closed")
        main_funtions.main()

    main_funtions.clear_object_attributes()
    main_funtions.main()

def send_configuration_lite(config, netconf_session) -> None:
    """Send configuration via NETCONF"""

    xmlstr = xml.tostring(config, method='xml')
    converted_config = xmlstr.decode('utf-8')

    try:
        netconf_session.edit_config(converted_config, target="running")
        save_running_config(netconf_session)

    except manager.operations.errors.TimeoutExpiredError as error:
        logging.exception(f"Connection to {host} failed", exc_info=True)
        print(f"Connection to {self._host} failed")
        main_funtions.main()
    except manager.transport.AuthenticationError as error:
        logging.exception(f"Invalid Credentials", exc_info=True)
        print("Invalid Credentials")
        main_funtions.login()
    except socket.gaierror as error:
        logging.exception(f"Invalid IPs", exc_info=True)
        print("Invalid IP")
        main_funtions.main()
    except manager.operations.TimeoutExpiredError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SSHError as error:
        logging.exception(f"Connection Timeout", exc_info=True)
        print("Connection Timeout")
        main_funtions.main()
    except manager.transport.errors.SessionCloseError:
        logging.exception(f"Session Error, Session Has Been Closed", exc_info=True)
        print("Session Error, Session Has Been Closed")
        main_funtions.main()

    main_funtions.clear_object_attributes()
