try:
    import requests
except ImportError:
    print("Module REQUESTS not available.")
    pass
try:
    import warnings
except ImportError:
    print("Module WARNING not available.")
    pass
try:
    import json
except ImportError:
    module_array.append("json")
try:
    import time
except ImportError:
    module_array.append("time")
try:
    import sqlite3
except ImportError:
    module_array.append("sqllite3")
    print("Module SQLITE3 not available.")


ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')

fmc_ip = input("FMC IP: ")
username = input("Username: ")
password = input("Password: ")

mydb = sqlite3.connect("FMC")                                       # Create local DB name FMC
c = mydb.cursor()                                                   # Cusors used to write to DB
d = mydb.cursor()
e = mydb.cursor()
f = mydb.cursor()
g = mydb.cursor()
null = ""

def get_fmc_tokens():

    uri = "https://" + fmc_ip + "/api/fmc_platform/v1/auth/generatetoken"

    # Parse response for the next step of authentication which requires access/refresh tokens and Domain UUID
    # Create headers for your further request to the FMC

    session = requests.Session()
    r = session.post(uri, verify=False, auth=(username, password))
    print(r.headers)
    get_access_token = r.headers["X-auth-access-token"]
    get_refresh_token = r.headers["X-auth-refresh-token"]
    domain_uuid = r.headers["DOMAIN_UUID"]
    headers = {"X-auth-access-token": get_access_token, "X-auth-refresh-token": get_refresh_token }

    return  session, headers, domain_uuid

def objects(dom_uidd, type, id):

    # Use the URI component recieved from main to build URI. Time.sleep is used to slow the pace of get request (120 per minute)
    # Convert the request to a dictionary and return it to the caller.
    # This process is done for every object. Remember, in the rule it gives us object name and ID, not values. Line 77

    time.sleep(.5)
    uri = "https://" + fmc_ip + "/api/fmc_config/v1/domain/" + fmc_access[2] + "/object/" + type + "/" + id + ""
    r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))

    try:
        object = r.json()
        insert_object(object["id"])
        print(object)

        # Update the Object_Used table. Set column attributes to the values stored in the object dictionary

        try:
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?", (object["type"],object["name"], object["value"], object["id"],))
            mydb.commit()
        except KeyError:
            pass

    except json.JSONDecodeError as error:
        object = "Error"
        pass

    return object # Return the object to the caller si ut can be update/stored in the database

