Project Routing
==============
**Description**
--------------

  Project Routing is an open-source project which goal is to collect and store routing tabled by vendor and vendor table types. All routes are stored in a local SQL db
  using sqllite3 or using the DB tool you can export routes to an excel sheet.
  

**Contributions:**

  For contributions to the project please use the blueprint from Abstract.py file. Following the abstract methods will allow you to create code for a specific vendor.

Routing Table Compatibility
___________

+ Nexus OS
+ Cisco IOS XE
+ ASA

**Usages**
___________

**Database Tool** 

Get and view routing tables from a local sqlite database. Credential entry is here or just skip credential input if you've previosly populated the table. You can query the routing table using the following permameters

When loading the tool you will see:
  
  **Database populated? Press enter to skip. Enter any other key to populate new table.**
      Press enter if your routing table has been populated or input any key and press enter to populate a new table.
**You can query the table for the following parameters:**
  
  
                    + Protocol
                    + Prefix (Example: 192.168.1.0/24, 192.180, or 192.168.1.0)
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
                        Total Routes: 1
                        
                    >>> VDC: DC-OTV
                        VRF: default
                        Prefix: 192.168.1.0/24
                        Protocol: ospf-1,type-2
                        Admin-Distance: 110
                        Hop(s): 192.168.1.150, 192.168.1.151
                        Out-Interface(s): Po1, Po1
                        Metric(s): 500, 500
                        Tag: None
                        Age: 2w4d, 2w4d
                        
                    >>> Context: None
                        Prefix: 192.168.1.0 255.255.255.0
                        Protocol: O E2
                        Admin-Distance: 110
                        Hop(s): 192.168.5.13, 192.168.5.14
                        Out-Interface(s): internal-trusted, internal-trusted
                        Metric(s): 500, 500
                        Tag: None
                        Age: 2w4d, 2w4d


**Export Routes to Excel:**
                  
                  >>> DB_Query Tool
                      |
                      Table: Routing_IOS_XE
                      |
                      1. Search by protocol
                      2. Search by prefix
                      3. Search by metric
                      4. Search by AD
                      5. Search by Interface
                      6. Search by Tag
                      7. Full Table
                      **8. Export to Excel** <-----Option (Files is saved to Database folder in ProjectRouting directory)
              

    
