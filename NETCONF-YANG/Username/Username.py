module_array = [ ]
from os import system, name
try:
    from ncclient import manager
except ImportError:
    print("Module NCC Client not available.")
    module_array.append("ncclient")
try:
    from socket import gaierror
except ImportError:
    print("Module socket not available.")
    module_array.append("gaierror")
try:
    import xmltodict
except ImportError:
    print("Module xmltodict not available.")
    module_array.append("xmltodict")
try:
    import xml.etree.ElementTree as xml
except ImportError:
    print("Module etree not available.")
    module_array.append("etree")
try:
    import lxml.etree as ET
except ImportError:
    print("Module lxml not available.")
    module_array.append("lxml")
try:
    import collections
except ImportError:
    module_array.append("collections")
    pass

netconf_session = " "

def module_check():

    # Check to see if there is any python modules not install. If so you will be notified.

    if not module_array:
        pass
    else:
        print("\n")
        print("{:>75}".format("!!Program will close if all modules below aren't installed!!"))
        print("\n")
        for module in module_array:
            print("{:^84}". format(module))

def get_usernames():

    user_filter = """    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <username/>
      </native>
    </filter>"""

    cred_get_reply = netconf_session.get(user_filter)

    cred_details = xmltodict.parse(cred_get_reply.xml)["rpc-reply"]["data"]
    cred_config = cred_details["native"]["username"]

    # This block of code checks if cred_config is a dictionary. If so it will access it as such dict(), if not it will treat it as a list []
    # Why? If one user name only exist in the config, xmltodict will convert it to a dictionary, if there is more than one username
    # xmltodict will treat as a list of dictionaries, beging with a list or [dict]

    if isinstance(cred_config, dict): # check if dictionary
        print("")
        print("Username Details:")
        if "name" in cred_config:
            print("  Username: {}".format(cred_config["name"]))
        if "privilege" in cred_config:
            print("  Priv: {}".format(cred_config["privilege"]))
        if "encryption" in cred_config:
            print("  Encryption: {}".format(cred_config["password"]["encryption"]))
        if "password" in cred_config:
            print("  Password: {}".format(cred_config["password"]["password"]))
        if "encryption" in cred_config:
            print("  Password: {}".format(cred_config["secret"]["encryption"]))
        if "secret" in cred_config:
            print("  Password: {}".format(cred_config["secret"]["secret"]))
    else:
        for item in cred_config: # Iterate through the array of dictionaries

            print("")
            print("Username Details:")
            if "name" in item:
                print("  Username: {}".format(item["name"]))
            if "privilege" in item:
                print("  Priv: {}".format(item["privilege"]))
            if "encryption" in item:
                print("  Encryption: {}".format(item["password"]["encryption"]))
            if "password" in item:
                print("  Password: {}".format(item["password"]["password"]))
            if "encryption" in item:
                print("  Password: {}".format(item["secret"]["encryption"]))
            if "secret" in item:
                print("  Password: {}".format(item["secret"]["secret"]))

    print("\n")
    main()

def credentials_configuration():

    Cred_Config = "C:\Python\XML_Filters\Credentials_Send_Config.xml"

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    username_element = xml.SubElement(native_element, "username")

    print("New User Configuration")
    print("\n")

    user_input = input("Username: ")
    user_id = xml.SubElement(username_element, "name")
    user_id.text = user_input

    priv_input = input("Privilage Level: ")
    priv_element = xml.SubElement(username_element, "privilege")
    priv_element.text = priv_input

    password_element = xml.SubElement(username_element, "password")

    password_input = input("Password: ")
    pass_element = xml.SubElement(password_element, "password")
    pass_element.text = password_input

    try:
        tree = xml.ElementTree(root) # Writes XML file to share
        with open(Cred_Config, "wb") as save_file:
            tree.write(save_file)
    except FileNotFoundError:
        print("File doesn't exist")
        main()
        pass

    send_single_configuration(Cred_Config)

def delete_credentials():

    Delete_User_Config = "C:\Python\XML_Filters\Credentials_Delete_Config.xml"

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    username_element = xml.SubElement(native_element, "username")
    username_element.set("xc:operation", "remove")

    user = input("User:  ")
    print("\n")

    name_id = xml.SubElement(username_element, "name")
    name_id.set("xc:operation", "remove")
    name_id.text = user

    try:
        tree = xml.ElementTree(root)  # Writes XML file to share
        with open(Delete_User_Config, "wb") as save_file:
            tree.write(save_file)
    except FileNotFoundError:
        print("File doesn't exist")
        main()
        pass

    send_single_configuration(Delete_User_Config)

def send_single_configuration(file):

    try:
        config_file = open(file=file).read()
        send_payload = netconf_session.edit_config(config_file, target="running")
        print("\n")
        save_configuration()
        print("Configuration Complete!")
        print("\n")
        main()

    except ValueError:
        print("Configuration Saved")
        main()
    except AttributeError as error:
        print("Connection Unsucessful")
        pass
    except (UnicodeError):
        print("Invalid IP address. Please try again")
        pass
    except manager.NCClientError:
        print("Please review configuration")
        pass
    except gaierror:
        print("Please review configuration")
        pass

def save_configuration():

    # SAVES RUNNING CONFIG TO STARTUP CONFIG AFTER CONFIGURATION SEND

    save_payload = """
    		<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
            """
    try:
        response = netconf_session.dispatch(ET.fromstring(save_payload))
        print("Configuration Saved")
    except ValueError:
        print("Error")

def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

def device_connect():

        print("\n")
        print("Device Login Credentials\n")
        host = input("IP: ")
        username = input("Username: ")
        password = input("Password: ")

        try:

            global  netconf_session
            netconf_session = manager.connect(host=host, port=830, timeout=3, username=username, password=password,
                                            device_params={'name': 'csr'})

        except manager.NCClientError:
            print("Login Failed")
            device_connect()
            pass
        except AttributeError:
            print("Login Failed")
            pass
        except gaierror:
            print("Login Failed")
            device_connect()
            pass

        return netconf_session

def main():

    clear()
    while True:

        print("\n")
        print("1. Add User")
        print("2. Remove User")
        print("3. View Users")
        print("\n")

        config_selection = input("Selection:  ")
        print("\n")

        if config_selection == "1":
            credentials_configuration()
        elif config_selection == "2":
            delete_credentials()
        elif config_selection == "3":
            get_usernames()
        else:
            print("\n")
            print("Invalid selection")
            print("\n")

if __name__ == '__main__':

    module_check()
    netconf_session = device_connect()
    main()


