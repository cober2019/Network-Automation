Project Routing
==============
**Description**
--------------

  Project Routing is an open-source project which goal is to collect and store routing tabled by vendor and vendor table types. The tables are stored in two different ways.
  
  + Memorey, dictionary format
  + SqlLite3

**Contributions:**

  For contributions to the project please use the blueprint from Abstract.py file. Following the abstract methods will allow you to create code for a specific vendor.

**Status**
______

Under Developement

Routing Table Compatibility
___________

+ Nexus OS
+ Cisco IOS XE
+ ASA

**Usages**
___________

**Database Tool** 

View routing table from a local sqlite database. Credential entry is here or just skip credential input if your've previosly populated the  table. You can query the routing table using the following permameters

                    + Protocol
                    + Prefix
                    + Metric
                    + AD
                    + Outgoing Interface
                    + Tag

**Example Query (Prefix Lookup: )**

                    >>> VRF: global
                        Prefix: 10.10.10.0/24
                        Protocol: O
                        Admin-Distance: 110
                        Hop(s): 192.168.150.25, 192.168.150.21
                        Out-Interface(s): GigabitEthernet0/0/5, GigabitEthernet0/0/4
                        Metric(s): 41, 41
                        Tag: None
                        CDP neighbor(s): Iceland-Core01, Iceland-Core02
                        Total Routes: 1

**Usage w/out DB Tool** 

View data in a dictionary format, or formatted output from a dictionary. SQLlite databse is still created if class is initiated. You also can use this for conditional checks.

  **Initiate Class:**

    **IOS XE & Nexus**

          >>> getroutes = Routing(host="192.168.1.1", username="JoeSmo", password="HelpMe!")

    **ASA**

          >>> getroutes = Routing(host="192.168.1.1", username="JoeSmo", password="HelpMe!", enable="HelpMe!")


  **Print Routing Table Formatted:**

    **Nexus**

            >>> print(getroutes.vdc_routes_unpacked())

    **IOS XE & ASA**

            >>> print(getroutes.routes_unpacked())

  **Print Routing Table UnFormatted:**

    **Printing unformatted is more of a use case the this code. As mentioned above you can run conditional statments against the route table.
    Please view class method routes_unpacket() for IOS XE, and vdc_routes_unpacked() to view how to access the route dictionary.**

    **Nexus**

      Use property vdcroutes

           >>> getroutes.vdcroutes

    **IOS XE & ASA**

      Use property routing_instance

           >>> getroutes.routing_instance

    
