Meraki Slim (a lighter version of what im current working on:)

This program allows you GET Meraki site data via Meraki API.

When you launch the program you will be requested to provide 2 thing:

1. API Key
2. Organization ID

NOTE* Two files are need. Please provide a file path int eh following variable:

1. network_file - line 22
2. meraki_file - line 23

Once these are entered the program will GET all site names, site IDs, and timezones. Option 7 in the main menu will all you to 
re-fetch without exiting This data will be written to a global dictionary.Once the latter is complete you will be brought to the
main menu, shown below:

1. View Content Filtering
2. View Network Port 
3. View Firewall Rules
4. View Subnets 
5. View VPN Settings 
6. Find Site ID 
7. Fetch the Cloud 

Every menu has will use GETs only, there is no POST in the program. when you access an option you will be presented with avaiable sites which
you can use TAB and Autocomplete for selection. Once site is selected you will be sent to another funtion with a similar name to the current with
the word "fetch" in the funtion name. Once the site data is "fetched/GET," it will be written to a global dictionary using the GEt TYPE, ports
firewall rules, etc. Once fetched, data will be read from the dictionarys and presented. Outputs below:



  HubID: N_584905001604781111 |   Hub Name: Hub1           | Default Route: False                
  HubID: N_584905001604782222 |   Hub Name: Hub2           | Default Route: False                
  HubID: N_584905001604783333 |   Hub Name: Hub3           | Default Route: False                
  HubID: N_584905001604784444 |   Hub Name: Hub4           | Default Route: False                


  Subnet: 192.168.1.0/24      |   VPN Advertised: True                 
  Subnet: 192.168.2.0/24      |   VPN Advertised: False   
  

 Vlan ID     Vlan Name              Gateway               Subnet
____________________________________________________________________________


    10         User                 192.168.1.1          192.168.1.0/24       
    20         WIFI                 192.168.2.1          192.168.2.0/24      

  

  Port         Enabled          Type        Allowed Vlans       Port Vlan        Access Policy        Drop Untagged
______________________________________________________________________________________________________________________


    3            True           access          ---                10                 open                 False               
    4            True           trunk           all                ---                ---                  True                
    5            True           trunk           all                ---                ---                  True                
    6            True           trunk           all                ---                ---                  True                
    7            True           trunk           all                ---                ---                  True                
    8            True           trunk           all                ---                ---                  True                
    9            True           trunk           all                ---                ---                  True                
    10           True           access          ---                20                 open                 False               
    11           True           trunk           all                ---                ---                  True                
    12           True           trunk           all                ---                ---                  True                
