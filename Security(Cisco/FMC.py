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
mydb = sqlite3.connect("FMC_9")
c = mydb.cursor()
d = mydb.cursor()
null = ""

def get_fmc_tokens():

    uri = "https://" + fmc_ip + "/api/fmc_platform/v1/auth/generatetoken"

    # Parse response for the next step of authentication which requires access/refresh tokens and Domain UUID
    # Create headers for your further request to the FMC

    session = requests.Session()
    r = session.post(uri, verify=False, auth=(username, password))
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
        nested_objects = [ ]
        object = r.json()
        print(object)

        # Lines 71- 83 gets nested objects. The i variable represents each list within the list. We will save targeted k/v pairs to list return it to caller
        # Process

        # This block of code is for nested objects
        # The host object will return as they dont need anymore inspection. for group we need to loop again. Using GET
        # Get the type in lower for the URI requirement
        # Use the UUID and object ID
        # Convert reponse to dict r.json()
        # Store the value to list and return it to caller nested_objects()
        # The process is the same down to line 142

        try:
            for i in object["objects"]:

                try:
                    insert_object(i["id"])
                    nested_objects.append(i["port"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(i["type"], i["name"], i["port"], i["id"],))
                    mydb.commit()
                except KeyError as error:
                    pass

                try:
                    insert_object(i["id"])
                    nested_objects.append("ICMP" + "-" + i["icmpType"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?", (i["type"], i["name"], i["icmpType"], i["id"],))
                    mydb.commit()
                except KeyError as error:
                    pass
        except KeyError as error:
            pass

        # Write any interface objects to th DB if they are nested

        try:
            for objects in object["interfaces"]:
                try:
                    insert_object(object["id"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(objects["type"], objects["name"], objects["name"],  objects["id"],))
                    mydb.commit()
                except KeyError:
                    pass
        except KeyError:
            pass


        try:
            for i in object["objects"]:

                obj_type = str(i["type"] + "s").lower()
                time.sleep(.5)

                uri = "https://" + fmc_ip + "/api/fmc_config/v1/domain/" + fmc_access[2] + "/object/" + obj_type + "/" + i["id"] + ""
                r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))
                nested_object = r.json()

                try:
                    insert_object(nested_object["id"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(nested_object["type"], nested_object["name"], nested_object["value"], nested_object["id"],))
                    mydb.commit()
                    nested_objects.append(nested_object["value"])
                except KeyError:
                    pass

        except KeyError:
            pass

        # Write any icmp objects to th DB if they aren't nested

        try:
            insert_object(object["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(object["type"], object["icmpType"], object["name"], object["id"],))
            mydb.commit()
        except KeyError as error:
            pass

        # Write any protocol/port objects to th DB if they aren't nested

        try:
            insert_object(object["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=?, protocol=? WHERE id=?",(object["type"], object["name"], object["port"], object["protocol"], object["id"],))
            mydb.commit()
        except KeyError:
            pass

        # Update the Object_Used table. Set column attributes to the values stored in the object dictionary

        try:
            insert_object(object["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?", (object["type"],object["name"], object["value"], object["id"],))
            mydb.commit()
        except KeyError:
            pass

    except json.JSONDecodeError as error:
        object = "Error"
        pass

    cleanup_db()                    # This will cleant duplcate entries from out DB. To reduce conditional code in the latter code.
    return object, nested_objects   # Return the object to the caller si ut can be update/stored in the database

def create_fw_table(table):

    # Create a table within the DB. Add four columns, can be nore if needed.

    try:
        d.execute('''CREATE TABLE ''' + table + '''  (Name,  SrcInt, dstInt, srcNet, dstNet, vlanTags, users, apps, srcPort, dstPort, URLS, iseAtts, action)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def insert_firewall(ruleset, ruleName):

    # Insert the row in the DB. Takes one argument which is the rule ID. The null will be filled in during program runtime. This has to match the number of comlumns
    # when the tabe is created.

    try:
        d.execute("INSERT INTO " + rule_set + " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (ruleName,  null, null, null, null, null, null, null, null, null, null, null, null))
        mydb.commit()
    except sqlite3.OperationalError as error:
        pass

def cleanup_db():

    # Cleanup any duplicate DB entries, keeping the most old (min)

    try:
        for row in c.execute('SELECT * FROM Object_Used'): # Cleanup any database duplicates
                c.execute('DELETE FROM Object_Used WHERE rowid not in (SELECT min(rowid) FROM Object_Used GROUP BY id)')
                mydb.commit()
    except sqlite3.OperationalError:
        pass

def create_obj_used_table():

    # Create a table within the DB. Add four columns, can be nore if needed.

    try:
        d.execute('''CREATE TABLE Object_Used  (id, type,  name, value, protocol)''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def insert_object(objectid):

    # Insert the row in the DB. Takes one argument which is the object ID. The null will be filled in during program runtime

    try:
        d.execute("INSERT INTO Object_Used VALUES ('%s', '%s', '%s', '%s', '%s')" % (objectid, null, null, null, null))
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

            rule_set = access_pol["items"][i]["name"].replace("-", "_")
            uri = access_pol["items"][i]["links"]["self"] + "/accessrules?offset=1&limit=1000"                          # offset is rule 2, limit is 100 rules per page. 1000 is max
            r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))
            access_rule = r.json()
            create_fw_table(rule_set)

            # Now that we have our access_rule dictionary, we will need to dig another layer into the rule. Why? Because FMC only give us object names, not object values
            # We will uses the range command to iterate through 1000 rules. You may not have tha many or more. Its an arbitrary number

            rule = 0
            paging_number = 0

            try:
                for i in range(0,5000):

                    if rule == int(access_rule["paging"]["limit"]):                                                     # Check to see if we reached our paging limit use K/V pairs
                        try:
                            rule = 0                                                                                    # If so, reset the rule or index to 0 since we will go to next page/ruleset
                            uri = access_rule["paging"]["next"][0]                                                      # Get the next ruleset by using the next k/v pair, storing it as out URI
                            r = fmc_access[0].get(uri, verify=False, headers=fmc_access[1], auth=(username, password))  # Request the next page/rule set
                            access_rule = r.json()                                                                      # Save response to dictionary
                        except IndexError as error:
                            pass
                    else:                                                                                               # If we haven't reached our paging limit, pass, continue will current page/ruleset
                        pass

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

                    # Heres where we convert the object names to values. They key items are  needed for conversion are object types, object id, and domain UUID
                    # They're all components of the URI which is needed to convert the objects

                    try:
                        print(string["name"])
                        rule_name = string["name"]
                    except KeyError as error:
                        pass
                    
                    insert_firewall(rule_set, rule_name)

                    try:
                        update_db(rule_set, "action", "Name", string["action"], rule_name)                           # Write rule action and number to db using update_db() function
                    except (KeyError, TypeError):
                        pass

                    try:

                        src_net = [ ]                                                                                   # Use comments for destination networks section
                        for i in string["sourceNetworks"]["objects"]:                                                   # Access the sourceNetwork, object list of dictionaries, notice iteration

                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])                                    # Call the get_object_value[0] funtions and send required URI components

                            try:
                                src_net.append(get_object_value[0]["value"])                                            # Append list returned from objects
                            except KeyError:
                                pass

                            nested_list = [src_net.append(i) for i in get_object_value[1]]

                        src_list = [ i for i in src_net]                                                                # List can't be stored to db so we convert it to string using join()
                        update_db(rule_set, "srcNet", "Name", ",".join(src_list), rule_name)                         # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:                                                              # You will recive a Keyerror if the rule is set to ANY. FMC does'nt return src - ANY
                        update_db(rule_set, "srcNet", "Name", "Any", rule_name)                                      # Call the update DB function, send name, column variables
                        pass

                    try:

                        dst_net = [ ]
                        for i in string["destinationNetworks"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])

                            try:
                                dst_net.append(get_object_value[0]["value"])
                            except KeyError:
                                pass

                            nested_list = [dst_net.append(i) for i in get_object_value[1]]                              # Unpack nested objects and store to a list. Objects are second variable
                                                                                                                        # returned from the get_objects_ function
                        dst_list = [i for i in dst_net]
                        update_db(rule_set, "dstNet", "Name", ",".join(dst_list), rule_name)

                    except (KeyError, TypeError) as error:
                        update_db(rule_set, "dstNet", "Name", "Any", rule_name)                                      # If keyError occurs, write "Any" into DB
                        pass



                    src_ports = [ ]
                    try:
                        for i in string["sourcePorts"]["literals"]:                                                    # These are type literal. Which means they dont have an object associaited
                            try:
                                dst_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass
                    except (KeyError, TypeError):
                        pass

                    try:                                                                                                # Use comments for destination ports section
                        for i in string["sourcePorts"]["objects"]:                                                      # Access the sourcePorts, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])                                    # Call the get_object_value[0] funtions and send reuqired URI components
                            nest_objects = [src_ports.append(i) for i in get_object_value[1]]                           # Iterate through list of nested ports from parent. Store to list

                            try:
                                src_ports.append(get_object_value[0]["protocol"] + "-" + get_object_value[0]["port"])   # Get single objects which aren't nested. Store to list
                            except (KeyError, TypeError):
                                pass

                            try:
                                for i in get_object_value[0]["objects"]:                                                # Iterate list of objects. No parent
                                    src_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass

                        src_port_list = [i for i in src_ports]                                                          # List can't be stored to db so we convert it to string using join()
                        update_db(rule_set, "srcPort", "Name", ",".join(src_port_list), rule_name)                   # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:
                        update_db(rule_set, "srcPort", "Name", "Any", rule_name)                                     # If keyError occurs, write "Any" into DB
                        pass




                    dst_ports = [ ]
                    try:
                        for i in string["destinationPorts"]["literals"]:
                            try:
                                dst_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass
                    except (KeyError, TypeError):
                        pass

                    try:
                        for i in string["destinationPorts"]["objects"]:

                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            nest_objects = [dst_ports.append(i) for i in get_object_value[1]]

                            try:
                                dst_ports.append(get_object_value[0]["protocol"] + "-" + get_object_value[0]["port"])
                            except (KeyError, TypeError):
                                pass

                            try:
                                for i in get_object_value[0]["objects"]:
                                    dst_ports.append(i["protocol"] + "-" + i["port"])
                            except (KeyError, TypeError):
                                pass

                        dst_port_list = [i for i in dst_ports]
                        update_db(rule_set, "dstPort", "Name", ",".join(dst_port_list), rule_name)

                    except (KeyError, TypeError) as error:
                        update_db(rule_set, "dstPort", "Name", "Any", rule_name)
                        pass



                    try:
                                                                                                                        # Use coments for destination zones section
                        for i in string["sourceZones"]["objects"]:                                                      # Access the sourcePorts, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            update_db(rule_set, "srcInt", "Name", get_object_value[0]["name"], rule_name)            # Call the update DB function, send name, column variables

                    except (KeyError, TypeError) as error:
                        update_db(rule_set, "srcInt", "Name", "Any", rule_name)                                      # If keyError occurs, write "Any" into DB
                        pass

                    try:

                        for i in string["destinationZones"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(fmc_access[2], type, i["id"])
                            update_db(rule_set, "dstInt", "Name",get_object_value[0]["name"], rule_name)

                    except (KeyError, TypeError) as error:
                        update_db(rule_set, "dstInt", "Name", "Any", rule_name)
                        pass

                    rule = rule + 1
                    paging_number = paging_number + 1

            except (json.JSONDecodeError,KeyError, IndexError) as error:
                pass
