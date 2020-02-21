try:
    from ncclient import manager
except ImportError:
    print("Module NCC Client not available.")
try:
    import ncclient
except ImportError:
    print("Module NCC Client not available.")
try:
    from socket import gaierror
except ImportError:
    print("Module socket not available.")

try:
    import xmltodict
except ImportError:
    print("Module xmltodict not available.")

def get_usernames():

    user_filter = """    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <username/>
      </native>
    </filter>"""

    host = input("IP: ")

    device_connect(host)
    cred_get_reply = m.get(user_filter)

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

def device_connect(host):

        # NETCONF login

        try:

            global m
            m = manager.connect(host=host, port=830, timeout=3, username="cisco", password="cisco",
                                            device_params={'name': 'csr'})

        except ncclient.NCClientError:
            global_status = status_2
            pass
        except AttributeError:
            global_status = status_2
            pass
        except gaierror:
            global_status = status_2
            db_conn.start()
            pass


if __name__ == '__main__':

    get_usernames()


