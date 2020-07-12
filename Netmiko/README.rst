Routing Tables
==============
Description
--------------

Using Netmiko, this code gets a device routing table and converts it to dictionary format. The goal is to allow you to run your code against the
routing as a condition. In turn, it will improve the reliability of your deployment. 

Status
______

Under Developement

Depedency Modules
__________

+ netmiko
+ re
+ collections
+ time

Routing Table Compatibility
___________

+ Nexus OS
+ Cisco IOS XE


Usage
__________

**Initiate Class:**
  
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
    
    
