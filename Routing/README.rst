Cisco Routing
===============

Currently this program gets routing tables from Cisco XE, NXOS, and ASA devices. It then parses the data and prints the route details. 

Idea
-----

You can  call the routing table class directly from your program and run conditional statements if desired. For example code visit main.py

**Steps**

1. Create the object
2. Check to see if auth is True or if there is an object
3. Get the routing table
4. Call the class property to access the routing table. Data structure is list of lists

        >>> connection_obj = device_login(ip, username, password, enable)
        >>> if connection_obj[1] != False or connection_obj[0] is not None:
                table_obj = xe_routing.RoutingIos(connection_obj[0])
 
        >>> [print(", ".join(i)) for i in table_obj.route_table]
