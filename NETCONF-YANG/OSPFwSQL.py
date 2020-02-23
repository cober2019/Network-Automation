
try:
    import sqlite3
except ImportError:
    print("Module SQLITE3 not available.")
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
try:
    import xml.etree.ElementTree as xml
except ImportError:
    print("Module xml not available.")
try:
    import lxml.etree as ET
except ImportError:
    print("Module lxml not available.")
try:
    from datetime import date
except ImportError:
    print("Module time not available.")
try:
    import time
except ImportError:
    print("Module time not available.")

mydb = sqlite3.connect("Automation")
c = mydb.cursor()
d = mydb.cursor()
status_1 = "Pass"
status_2 = "Fail"
job_1 = "Send"
job_2 = "View"
global_status = " "
filename = "C:\Python\OSPF_Config.xml"
not_app = " N/A"

def main():

    print("\n")
    print("1. OSPF Configuration")
    print("2. View OSPF")
    print("3. Device Status")
    print("\n")

    selection = input("Selection: ")
    print("\n")

    if selection == "1":
        db_check()
        ospf_send()
    elif selection == "2":
        db_check()
        get_ospf()
    elif selection == "3":
        db_check()
        view_database()
        main()
    else:
        main()

def cleanup_empty_elements(root_var, file):

    # Cleans up empty elements in the tree. This help when you ask a user for an input and they just hit enter.
    # In XML it looks like this <id><id> (id is an example.) If this is senf to a device you will receive an
    # RPC error. So it saves, cleans it up, and saves it again.

    try:
        tree = xml.ElementTree(element=root_var)
        tree.write(file_or_filename=file)

        root = ET.fromstring(open(file=file).read())
        for element in root.xpath("//*[not(node())]"):
            element.getparent().remove(element)

        tree = xml.ElementTree(element=root)
        tree.write(file_or_filename=file)

    except FileNotFoundError:
        pass

def ospf_send():

        host = input("IP: ")
        print("\n")

        root = xml.Element("config")
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        native_element = xml.Element("native")
        native_element.set("xmlns:ios-ospf", "http://cisco.com/ns/yang/Cisco-IOS-XE-ospf")
        native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        root.append(native_element)
        router_element = xml.SubElement(native_element, "router")
        ospf_element = xml.SubElement(router_element, "ios-ospf:ospf")

        print("\n")
        print("OSPF Configuration:")
        print("\n")

        process_input = input("OSPF Process: ")
        process_id = xml.SubElement(ospf_element, "ios-ospf:id")
        process_id.text = process_input

        rid_input = input("Router ID: ")
        rid_id = xml.SubElement(ospf_element, "ios-ospf:router-id")
        rid_id.text = rid_input

        network_leaf = xml.SubElement(ospf_element, "ios-ospf:network")

        network_input = input("Network ID: ")
        network_id = xml.SubElement(network_leaf, "ios-ospf:ip")
        network_id.text = network_input

        mask_input = input("Wildcard: ")
        mask = xml.SubElement(network_leaf, "ios-ospf:mask")
        mask.text = mask_input

        area_input = input("Area: ")
        area_id = xml.SubElement(network_leaf, "ios-ospf:area")
        area_id.text = area_input

        cleanup_empty_elements(root, filename)

        device_connect(host, job_1)
        db_update(host, status_1, status_1, job_1, filename)
        view_database()
        main()

def get_ospf():

    host = input("IP: ")
    print("\n")

    ospf_get = """<filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <router/>
      </native>
    </filter>
    """

    device_connect(host, job_2)

    try:
        ospf_get_reply = m.get(ospf_get)
        ospf_details = xmltodict.parse(ospf_get_reply.xml)["rpc-reply"]["data"]
    except NameError:
        main()
        pass

    try:
        ospf_config = ospf_details["native"]["router"]["ospf"]
    except TypeError:
        print("\n")
        print("OSPF not configured")
        main()
        pass

    # This block of code checks if ospf_config is a dictionary. If so it will access it as such dict(), if not it will treat it as a list []
    # Why? If one OSPF process exist in the config, xmltodict will convert it to a dictionary, if there is more than one OSPF proccess
    # xmltodict will treat as a list of dictionaries, beging with a list or [dict]

    try:
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

    except UnboundLocalError:
        pass

    db_update(host, status_1, status_1, job_2, not_app )
    print("\n")
    main()

def device_connect(host, job):

    # NETCONF login
    # db_update function updates the DB entry based on pass/fail
    # global status variable keeps track of device connectivty, later used in get_capabilties function.
    # If status is "fail" program won't check for capabilities

    global global_status
    try:

        global m
        m = manager.connect(host=host, port=830, timeout=3, username="cisco", password="cisco",
                            device_params={'name': 'csr'})

        ospf_config = open(filename).read()
        send_payload = m.edit_config(ospf_config, target="running")

    except ncclient.NCClientError:
        db_update(host, status_2, status_2, job, not_app)
        main()
        pass
    except AttributeError:
        db_update(host, status_2, status_2, job, not_app)
        main()
        pass
    except gaierror:
        db_update(host, status_2, status_2, job, not_app)
        main()
        pass

def db_update(host, status1, status2, job, filename):

    # With sql functions included in the program, this will add an entry if not there. I will then use the
    # cleanup() function to remove any duplicate entries

    d.execute("INSERT INTO Automation VALUES ('%s','%s','%s', '%s', '%s', '%s', '%s')" %
              (host, status1, status2, job, filename, date.today(), time.strftime("%H:%M:%S ")))

    mydb.commit()
    cleanup_db()

def cleanup_db():

    # Cleanup any duplicate DB entries, keeping the most current (max)

    try:
        for row in c.execute('SELECT * FROM Automation'): # Cleanup any database duplicates
                c.execute('DELETE FROM Automation WHERE rowid not in (SELECT max(rowid) FROM Automation GROUP BY Device)')
                mydb.commit()
    except sqlite3.OperationalError:
        pass

def headers():

    # Any time database is viewed, filtered or unfiltered these headings will show

    print("\n")
    print("{:>14} {:>18} {:>17} {:>15} {:>15} {:>18} ".format
          ("IP",  "Conn Status", "Job Status", "Job Type", "Date", "Time"))
    print("__________________________________________________________________________________________________________")
    print("\n")

def view_database():

    #  Iterate through the rows in the current DB and print our the entries. As you can see, iterating
    # through the DB is like and array/lost. Index them as usual

    try:
        headers()
        for row in c.execute('SELECT * FROM Automation'):
            print("{:>0} {:>15} {:>11} {:>17} {:>15} {:>20} {:>20} ".format("  ",
                                row[0], row[1], row[2], row[3], row[5], row[6]))
        print("\n")

    except sqlite3.OperationalError:
        print("\n")
        print("Database Doesn't Exist")
        db_check()
        print("\n")
        pass

def db_check():

    # Check to see if there is an existing DB. If not, a db is created. This will be created in the .py folder.

    try:
        c.execute('''CREATE TABLE Automation (Device, Status1, Status2, JobType, File, DateTime, Time)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

if __name__ == '__main__':

    main()