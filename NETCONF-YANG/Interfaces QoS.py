module_array = [ ]

try:
    import sqlite3
except ImportError:
    module_array.append("sqllite3")
    print("Module SQLITE3 not available.")
try:
    from ncclient import manager
except ImportError:
    module_array.append("ncclient")
    print("Module NCC Client not available.")
try:
    import ncclient
except ImportError:
    module_array.append("ncclient")
    print("Module NCC Client not available.")
try:
    from socket import gaierror
except ImportError:
    module_array.append("socket")
    print("Module socket not available.")
try:
    import xmltodict
except ImportError:
    module_array.append("xmltodict")
    print("Module xmltodict not available.")
try:
    import lxml.etree as ET
except ImportError:
    module_array.append("lxml.etree")
    print("Module lxml not available.")
try:
    import datetime
except ImportError:
    module_array.append("datetime")
    print("Module datetime not available.")
try:
    import time
except ImportError:
    module_array.append("time")
    print("Module time not available.")
try:
    import calendar
except ImportError:
    module_array.append("calendar")
    print("Module time not available.")


mydb = sqlite3.connect("Automation")
c = mydb.cursor()
d = mydb.cursor()
e = mydb.cursor()
f = mydb.cursor()
g = mydb.cursor()
h = mydb.cursor()

int_array = []
int_2_array = []
total_seconds = " "
timestamp_diff = " "
poll_time = int(10)
place_holder = "---"
total_seconds = " "
poll_date = " "

def module_check():

    # Check to see if there is any python modules not install. If so you will be notified.

    if not module_array:
        main()
    else:
        print("\n")
        print("{:>75}".format("!!Program will close if all modules below aren't installed!!"))
        print("\n")
        for module in module_array:
            print("{:^84}". format(module))
        main()

def main():

    print("\n")
    while True:

        print("Interface Viewer")
        print("\n")
        print("1. Collect Interface Stats") # Collect new data
        print("2. View Current Database ") # Data from last poll
        print("\n")
        selection = input("Selection: ")
        print("\n")

        if selection == "1":

            host = input("IP: ")
            del_entry(host)
            del_entry_diff(host)
            device_connect(host)
            interfaces(host)
            main()
            break

        elif selection == "2":

            host = input("IP: ")
            view_qos_stats(host)
            main()
            break

        else:
            print("\n")
            print("Invalid Selection")
            print("\n")

