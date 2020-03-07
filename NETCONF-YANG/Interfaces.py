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
int_array = []
int_2_array = []
total_seconds = " "
not_app = "N/A"

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
        print("2. View Current Database (By Device)") # Data from last poll
        print("3. View Historical Database (By Device)") # Data from two polls ago
        print("\n")
        selection = input("Selection: ")
        print("\n")

        if selection == "1":

            host = input("IP: ")
            device_connect(host)
            interfaces(host)
            main()
            break

        elif selection == "2":

            host = input("IP: ")
            view_stats(host)
            main()
            break

        elif selection == "3":
            host = input("IP: ")
            view_copy_stats(host)
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

    # Before we get the interfaces, we will delete the current interfaces in the current database. This is for just
    # in case we deleted an interface on a device, like a tunnel or loopback. The new output will reflect the current interfaces

    del_entry(host)

    # Loop through the array(s) created above and put the entries into the int stats variable. This will allow us to loop through
    # all interface an get statistics.

    int_headers()
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

        timestamp_1 = datetime.datetime.now().timestamp()  # Get time of the first stats poll = cont line 290
        intf_state_reply = m.get(int_stats)
        intf_status = xmltodict.parse(intf_state_reply.xml)["rpc-reply"]["data"]
        intf_info_tree = intf_status["interfaces-state"]["interface"]

        stats_bytes_in = int(intf_info_tree["statistics"]["in-octets"])
        stats_bytes_out = int(intf_info_tree["statistics"]["out-octets"])

        time.sleep(10) # Using sleep we can determine the polling period

        timestamp_2 = datetime.datetime.now().timestamp()
        intf_state_reply_2 = m.get(int_stats)
        intf_status_2 = xmltodict.parse(intf_state_reply_2.xml)["rpc-reply"]["data"]
        intf_info_tree_2 = intf_status_2["interfaces-state"]["interface"]

        int_speed = int(int(intf_info_tree["speed"]) // 1e+9) # Calculate interface speed in bits and convert to megabits
        print(intf_info_tree["speed"])

        stats_bytes_in_2 = int(intf_info_tree_2["statistics"]["in-octets"])
        stats_bytes_out_2 = int(intf_info_tree_2["statistics"]["out-octets"])

        # Get packet errors/discards
        in_dis = intf_info_tree["statistics"]["in-discards"]
        in_err = intf_info_tree["statistics"]["in-errors"]
        out_dis = intf_info_tree["statistics"]["out-discards"]
        out_err = intf_info_tree["statistics"]["out-errors"]

        timestamp_diff = float(timestamp_2) - float(timestamp_1)    # Subtracts lines 290 and 298, apply to bandwidth formuals

        # Bandwidth calculation for inbound - cont line 320

        try:
            bytes_in_diff = stats_bytes_in_2 - stats_bytes_in
            bits_in = int(bytes_in_diff * 8 // timestamp_diff)
            calc_1 = round(bytes_in_diff * 8 * 100 , 4)
            calc_1_1 = round(timestamp_diff * int(intf_info_tree["speed"]), 2)
            mbps_in_perc =  round(calc_1 / calc_1_1, 2)
        except ValueError:
            pass

        # Bandwidth Calculation for inbound - cont 331

        try:
            bytes_out_diff = stats_bytes_out_2 - stats_bytes_out
            bits_out = int(bytes_out_diff * 8 // timestamp_diff)
            calc_2 = round(bytes_out_diff * 8 * 100, 4)
            calc_2_1 = round(timestamp_diff * int(intf_info_tree["speed"]), 2)
            mbps_out_perc = round(calc_2 / calc_2_1, 2)
        except ValueError:
            pass

        db_int_update(host, interface, int_speed, bits_in, bits_out , mbps_in_perc,  # Update current database - cont line 329
                      mbps_out_perc, not_app, not_app, out_dis, out_err, in_dis, in_err, stats_bytes_in, stats_bytes_out)

#################################################################################################################################

        # The below section of code accesses a copy/older table in the database, get the PktsIn, PktsOut and subtracts the current byte total
        # by the historical. This will give you the average Mbps second over that time period. That calculation is then updated in the current
        # database.

        for row in c.execute('SELECT PktsIn, DateTime FROM IntStatsCopy WHERE Name=?', (interface,)):

            # Calculate the time difference in seconds. Current data/time minus older database data/time for the interfcae

            time_diff_1 = datetime.datetime.now() - datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f')
            time_diff(time_diff_1) # Lines 377 - 386

            # Bandwidth calculation for inbound - cont line 318

            if stats_bytes_in < stats_bytes_in:
                counter_rollover = stats_bytes_in + (4294967296 - int[0])     # Calculater if there is one counter rollover
                bits_in = counter_rollover - stats_bytes_in
                calc_1 = round(bits_in * 8 * 100, 4)
                calc_1_1 = round(total_seconds * int(intf_info_tree["speed"]), 2)
                mbps_in_perc = round(calc_1 / calc_1_1, 2)
            else:
                bits_in = stats_bytes_in_2 - stats_bytes_in
                calc_1 = round(bits_in * 8 * 100, 4)
                calc_1_1 = round(total_seconds * int(intf_info_tree["speed"]), 2)
                mbps_in_perc = round(calc_1 / calc_1_1, 2)
            try:
                d.execute("UPDATE IntStats SET InDiff=? WHERE Name=?", (str(mbps_in_perc), interface))
                mydb.commit()
            except (UnboundLocalError, sqlite3.OperationalError):
                pass

        for row in c.execute('SELECT PktsOut, DateTime FROM IntStatsCopy WHERE Name=?', (interface,)):

            # Calculate the time difference in seconds. Current data/time minus older database data/time for the interfcae

            time_diff_2 = datetime.datetime.now() - datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f')
            time_diff(time_diff_1)  # Lines 377 - 386

            # Bandwidth Calculation for inbound - cont 324

            if stats_bytes_out < stats_bytes_out:
                counter_rollover = stats_bytes_in + (4294967296 - int(int[0]))     # Calculater if there is a counter rollover
                bits_out = counter_rollover - stats_bytes_out
                calc_2 = round(bits_out * 8 * 100, 4)
                calc_2_1 = round(total_seconds * int(intf_info_tree["speed"]), 2)
                mbps_out_perc = round(calc_2 / calc_2_1, 2)
            else:
                bits_out = stats_bytes_out_2 - stats_bytes_out
                calc_2 = round(bits_out * 8 * 100, 4)
                calc_2_1 = round(total_seconds * int(intf_info_tree["speed"]), 2)
                mbps_out_perc = round(calc_2 / calc_2_1, 2)

            try:
                d.execute("UPDATE IntStats SET OutDiff=? WHERE Name=?", (str(mbps_out_perc), interface))
                mydb.commit()
            except (UnboundLocalError, sqlite3.OperationalError):
                pass

        real_time_view(host, interface)

    db_maintenance()
    main()

def time_diff(diff):

    # Converts Date/Time into seconds

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600 * 60
    minutes = (seconds % 3600) // 60

    global total_seconds
    total_seconds = hours + minutes * 60

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
    except KeyboardInterrupt:
        main()

def int_headers():

    # Any time database is viewed, filtered or unfiltered these headings will show

    print("\n")
    print("{:>26} {:>21} {:>22} {:>21} {:>21} {:>21} {:>17} {:>14} {:>14} {:>14} {:>14} {:>14}".format
          ("Interface(s)", "Speed (Gbps) ",  "In (Bits/Sec)", "Out (Bits/Sec)",  "Utl In (%)", "Utl Out (%)", "In Diff (%)", "Out Diff (%)",  "Out Dis", "Out Err", "In Dis", "In Err"))
    print("_______________________________________________________________________________"
          "_______________________________________________________________________________"
          "_______________________________________________________________________________")
    print("\n")

def view_stats(host):

    try:
        # Acess the current database and present the data to the user. User indexing to access data
        date = [row[13] for row in c.execute('SELECT * FROM IntStats WHERE Device=?', (host,))]  # historical date
        print("\n")
        print("{:2} {:1}".format("Historical Data Collected On", date[0]))

        int_headers()
        try:

            for row in c.execute('SELECT * FROM IntStats WHERE Device=?', (host, )):
                print("{:>0} {:>25} {:>15} {:>20} {:>23} {:>22} {:>20} {:>19} {:>13} {:>13} {:>16} {:>13} {:>14}".format("  ",
                            row[1], row[2], row[3], row[4] , row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
            print("\n")

        except sqlite3.OperationalError:
            print(" No Data Available")
            pass
    except IndexError:
        print("No Data Available")
        pass

def real_time_view(host, interface):

    # Acess the current database and present the data to the user. User indexing to access data

    try:

        for row in c.execute('SELECT * FROM IntStats WHERE Device=? AND Name=?', (host, interface, )):
            print("{:>0} {:>25} {:>15} {:>20} {:>23} {:>22} {:>20} {:>19} {:>13} {:>13} {:>16} {:>13} {:>14}".format("  ",
                        row[1], row[2], row[3], row[4] , row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
        print("\n")

    except sqlite3.OperationalError:
        print(" No Data Available")
        pass
    except IndexError:
        pass

def view_copy_stats(host):

    # Acess the copy/older database and present the data to the user. User indexing to access data. Not used in program
    # but is avaiable if desired.

    try:

        date = [row[13] for row in c.execute('SELECT * FROM IntStatsCopy WHERE Device=?', (host, ))] # historical date
        print("\n")
        print("{:2} {:1}".format("Log Date/Time:", date[0]))
        int_headers()
        for row in c.execute('SELECT * FROM IntStatsCopy WHERE Device=?', (host, )):
            print("{:>0} {:>25} {:>15} {:>20} {:>23} {:>22} {:>20} {:>19} {:>13} {:>13} {:>16} {:>13} {:>14}".format("  ",
                        row[1], row[2], row[3], row[4] , row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
        print("\n")

    except sqlite3.OperationalError:
        pass
    except IndexError:
        print("No Historical Data Available")
        pass

def db_maintenance():

    # Cleanup any duplicate DB entries, keeping the most current (max)

    try:
        for row in c.execute('SELECT * FROM IntStatsCopy'): # Cleanup any database duplicates
                c.execute('DELETE FROM IntStatsCopy WHERE rowid not in (SELECT max(rowid) FROM IntStatsCopy GROUP BY Device)')
                mydb.commit()
    except sqlite3.OperationalError:
        pass

    # Copies newer database entries to the copy database. This is later used to get historical differences.

    try:
        c.execute(''' INSERT INTO IntStatsCopy SELECT Device, Name, Speed, InBits, OutBits, InPerc, OutPerc, InDiff, OutDiff,
                    OutDis, OutErr, InDis, InErr, DateTime, PktsIn, PktsOut FROM IntStats ''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_int_update(host, name, speed, InBits, OutBits, InPerc, OutPerc, InDiff, OutDiff, OutDis, OutErr, InDis, InErr, PktsIn, PktsOut):

    # Update the current database with data collected in interfaces() function

    try:
        d.execute("INSERT INTO IntStats VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (host, name, speed, InBits, OutBits, InPerc, OutPerc, InDiff, OutDiff, OutDis, OutErr, InDis, InErr, datetime.datetime.now(), PktsIn, PktsOut))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_check():

    # Check to see if there is an existing table in the DB, if not create one. 2 our created below, primary table, and
    # copy for hostorical data.

    try:
        c.execute('''CREATE TABLE IntStats (Device, Name, Speed, InBits, OutBits, InPerc, OutPerc, InDiff, OutDiff, OutDis, 
                    OutErr, InDis, InErr, DateTime, PktsIn, PktsOut)''')
        mydb.commit()

        c.execute('''CREATE TABLE IntStatsCopy (Device, Name, Speed, InBits, OutBits, InPerc, OutPerc, InDiff, OutDiff,  OutDis, 
                    OutErr, InDis, InErr, DateTime, PktsIn, PktsOut)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass


def del_entry(host):

    try:
        c.execute('DELETE FROM IntStats WHERE Device=?', (host,))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

if __name__ == '__main__':

    db_check()
    module_check()