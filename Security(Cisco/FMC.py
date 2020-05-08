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



ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
username = input("Username: ")
password = input("Password: ")
fmc_ip = input("FMC IP: ")

uri = "https://" + fmc_ip + "/api/fmc_platform/v1/auth/generatetoken"

def objects(dom_uidd, type, id):

    # Use the URI component recieved from main to build URI. Time.sleep is used to slow the pace of get request (120 per minutes)
    # Convert the request to a dictionary and return it to the caller.
    # This process is done for every object. Remember, in the rule it gives us object name and ID, not values. Line 77

    time.sleep(1)
    uri = "https://" + fmc_ip + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/" + type + "/" + id + ""
    r = session.get(uri, verify=False, headers=headers, auth=(username, password))
    try:
        object = r.json()
    except json.JSONDecodeError as error:
        object = "Error"
        pass

    return object

if __name__ == '__main__':

    # POST credentials to FMC
    # Parse response for the next step of authentication which requires access/refresh tokens and Domain UUID
    # Create headers for your further request to the FMC

    session = requests.Session()
    r = session.post(uri, verify=False, auth=(username, password))
    get_access_token = r.headers["X-auth-access-token"]
    get_refresh_token = r.headers["X-auth-refresh-token"]
    domain_uuid = r.headers["DOMAIN_UUID"]
    headers = {"X-auth-access-token": get_access_token, "X-auth-refresh-token": get_refresh_token }

    # Request access policies from the FMC, or all rule sets the FMC has
    # Turn response into a dictionary  using .json
    # Get the the number of policies using "count" value

    uri = "https://" + fmc_ip + "/api/fmc_config/v1/domain/" + domain_uuid +"/policy/accesspolicies"
    r = session.get(uri, verify=False, headers=headers, auth=(username, password))
    access_pol = r.json()
    count = access_pol["paging"]["count"]

    # Now that we have all policies lets access them to see what rules are inside
    # Since we have "count" policies, we will use each policy ID obtained from acceess_pol dictionary. This id will be placed in the URI.
    # Make the request which gives us all access rules in the policy. We will create access_rule dictionary

    for i in range(0, count):

            print(access_pol["items"][i]["name"] +": " + access_pol["items"][i]["id"])
            uri = access_pol["items"][i]["links"]["self"] + "/accessrules?offset=1000&limit=1000"
            r = session.get(uri, verify=False, headers=headers, auth=(username, password))
            try:
                access_rule = r.json()
            except json.JSONDecodeError:
                break

    # Now that we have our access_rule dictionary, we will need to dig another layer into the rule. Why? Because FMC only give us object names, not object values
    # We will uses the range command to iterate through 1000 rules. You may not have tha many or more. Its an arbitrary number

            for rule in range(0,1000):
                try:

    # Using the self key/value in the the access_rule dict we can get the URI of the particular rule.
    # Once we've access the rule we will create another dictionary from the REST response. string() is the dictionary in this case


                    uri = access_rule["items"][rule]["links"]["self"]
                    r = session.get(uri, verify=False, headers=headers, auth=(username, password))
                    string = r.json()

                except (KeyError, json.JSONDecodeError):
                    continue
                except IndexError:
                    pass

    # Heres where we convert the object names to values. They key items are  needed for conversion are object types, object id, and domain UUID
    # They're all components of the URI which is needed to convert the objects

                try:
                    print("---------------------------------------------")
                    print("Access Rule: \n")

                    try:
                        print("Source Networks:\n")                                             # Repeat the following  destination networks (lines 117,126)
                        for i in string["sourceNetworks"]["objects"]:                           # Access the sourceNetwork, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                 # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(domain_uuid, type, i["id"])              # Call the get_object_value funtions and send required URI components
                            print(get_object_value["name"] + "-" + get_object_value["value"])   # Print return values, the returng value will be a dictionary

                        print("\n")
                    except (KeyError, TypeError) as error:                                      # You will recive a Keyerror if the rule is set to ANY. FMC does'nt return src - ANY
                        print("Any\n")                                                          # Print "Any"
                        pass

                    try:
                        print("Dest Networks:\n")
                        for i in string["destinationNetworks"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(domain_uuid, type, i["id"])
                            print(get_object_value["name"] + "-" + get_object_value["value"])
                        print("\n")
                    except (KeyError, TypeError) as error:
                        print("Any\n")
                        pass


                    try:
                        print("Src Ports:\n")                                                        # Repeat the following not for destination ports (lines 151,166)
                        for i in string["sourcePorts"]["objects"]:                                   # Access the sourcePorts, object list of dictionaries, notice iteration
                            type = str(i["type"] + "s").lower()                                      # Grab i[type], i is a dictionary and set it to lower. URI requirement
                            get_object_value = objects(domain_uuid, type, i["id"])                   # Call the get_object_value funtions and send reuqired URI components

                            try:
                                print(get_object_value["protocol"] + "-" + get_object_value["port"]) # Print return values, the returng value will be a dictionary
                            except KeyError:
                                pass

                            try:
                                for i in get_object_value["objects"]:                                # You may recive a Parent object with more nested ports. This will be another list of dictionaries
                                    print(i["name"] + "-" + str(i["port"]))                          # Print the i["name], i being  a dictionary within a list, and i[port]
                            except (KeyError, TypeError):
                                pass

                        print("\n")
                    except (KeyError, TypeError) as error:
                        print("Any\n")
                        pass

                    try:
                        print("Dest Ports:\n")
                        for i in string["destinationPorts"]["objects"]:
                            type = str(i["type"] + "s").lower()
                            get_object_value = objects(domain_uuid, type, i["id"])

                            try:
                                print(get_object_value["protocol"] + "-" + get_object_value["port"])
                            except KeyError:
                                pass

                            try:
                                for i in get_object_value["objects"]:
                                    print(i["name"] + "-" + str(i["port"]))
                            except (KeyError, TypeError):
                                pass

                        print("\n")
                    except (KeyError, TypeError) as error:
                        print("Any\n")
                        pass

                except (json.JSONDecodeError):
                    pass

                stop = input("stop")