def create_fw_table():

    # Create a table within the DB. Add four columns, can be nore if needed.

    try:
        d.execute('''CREATE TABLE FMC_Rules  (RuleNumber, Name,  SrcInt, dstInt, srcNet, dstNet, srcPort_1,  
                                              vlanTags, users, apps, srcPort, dstPort, URLS, iseAtts, action)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def insert_firewall(ruleNumber):

    # Insert the row in the DB. Takes one argument which is the rule ID. The null will be filled in during program runtime. This has to match the number of comlumns
    # when the tabe is created.

    try:
        d.execute("INSERT INTO FMC_Rules VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',"
                                                "'%s', '%s')" %(ruleNumber, null, null, null, null, null, null, null, null, null, null, null, null, null, null))
        mydb.commit()
    except sqlite3.OperationalError :
        pass

def create_obj_used_table():

    # Create a table within the DB. Add four columns, can be nore if needed.

    try:
        d.execute('''CREATE TABLE Object_Used  (id, type,  name, value)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def insert_object(objectid):

    # Insert the row in the DB. Takes one argument which is the object ID. The null will be filled in during program runtime

    try:
        d.execute("INSERT INTO Object_Used VALUES ('%s', '%s', '%s', '%s')" % (objectid, null, null, null))
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def update_db(table, column, where_1, list, where_2):

    # This function update our sql DB with the requested arguments
    # 1. Table to update
    # 2. Column to update
    # 3. Row to update
    # 4. New data
    # The two variables on the far right in () are the variable we are placing in the ?.
    # We then commit/save to the DB

    d.execute("UPDATE " + table + " SET " + column + "=? WHERE " + where_1 + "=?", (list, where_2,))
    mydb.commit()

if __name__ == '__main__':

    create_fw_table()                                                                                           # Create the fw table in the DB
    create_obj_used_table()                                                                                     # Creates the objected used table in the DB
    fmc_access = get_fmc_tokens()                                                                               # Get FMC access tokens

    # Request access policies from the FMC, or all rule sets the FMC has
    # Turn response into a dictionary  using .json
    # Get the the number of policies using "count" value

    uri = "https://" + fmc_ip + "/api/fmc_config/v1/domain/" + fmc_access[2] +"/policy/accesspolicies"
    r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))
    access_pol = r.json()
    count = access_pol["paging"]["count"]

    # Now that we have all policies lets access them to see what rules are inside
    # Since we have "count" policies, we will use each policy ID obtained from acceess_pol dictionary. This id will be placed in the URI.
    # Make the request which gives us all access rules in the policy. We will create access_rule dictionary

    for i in range(0, count):

            uri = access_pol["items"][i]["links"]["self"] + "/accessrules?offset=1&limit=1000"
            r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))
            access_rule = r.json()

            # Now that we have our access_rule dictionary, we will need to dig another layer into the rule. Why? Because FMC only give us object names, not object values
            # We will uses the range command to iterate through 1000 rules. You may not have tha many or more. Its an arbitrary number

            rule = 0
            try:
                for rule in range(0,5000):
                    print(str(rule))
                    try:

                        # Using the self key/value in the the access_rule dict we can get the URI of the particular rule.
                        # Once we've access the rule we will create another dictionary from the REST response. string() is the dictionary in this case

                        uri = access_rule["items"][rule]["links"]["self"]
                        r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))

                        try:
                            string = r.json()
                        except json.JSONDecodeError:
                            pass

                        try:

                            string["error"]["messages"][0]["description"] == "Access token invalid."
                            time.sleep(10)
                            fmc_access = get_fmc_tokens()
                            r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))
                            string = r.json()

                        except KeyError as error:
                            pass
                    except IndexError:
                        continue

                    # Heres where we convert the object names to values. They key items are  needed for conversion are object types, object id, and domain UUID
                    # They're all components of the URI which is needed to convert the objects

                    try:
                        print(string["name"])
                    except KeyError as error:
                        pass

                    insert_firewall(rule)

                    try:
                        update_db("FMC_Rules", "action", "RuleNumber", string["action"], str(rule))                     # Write rule action and number to db using update_db() function
                    except (KeyError, TypeError):
                        pass

                    try:
                        update_db("FMC_Rules", "Name", "RuleNumber", string["name"], str(rule))                         # Write rule name and number to db using update_db() function
                    except (KeyError, TypeError):
                        pass

                    try:

                        src_net = [ ]                                                                                   # Use comments for destination networks section
                        for i in string["sourceNetworks"]["objects"]:                                                   # Access the sourceNetwork, object list of dictionaries, notice iteration

                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])                                    # Call the get_object_value funtions and send required URI components
                            src_net.append(get_object_value["value"])                                                   # Append list returned from objects

                        src_list = [ i for i in src_net]                                                                # List can't be stored to db so we convert it to string using join()
                        update_db("FMC_Rules", "srcNet", "RuleNumber", ",".join(src_list), str(rule))                   # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:                                                              # You will recive a Keyerror if the rule is set to ANY. FMC does'nt return src - ANY
                        update_db("FMC_Rules", "srcNet", "RuleNumber", "Any", str(rule))                                # Call the update DB function, send name, column variables
                        pass

                    try:

                        dst_net = [ ]
                        for i in string["destinationNetworks"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            dst_net.append(get_object_value["value"])

                        dst_list = [i for i in dst_net]
                        update_db("FMC_Rules", "dstNet", "RuleNumber", ",".join(dst_list), str(rule))

                    except (KeyError, TypeError) as error:
                        update_db("FMC_Rules", "dstNet", "RuleNumber", "Any", str(rule))                                # If keyError occurs, write "Any" into DB
                        pass

                    try:

                        src_ports = [ ]                                                                                 # Use comments for destination ports section
                        for i in string["sourcePorts"]["objects"]:                                                      # Access the sourcePorts, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])                                    # Call the get_object_value funtions and send reuqired URI components

                            try:
                                src_ports.append(get_object_value["protocol"] + "-" + get_object_value["port"])
                            except (KeyError, TypeError):
                                pass

                            try:
                                for i in get_object_value["objects"]:
                                    src_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass

                        src_port_list = [i for i in src_ports]                                                          # List can't be stored to db so we convert it to string using join()
                        update_db("FMC_Rules", "srcPort", "RuleNumber", ",".join(src_port_list), str(rule))             # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:
                        update_db("FMC_Rules", "srcPort", "RuleNumber", "Any", str(rule))                               # If keyError occurs, write "Any" into DB
                        pass

                    try:

                        dst_ports = [ ]
                        for i in string["destinationPorts"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])

                            try:
                                dst_ports.append(get_object_value["protocol"] + "-" + get_object_value["port"])
                            except KeyError:
                                pass

                            try:
                                for i in get_object_value["objects"]:
                                    dst_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass

                        dst_port_list = [i for i in dst_ports]
                        update_db("FMC_Rules", "dstPort", "RuleNumber", ",".join(dst_port_list), str(rule))

                    except (KeyError, TypeError) as error:
                        update_db("FMC_Rules", "dstPort", "RuleNumber", "Any", str(rule))
                        pass

                    try:
                                                                                                                        # Use coments for destination zones section
                        for i in string["sourceZones"]["objects"]:                                                      # Access the sourcePorts, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            update_db("FMC_Rules", "srcInt", "RuleNumber", get_object_value["name"], str(rule))         # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:
                        update_db("FMC_Rules", "srcInt", "RuleNumber", "Any", str(rule))                                # If keyError occurs, write "Any" into DB
                        pass

                    try:

                        for i in string["destinationZones"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            update_db("FMC_Rules", "dstInt", "RuleNumber",get_object_value["name"], str(rule))

                    except (KeyError, TypeError) as error:
                        update_db("FMC_Rules", "dstInt", "RuleNumber", "Any", str(rule))
                        pass

                    rule = rule + 1

            except (json.JSONDecodeError, IndexError, KeyError):
                pass
            program_end = input("Press Enter to Close Windows")
