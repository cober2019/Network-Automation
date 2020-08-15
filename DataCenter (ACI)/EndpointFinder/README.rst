Endpoint Finder
------------------
**Description:**
__________________

  Use Endpoint Finder to find endpoint your ACI fabric. Query via IP address or MAC to receive a detailed report of the EP location.


**Usage**
___________
  ***Querying by MAC provides more a more detailed report then by IP**

  **Find endpoint by IP address:** 

               >>> Reverse Lookup:      00:50:56:61:27:33
                   Tenant:              Storage
                   App Profile:         UCS
                   Endpoint Group:      Mangement
                   Learned From:        learned,vmm
                   Encapsulation:       vlan-2345
                   Reporting Leafs:     103, 104
                   
  **Find endpoint by MAC:** 

               >>> Reverse Lookup:      10.10.10.1
                   Tenant:              Storage
                   App Profile:         UCS
                   Endpoint Group:      management
                   Learned From:        learned,vmm
                   Encapsulation:       vlan-2345
                   Reporting Leafs:     104, 103
                   Paths:               192.168.1.10, 192.168.1.11, pod-1->103-104->Storage-Management

