NETCONF VLANS
_____________

Description
==========

  **NETCONF vlans allows you to view, add, and delete vlans from a cisco device. Please be aware that this program does modify
  configurations by getting current vlans with Netmiko, and re-applying them via YANG modeling. This is done for YANG model/configuration
  template consistency** 
  
Usage
=======

  **The program uses a local DB to sync vlans between DB and device, vise versa for every device instance. Configuration menu is as follows:**
  
              >>> 1. Add new vlan via DB
                  2. Add new vlan directly to router
                  3. Update Vlan From Database
                  4. Update Vlan From Router
                  5. Delete Vlan From Router
                  6. Delete Vlan From DB
                  7. View DB Vlans
                  8. Credentials
