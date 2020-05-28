try:
    import requests
except ImportError:
    pass
try:
    import warnings
except ImportError:
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
import  FMC_Sockets


ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')

mydb = sqlite3.connect("FMC_10")
c = mydb.cursor()
d = mydb.cursor()
null = ""


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
        d.execute("INSERT INTO " + ruleset + " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
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


class fmc:

    def __init__(self):

        self.username = None
        self.password = None
        self.net_loc = None
        self.ip = None
        self.query = None
        self.auth_key = None
        self.refresh_key = None
        self.domain_uuid = None
        self.stop_query = None

    def get_fmc_tokens(self):

        # Parse response for the next step of authentication which requires access/refresh tokens and Domain UUID
        # Create headers for your further request to the FMC

        path = "/api/fmc_platform/v1/auth/generatetoken"
        fmc_auth = FMC_Sockets.contact_fmc()
        fmc_auth.username = self.username
        fmc_auth.password = self.password
        fmc_auth.net_loc = self.net_loc
        fmc_auth.path = path
        fmc_auth.ip = self.ip
        fmc_tokens = fmc_auth.post(path)

        self.auth_key = fmc_tokens[0]
        self.refresh_key = fmc_tokens[1]
        self.domain_uuid = fmc_tokens[2]

        return fmc_auth

    def get_rules(self):


        errored_uri = [ ]
        create_obj_used_table()                                                                                                                                                                                                                                 # Creates the objected used table in the DB
        fmc_access = fmc.get_fmc_tokens(self)

        # Request access policies from the FMC, or all rule sets the FMC has
        # Turn response into a dictionary  using .json
        # Get the the number of policies using "count" value

        path = "/api/fmc_config/v1/domain/" + self.domain_uuid +"/policy/accesspolicies"
        policies = fmc_access.get(path, self.auth_key, self.refresh_key)
        count = policies["paging"]["count"]

        # Now that we have all policies lets access them to see what rules are inside
        # Since we have "count" policies, we will use each policy ID obtained from acceess_pol dictionary. This id will be placed in the URI.
        # Make the request which gives us all access rules in the policy. We will create access_rule dictionary

        for i in range(0, count):

                rule_set = policies["items"][i]["name"].replace("-", "_")
                path = policies["items"][i]["links"]["self"] + "/accessrules?" + self.query                                                                                                                                                                                            # offset is rule 2, limit is 100 rules per page. 1000 is max
                response = fmc_access.get(path, self.auth_key, self.refresh_key)
                create_fw_table(rule_set)
                # Now that we have our access_rule dictionary, we will need to dig another layer into the rule. Why? Because FMC only give us object names, not object values
                # We will uses the range command to iterate through 1000 rules. You may not have tha many or more. Its an arbitrary number

                rule = 0
                auth_counter = 0
                rule_num = 0

                for i in range(0,5000):

                    if auth_counter == 20:
                        auth_counter = 0
                        fmc_access = fmc.get_fmc_tokens(self)
                        rules = fmc_access.get(path, self.auth_key, self.refresh_key)
                    else:
                        pass

                    try:
                        if rule == int( response["paging"]["limit"]):
                            print("yes")
                            try:
                                rule = 0
                                path = response["paging"]["next"][0]
                                print(path)
                                response = fmc_access.get(path, self.auth_key, self.refresh_key)
                            except (IndexError, KeyError) as error:
                                break
                        else:
                            pass

                        path = response["items"][rule]["links"]["self"]
                        rules = fmc_access.get(path, self.auth_key, self.refresh_key)

                        try:
                            rule_name = rules["name"]
                            print("{:<25}{:<35}{:<20}".format(self.ip,  rule_name , time.perf_counter()))
                        except (KeyError) as error:
                            pass

                        insert_firewall(rule_set, rule_name)

                        try:
                            update_db(rule_set, "action", "Name", rules["action"], rule_name)
                        except (KeyError, TypeError):
                            pass

                        try:

                            src_net = [ ]
                            for i in rules["sourceNetworks"]["objects"]:
                                type = str(i["type"] + "s").lower()
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])
                                try:
                                    src_net.append(get_object_value[0]["value"])
                                except KeyError:
                                    pass

                                nested_list = [src_net.append(i) for i in get_object_value[1]]

                            src_list = [ i for i in src_net]                                                                                                                                                                            # List can't be stored to db so we convert it to rules using join()
                            update_db(rule_set, "srcNet", "Name", ",".join(src_list), rule_name)                                                                                                                                                    # Call the update DB function, send name, column variables

                        except (KeyError, TypeError) as error:                                                                                                                                                                      # You will recive a Keyerror if the rule is set to ANY. FMC does'nt return src - ANY
                            update_db(rule_set, "srcNet", "Name", "Any", rule_name)                                                                                                                                               # Call the update DB function, send name, column variables
                            pass

                        try:

                            dst_net = [ ]
                            for i in rules["destinationNetworks"]["objects"]:
                                type = str(i["type"] + "s").lower()
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])

                                try:
                                    dst_net.append(get_object_value[0]["value"])
                                except KeyError:
                                    pass

                                nested_list = [dst_net.append(i) for i in get_object_value[1]]                                                                                                                                              # Unpack nested objects and store to a list. Objects are second variable
                                                                                                                                                                                                                                                                                                  # returned from the get_objects_ function
                            dst_list = [i for i in dst_net]
                            update_db(rule_set, "dstNet", "Name", ",".join(dst_list), rule_name)

                        except (KeyError, TypeError) as error:
                            update_db(rule_set, "dstNet", "Name", "Any", rule_name)                                                                                                                                  # If keyError occurs, write "Any" into DB
                            pass

                        src_ports = [ ]
                        try:
                            for i in rules["sourcePorts"]["literals"]:                                                                                                                                                                  # These are type literal. Which means they dont have an object associaited
                                try:
                                    dst_ports.append(i["protocol"] + "-" + i["port"])
                                except (KeyError, TypeError):
                                    pass
                        except (KeyError, TypeError):
                            pass

                        try:                                                                                                # Use comments for destination ports section
                            for i in rules["sourcePorts"]["objects"]:                                                      # Access the sourcePorts, object list of dictionaries, notice iteration
                                type = str(i["type"] + "s").lower()                                                         # Grab i[type], i is a dictionary and set it to lower. URI requirement
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])
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

                            src_port_list = [i for i in src_ports]                                                          # List can't be stored to db so we convert it to rules using join()
                            update_db(rule_set, "srcPort", "Name", ",".join(src_port_list), rule_name)                   # Call the update DB function, send name, column variables

                        except (KeyError, TypeError) as error:
                            update_db(rule_set, "srcPort", "Name", "Any", rule_name)                                     # If keyError occurs, write "Any" into DB
                            pass

                        dst_ports = [ ]
                        try:
                            for i in rules["destinationPorts"]["literals"]:
                                try:
                                    dst_ports.append(i["protocol"] + "-" + i["port"])
                                except (KeyError, TypeError):
                                    pass
                        except (KeyError, TypeError) as error:
                            pass

                        try:
                            for i in rules["destinationPorts"]["objects"]:

                                type = str(i["type"] + "s").lower()
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])
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
                            for i in rules["sourceZones"]["objects"]:                                                                                                                                                                                     # Access the sourcePorts, object list of dictionaries, notice iteration
                                type = str(i["type"] + "s").lower()                                                                                                                                                                                             # Grab i[type], i is a dictionary and set it to lower. URI requirement
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])
                                update_db(rule_set, "srcInt", "Name", get_object_value[0]["name"], rule_name)                                                                                                           # Call the update DB function, send name, column variables

                        except (KeyError, TypeError) as error:
                            update_db(rule_set, "srcInt", "Name", "Any", rule_name)                                                                                                                                                            # If keyError occurs, write "Any" into DB
                            pass

                        try:

                            for i in rules["destinationZones"]["objects"]:
                                type = str(i["type"] + "s").lower()
                                get_object_value = fmc.objects(self, fmc_access, type, i["id"])
                                update_db(rule_set, "dstInt", "Name",get_object_value[0]["name"], rule_name)

                        except (KeyError, TypeError) as error:
                            update_db(rule_set, "dstInt", "Name", "Any", rule_name)
                            pass

                        rule = rule + 1
                        auth_counter = auth_counter + 1
                        rule_num = rule_num + 1

                    except (KeyError, TypeError, IndexError) as error:
                        rule_num = rule_num + 1
                        errored_uri.append(path)
                        pass


    def objects(self, object, type, id):

        # Use the URI component recieved from main to build URI.
        # Convert the request to a dictionary and return it to the caller.
        # This process is done for every object. Remember, in the rule it gives us object name and ID, not values. Line 77

        path = "/api/fmc_config/v1/domain/" + self.domain_uuid + "/object/" + type + "/" + id + ""
        request = object.get(path, self.auth_key, self.refresh_key)
        nested_objects = []

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
            for i in request["objects"]:
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
            for objects in request["interfaces"]:
                try:
                    insert_object(request["id"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(objects["type"], objects["name"], objects["name"], objects["id"],))
                    mydb.commit()
                except KeyError:
                    pass
        except KeyError:
            pass

        try:
            for i in request["objects"]:

                obj_type = str(i["type"] + "s").lower()

                path = "/api/fmc_config/v1/domain/" + self.domain_uuid + "/object/" + obj_type + "/" + i["id"] + ""
                request = object.get(path, self.auth_key, self.refresh_key)
                nested_object = requests

                try:
                    insert_object(nested_object["id"])
                    c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?", (
                    nested_object["type"], nested_object["name"], nested_object["value"], nested_object["id"],))
                    mydb.commit()
                    nested_objects.append(nested_object["value"])
                except KeyError:
                    pass

        except KeyError:
            pass

        # Write any icmp objects to th DB if they aren't nested

        try:
            insert_object(request["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?",(request["type"], request["icmpType"], request["name"], request["id"],))
            mydb.commit()
        except KeyError as error:
            pass

        # Write any protocol/port objects to th DB if they aren't nested

        try:
            insert_object(request["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=?, protocol=? WHERE id=?", (request["type"], request["name"], request["port"], request["protocol"], request["id"],))
            mydb.commit()
        except KeyError:
            pass

        # Update the Object_Used table. Set column attributes to the values stored in the object dictionary

        try:
            insert_object(request["id"])
            c.execute("UPDATE Object_Used  SET type=?, name=?, value=? WHERE id=?", (request["type"], request["name"], request["value"], request["id"],))
            mydb.commit()
        except KeyError:
            pass

        cleanup_db()  # This will cleant duplcate entries from out DB. To reduce conditional code in the latter code.
        return request, nested_objects  # Return the object to the caller si ut can be update/stored in the database