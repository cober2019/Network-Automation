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

def get_ospf():

    host = input("IP: ")

    ospf_get = """<filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <router/>
      </native>
    </filter>
    """

    device_connect(host)

    ospf_get_reply = m.get(ospf_get)

    ospf_details = xmltodict.parse(ospf_get_reply.xml)["rpc-reply"]["data"]
    ospf_config = ospf_details["native"]["router"]["ospf"]

    # This block of code checks if ospf_config is a dictionary. If so it will access it as such dict(), if not it will treat it as a list []
    # Why? If one OSPF process exist in the config, xmltodict will convert it to a dictionary, if there is more than one OSPF proccess
    # xmltodict will treat as a list of dictionaries, beging with a list or [dict]

    if isinstance(ospf_config, dict): # check if dictionary

        print("")
        print("OSPF Details:")
        if "id" in ospf_config:
            print("  Process: {}".format(ospf_config["id"]))
        if "router-id" in ospf_config:
            print("  Router ID: {}".format(ospf_config["router-id"]))
        if "default-information" in ospf_config:
            print("  Router ID: {}".format(ospf_config["default-information"]["originate"]["metric-type"]))
        if "network" in ospf_config:
            print("  Network: {}".format(ospf_config["network"]["ip"]))
        if "network" in ospf_config:
            print("  Wildcard: {}".format(ospf_config["network"]["mask"]))
        if "network" in ospf_config:
            print("  Area: {}".format(ospf_config["network"]["area"]))

    else:
        for item in ospf_config: # Iterate through the array of dictionaries
    
            print("")
            print("OSPF Details:")
            if "id" in item:
                print("  Process: {}".format(item["id"]))
            if "router-id" in item:
                print("  Router ID: {}".format(item["router-id"]))
            if "default-information" in item:
                print("  Router ID: {}".format(item["default-information"]["originate"]["metric-type"]))
            if "network" in item:
                print("  Network: {}".format(item["network"]["ip"]))
            if "network" in item:
                print("  Wildcard: {}".format(item["network"]["mask"]))
            if "network" in item:
                print("  Area: {}".format(item["network"]["area"]))

def device_connect(host):

    # NETCONF login

    try:

        global m
        m = manager.connect(host=host, port=830, timeout=3, username="cisco", password="cisco",
                            device_params={'name': 'csr'})

    except ncclient.NCClientError:
        pass
    except AttributeError:
        pass
    except gaierror:
        pass

if __name__ == '__main__':

    get_ospf()
