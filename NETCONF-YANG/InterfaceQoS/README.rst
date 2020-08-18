Interface QoS
-------------

Description:
============

  **Interfaces QoS uses IETF YANG model to retrieve interface stats via NETCONF. You can view a single interface, all interfaces or do a simple check to see if any policies are assigned**
  
Usage
========
 ***WRED stats pull zero for Cisco even if there is drops**
 
    **View All Interfaces:** 
  
          >>> get_interfaces(username="admin", password="cisco", host="192.168.1.1")
              |
              GigabitEthernet0/0/0
              Policy Direction: outbound
              Policy Name: 100-Meg-l3
              Queue       ->  class-default        Premium+             Premium              Enhanced+            Enhanced             Default-Class        class-default       
              Class Rate  ->  16                   0                    0                    0                    0                    75                   0                   
              Bytes In    ->  729432223476         270602676            0                    0                    227966               682967879363         46193513471         
              Pkts In     ->  2768188433           2600423              0                    0                    2781                 2734559115           31026114            
              Drop Bytes  ->  99880                0                    0                    0                    0                    0                    99880               
              Drop Pkts   ->  136762074            0                    0                    0                    0                    0                    136762074           
              WRED Pkts   ->  0                    0                    0                    0                    0                    0                    0                   
              WRED Bytes  ->  0                    0                    0                    0                    0                    0                    0     
              |
              GigabitEthernet0/0/1
              Policy Direction: outbound
              Policy Name: 100-Meg
              Queue       ->  class-default        Real-Time            Premium              Standard             Best-Effort          class-default       
              Class Rate  ->  422                  0                    0                    0                    421                  0                   
              Bytes In    ->  302277853641         220816243            0                    0                    275896305045         26160732353         
              Pkts In     ->  415323436            2021465              0                    0                    395597965            17704006            
              Drop Bytes  ->  418798               0                    0                    0                    0                    418798              
              Drop Pkts   ->  181826195            0                    0                    0                    0                    181826195           
              WRED Pkts   ->  0                    0                    0                    0                    0                    0                   
              WRED Bytes  ->  0                    0                    0                    0                    0                    0     

  **View Single Interfaces:**
  
           >>>  get_interfaces(username="admin", password="cisco", host="192.168.1.1", interface="GigabitEthernet0/0/0")
                |
                GigabitEthernet0/0/1
                Policy Direction: outbound
                Policy Name: 100-Meg
                Queue       ->  class-default        Real-Time            Premium              Standard             Best-Effort          class-default       
                Class Rate  ->  422                  0                    0                    0                    421                  0                   
                Bytes In    ->  302277853641         220816243            0                    0                    275896305045         26160732353         
                Pkts In     ->  415323436            2021465              0                    0                    395597965            17704006            
                Drop Bytes  ->  418798               0                    0                    0                    0                    418798              
                Drop Pkts   ->  181826195            0                    0                    0                    0                    181826195           
                WRED Pkts   ->  0                    0                    0                    0                    0                    0                   
                WRED Bytes  ->  0                    0                    0                    0                    0                    0     
                
  **Check Interfaces For Assigned Policies:**

        >>> has_qos(username="admin", password="cisco", host="192.168.1.1")
            TenGigabitEthernet0/0/0
            Qos Policy Assigned: Not Assigned
            TenGigabitEthernet0/0/1
            Qos Policy Assigned: Not Assigned
            GigabitEthernet0/0/0
            Qos Policy Assigned: Assign->Policy Name: 100-Meg
            GigabitEthernet0/0/1
            Qos Policy Assigned: Assign->Policy Name: 100-Meg