def interfaces(host):

    perc_in_diff = "N/A"
    perc_out_diff = "N/A"
    global int_array
    global int_2_array
    int_array = []
    int_2_array = []

    get_int ="""<filter>
                <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface/>
                </native>
                </filter>"""


    # Collect all interfaces from the device. If the device doesnt have a particular interface type then it will pass
    # the Keyerror exception. We will use these variables later to access the interface dictionary in the next block
    # of code. The is block is line 111 - 141

    intf_info = m.get(get_int)
    intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]

    try:
        intf_config_tree_1 = intf_dict["native"]["interface"]["GigabitEthernet"]
    except KeyError:
        pass
    try:
        intf_config_tree_2 = intf_dict["native"]["interface"]["Loopback"]
    except KeyError:
        pass
    try:
        intf_config_tree_3 = intf_dict["native"]["interface"]["Tunnel"]
    except KeyError:
        pass
    try:
        intf_config_tree_4 = intf_dict["native"]["interface"]["Vlan"]
    except KeyError:
        pass
    try:
        intf_config_tree_5 = intf_dict["native"]["interface"]["Port-channel"]
    except KeyError:
        pass
    try:
        intf_config_tree_6 = intf_dict["native"]["interface"]["TenGigabitEthernet"]
    except KeyError:
        pass
    try:
        intf_config_tree_7 = intf_dict["native"]["interface"]["Port-channel-subinterface"]
    except KeyError:
        pass

    # Break down interface names for later use. Why? This is so we dont need static filters (interface numbers/names)
    # Place all interface number into an array. Check to see if there is multiple interfaces which would convert
    # to an array, or single interface which would convert to a dictionary. We will pass the Unboundlocal exception
    # if the device doesnt have the interface type, or hit an exception in line 111-142. This block of code is lines 144 - 259

    try:
        if isinstance(intf_config_tree_1, dict):
            if "name" in intf_config_tree_1:
                int_2_array.append("GigabitEthernet")
                int_array.append(intf_config_tree_1["name"])
        else:
            try:
                for item in intf_config_tree_1:
                    int_2_array.append("GigabitEthernet")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_2, dict):
            if "name" in intf_config_tree_2:
                int_2_array.append("Loopback")
                int_array.append(intf_config_tree_2["name"])

        else:

            try:
                for item in intf_config_tree_2:
                    int_2_array.append("Loopback")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_3, dict):

            if "name" in intf_config_tree_3:
                int_2_array.append("Tunnel")
                int_array.append(intf_config_tree_3["name"])
        else:

            try:
                for item in intf_config_tree_3:
                    int_2_array.append("Tunnel")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_4, dict):

            if "name" in intf_config_tree_3:
                int_2_array.append("Vlan")
                int_array.append(intf_config_tree_4["name"])
        else:

            try:
                for item in intf_config_tree_4:
                    int_2_array.append("Vlan")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_5, dict):

            if "name" in intf_config_tree_5:
                int_2_array.append("Port-channel")
                int_array.append(intf_config_tree_5["name"])
        else:

            try:
                for item in intf_config_tree_5:
                    int_2_array.append("Port-channel")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_6, dict):

            if "name" in intf_config_tree_6:
                int_2_array.append("TenGigabitEthernet")
                int_array.append(intf_config_tree_6["name"])
        else:

            try:
                for item in intf_config_tree_6:
                    int_2_array.append("TenGigabitEthernet")
                    int_array.append(item["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass

    try:
        if isinstance(intf_config_tree_7, dict):

            if "Port-channel" in intf_config_tree_7:
                int_2_array.append("Port-channel")
                int_array.append(intf_config_tree_7["Port-channel"]["name"])
        else:

            try:
                for item in intf_config_tree_7:
                    int_2_array.append("Port-channel")
                    int_array.append(item["Port-channel"]["name"])
            except UnboundLocalError:
                pass
    except UnboundLocalError:
        pass


    # Loop through the array(s) created above and put the entries into the int stats variable. This will allow us to loop through
    # all interface an get qos statistics.

    print("\n")
    print("#######################################")
    print("{:<0}".format(" Estimated Runime: %s ") % len(int_2_array * poll_time))
    print("#######################################")

    for name, num in zip(int_array, int_2_array):

        global  interface
        interface = num + name
        int_stats = """<filter>
                    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                    <name>%s</name>
                    </interface>
                    </interfaces-state>
                    </filter>""" % interface

        try:
            timestamp_1 = datetime.datetime.now().timestamp()  # Get time of the first stats poll = cont line 290
            intf_state_reply = m.get(int_stats)
            intf_status = xmltodict.parse(intf_state_reply.xml)["rpc-reply"]["data"]
            intf_info_tree = intf_status["interfaces-state"]["interface"]
            int_speed = int(int(intf_info_tree["speed"]))

            index = 0
            timestamp_1 = datetime.datetime.now().timestamp()  # Get time of the first stats poll = cont line 290

            # Iterate through the interface queues and collect statistics

            for i in range(0,len(int_2_array)):

                try:

                    policy_direction = (intf_info_tree["diffserv-target-entry"]["direction"])
                    policy_name = (intf_info_tree["diffserv-target-entry"]["policy-name"])
                    class_name = (intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-name"])
                    parent_policy = (intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["parent-path"])
                    class_bytes = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-bytes"])
                    class_pkts = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-pkts"])
                    class_rate = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-rate"])
                    queue_size_pkts = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["queue-size-pkts"])
                    queue_size_bytes = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["queue-size-bytes"])
                    drop_pkts = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["drop-pkts"])
                    drop_bytes = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["drop-bytes"])

                    wred_drop_pkts = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["wred-stats"]["early-drop-pkts"])
                    wred_drop_bytes = int(intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["wred-stats"]["early-drop-bytes"])

                    # Update database with collected statistics and use a plaveholder for stats that aren't collect yet
                    # Placeholders are needed because the DB table requires entries at every column

                    db_int_qos_update_1(host, int_speed, interface, policy_direction, policy_name, parent_policy, class_name, class_pkts, class_bytes,class_rate, drop_pkts, drop_bytes,
                                        place_holder, place_holder, place_holder, place_holder, place_holder, place_holder)

                    # Acess historical database and calculate differences between current (above) and historical stats
                    # Round the numbers so we dont get long integers
                    # Collect the historical polling date for later use.

                    for row in h.execute('SELECT ClassPkts, ClassBytes, ClassRate, DropPkts, DropBytes, DateTime FROM IntStatsQoSCopy WHERE Device=? AND ClassName=?',(host, class_name)):
                        try:
                            time_diff_1 = datetime.datetime.now() - datetime.datetime.strptime(row[5],'%Y-%m-%d %H:%M:%S.%f')
                            time_diff(time_diff_1)

                            try:
                                class_hist_pack = round((class_pkts - int(row[0])) / total_seconds, 2)
                                class_hist_bytes = round((class_bytes - int(row[1])) / total_seconds, 2)
                                class_hist_rate = round((class_rate - int(row[2])) / total_seconds, 1)

                                if class_rate >= int(row[2]):
                                    class_rate_plus_diff = class_rate + class_hist_rate
                                elif class_rate < int(row[2]):
                                    class_rate_plus_diff = class_rate - class_hist_rate

                                drop_hist_pkts = round((drop_pkts - int(row[3])) / total_seconds, 2)
                                drop_hist_bytes = round((drop_bytes - int(row[4])) / total_seconds, 2)

                            except ZeroDivisionError:
                                pass

                            # Update DB table entries with the calculated stats. Since all columns have been created, we only have to UPDATE
                            # with the UPDATE SQL Query

                            try:
                                db_int_qos_update_2(host,  class_name, class_hist_pack, class_hist_bytes, class_rate_plus_diff, drop_hist_pkts, drop_hist_bytes, row[5])
                            except UnboundLocalError:
                                pass
                        except IndexError:
                            pass

                    time.sleep(poll_time) # Polling time, stored globally

                    # Collect the second set of interface qos statistics

                    intf_state_reply_2 = m.get(int_stats)
                    intf_status_2 = xmltodict.parse(intf_state_reply_2.xml)["rpc-reply"]["data"]
                    intf_info_tree_2 = intf_status_2["interfaces-state"]["interface"]
                    int_speed_2 = int(int(intf_info_tree_2["speed"]))

                    timestamp_2 = datetime.datetime.now().timestamp()

                    global timestamp_diff
                    timestamp_diff = float(timestamp_2) - float(timestamp_1)

                    policy_direction_2 = (intf_info_tree_2["diffserv-target-entry"]["direction"])
                    policy_name_2 = (intf_info_tree_2["diffserv-target-entry"]["policy-name"])
                    class_name_2 = (intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-name"])
                    parent_policy_2 = (intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["parent-path"])
                    class_bytes_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-bytes"])
                    class_pkts_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-pkts"])
                    class_rate_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["classifier-entry-statistics"]["classified-rate"])
                    queue_size_pkts_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["queue-size-pkts"])
                    queue_size_bytes_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["queue-size-bytes"])
                    drop_pkts_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["drop-pkts"])
                    drop_bytes_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["drop-bytes"])
                    wred_drop_pkts_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["wred-stats"]["early-drop-pkts"])
                    wred_drop_bytes_2 = int(intf_info_tree_2["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index]["queuing-statistics"]["wred-stats"]["early-drop-bytes"])

                    # Calculate statistics for before and after statistics. Polling perios 10 secs

                    class_pkts_diff = round((class_pkts_2 - class_pkts) / poll_time, 2)
                    class_bytes_diff = round((class_bytes_2 - class_bytes) / poll_time, 2)
                    class_bits_diff = round((class_bytes_2 - class_bytes) * 8 /poll_time , 2)
                    class_rate_diff = round((class_rate_2 - class_rate) / poll_time, 1)

                    if class_rate_2 >= class_rate:
                        class_rate_plus_diff = class_rate_2 + class_rate_diff
                    elif class_rate_2 < class_rate:
                        class_rate_plus_diff = class_rate_2 - class_rate_diff

                    queue_size_pkts_diff = round((queue_size_pkts_2 - queue_size_pkts) / poll_time, 2)
                    queue_size_bytes_diff = round((queue_size_bytes_2 - queue_size_bytes) / poll_time, 2)
                    drop_pkts_diff = round((drop_pkts_2 - drop_pkts) / poll_time, 2)
                    drop_bytes_diff = round((drop_bytes_2 - drop_bytes) * 8 / poll_time, 2)
                    wred_drop_pkts_diff = round((wred_drop_pkts_2 - wred_drop_pkts) / poll_time, 2)
                    wred_drop_bytes_diff = round((wred_drop_bytes_2 - wred_drop_bytes) * 8 / poll_time, 2)

                    try:
                        avrg_packet_size = round(class_bytes_diff / class_pkts_diff, 2)
                    except ZeroDivisionError:
                        avrg_packet_size = place_holder
                        pass

                    # Update Diff Table in DB with the calculations

                    db_int_qos_update_diff(host, int_speed, interface, policy_direction_2, policy_name_2, parent_policy_2, class_name_2, class_pkts_diff, class_bytes_diff, class_bits_diff,
                                class_rate_plus_diff, drop_pkts_diff, drop_bytes_diff, avrg_packet_size)

                    index = index + 1
                except (IndexError):
                    pass
        except KeyError:
            continue
            pass
    db_maintenance(host)
    time.sleep(1)
    view_qos_stats(host)
    print("\n")
    main()

#################################################################################################################################

def device_connect(host):

    # NETCONF login

    try:

        username = input("Username: ")
        password = input("Password: ")

        global m
        m = manager.connect(host=host, port=830, timeout=3, username=username, password=password,
                            device_params={'name': 'csr'})


    except ncclient.NCClientError:
        print("Connection Failed to Host")
        main()
        pass
    except AttributeError:
        print("Connection Failed to Host")
        main()
        pass
    except gaierror:
        print("Connection Failed to Host")
        main()
        pass

def int_headers_diff():

    # Any time database is viewed, filtered or unfiltered these headings will show

    print("\n")
    print("Total: ^")
    print("PerSecond: * ")
    print("\n")
    print("{:>0} {:>66}{:>20} {:>18} {:>19} {:>16} {:>20} ".format( "PolicyTree", "*ClassPkts", "*ClassBytes", "*ClassBits", "*ClassRate", "*DropPkts", "AvrgPktSizeByte"))
    print("_______________________________________________________________________________________________________________"
          "___________________________________________________________________________")

def view_qos_stats_diff(host):

    try:
        # Acess the current database and present the data to the user. User indexing to access data

        print("##########################################################################")
        print("{:>75}".format(" Polling Cycle Diff Statistics  "))
        print("\n")

        for row in c.execute('SELECT DISTINCT Name, PolDirect, Speed FROM IntStatsQoSDiff WHERE Device=?', (host,)):
            print("Interface: {:>0} | Direction:{:<4} | Speed: {:>0} | Poll Interval (sec): {:<4} ".format(
                                                            row[0], row[1], row[2], poll_time))

            int_headers_diff()
            print("\n")
            for row in d.execute('SELECT * FROM IntStatsQoSDiff WHERE Device=? AND Name=? ', (host, row[0])):
                print("{:>0} {:<66} {:<16} {:<20} {:<21} {:<17} {:<15} {:<15} ".format("  ", row[5],  row[7], row[8], row[9], row[10], row[11], row[13]))

            print("\n")
    except sqlite3.OperationalError:
        print(" No Data Available")
        pass
    except IndexError:
        print("No Data Available")
        pass

def int_headers():

    # Any time database is viewed, filtered or unfiltered these headings will show

    print("\n")
    print("Total: ^")
    print("PerSecond: * ")
    print("\n")
    print("{:>0} {:>68}{:>20} {:>18} {:>12} {:>15} {:>18} {:>14} {:>15} {:>12} {:>12}".format
          ("PolicyTree", "^ClassPkts", "^ClassBytes","*ClassRate", "DrPkts", "DrBytes", "*ClPktHist", "*ClBytHist","*ClRtHist","*DrPktHist", "*DrBytHist"))
    print("_________________________________________________________________________________________________________________"
          "_______________________________________________________________________________________________________________________________________")

def view_qos_stats(host):

    # Access the current database and present the current statistics and hostorical differences

    try:

        print("\n")
        print("##########################################################################")
        print("{:>75}".format("Current Stats & Historical Diffs "))
        print("\n")

        pre_poll_date = [row for row in c.execute('SELECT DISTINCT HistDateTime FROM IntStatsQoS WHERE Device=?', (host,))]
        for row in c.execute('SELECT DISTINCT Name, PolDirect, Speed FROM IntStatsQoS WHERE Device=?', (host,)):
            print("Interface: {:>0} | Direction:{:<4} | Speed: {:>0} | Last Poll: {:<4} | *Seconds: {:<4} ".format(row[0], row[1], row[2], pre_poll_date[0][0], total_seconds))
            int_headers()
            print("\n")
            for row in d.execute('SELECT * FROM IntStatsQoS WHERE Device=? AND Name=? ', (host, row[0], )):
                print("{:>0} {:<66} {:<18} {:<20} {:<14} {:<12}  {:<18} {:<14} {:<17} {:<12} {:<11}  {:<10} ".format("  ",
                                                                                 row[5], row[7], row[8], row[9], row[10],
                                                                              row[11], row[12],row[13], row[14], row[15], row[16]))
            print("\n")
        view_qos_stats_diff(host)
    except sqlite3.OperationalError:
        print(" No Data Available")
        pass
    except IndexError:
        print("No Data Available")
        pass


def db_check():

    # Check to see if there is an existing table in the DB, if not create one.

    try:

        c.execute('''CREATE TABLE IntStatsQoS (Device, Name, Speed, PolDirect, PolName, ParentPol, ClassName,  ClassPkts, 
                    ClassBytes, ClassRate, DropPkts, DropBytes, ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, 
                    DateTime, HistDateTime )''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('''CREATE TABLE IntStatsQoSDiff (Device, Name, Speed, PolDirect, PolName, ParentPol, ClassName, ClassPktsDiff, ClassBytesDiff, ClassBitDiff, ClassRateDiff, 
                                                DropPktsDiff, DropBytesDiff, AvrgPktSize, DateTime)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('''CREATE TABLE IntStatsQoSCopy (Device, Name, Speed, PolDirect, PolName, ParentPol, ClassName,  ClassPkts, 
                        ClassBytes, ClassRate, DropPkts, DropBytes, ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, DateTime )''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def del_entry(host):

    try:
        d.execute('DELETE FROM IntStatsQoS WHERE Device=?', (host,))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def del_entry_diff(host):

    try:
        c.execute('DELETE FROM IntStatsQoSDiff WHERE Device=?', (host,))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def del_entry_historical(host):

    try:
        c.execute('DELETE FROM IntStatsQoSCopy WHERE Device=?', (host,))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_int_qos_update_1(host, speed, name, PolDirect, PolName, ParentPol, ClassName,  ClassPakts, ClassBytes, ClassRate, DropPkt, DropBytes,
                        ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, HistDateTime):

    try:
        d.execute("INSERT INTO IntStatsQoS VALUES ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s','%s', '%s', '%s', '%s')" %
                  (host, name, speed, PolDirect, PolName, ParentPol, ClassName,  ClassPakts, ClassBytes, ClassRate, DropPkt, DropBytes,
                   ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, datetime.datetime.now(), HistDateTime))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_int_qos_update_diff(host, speed, name, PolDirect, PolName, ParentPol, ClassName, ClassPakts, ClassBytes, ClassBits, ClassRate, DropPkt, DropBytes, AvrgPktSize):

    try:
        c.execute("INSERT INTO IntStatsQoSDiff VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (host, name, speed, PolDirect, PolName, ParentPol, ClassName, ClassPakts, ClassBytes, ClassBits, ClassRate, DropPkt, DropBytes, AvrgPktSize,  datetime.datetime.now()))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_int_qos_update_2(host, ClassName, ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, HistDateTime):

    try:
        d.execute("UPDATE IntStatsQoS SET ClassPktsDiff=?, ClassBytesDiff=?, ClassRateDiff=?, DropPktsDiff=?, DropBytesDiff=?, HistDateTime=? , DateTime=? WHERE Device=? AND ClassName=?",
                  (ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, DropBytesDiff, HistDateTime, datetime.datetime.now(),  host, ClassName))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_maintenance(host):

    del_entry_historical(host)

    try:
        c.execute(''' INSERT INTO IntStatsQoSCopy SELECT Device, Name, Speed, PolDirect, PolName, ParentPol, ClassName, ClassPkts, 
                        ClassBytes, ClassRate, DropPkts, DropBytes, ClassPktsDiff, ClassBytesDiff, ClassRateDiff, DropPktsDiff, 
                        DropBytesDiff, DateTime FROM IntStatsQoS ''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def time_diff(diff):

    # Converts Date/Time into seconds

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600 * 60
    minutes = (seconds % 3600) // 60

    global total_seconds
    total_seconds = hours + minutes * 60

if __name__ == '__main__':

    db_check()
    module_check()