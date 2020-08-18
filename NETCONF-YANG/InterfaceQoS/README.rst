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
              |
              Queue       ->  class-default        Premium+             Premium              Enhanced+            Enhanced             Default-Class        class-default       
              Class Rate  ->  15                   0                    0                    0                    0                    46                   0                   
              Class Pkts  ->  729447848167         270613935            0                    0                    227966               682983465477         46193540789         
              Class Bytes ->  2768282542           2600603              0                    0                    2781                 2734652966           31026192            
              Out Bytes   ->  729144560234         0                    0                    0                    0                    0                    729144560234        
              Out Pkts    ->  2767726474           0                    0                    0                    0                    0                    2767726474          
              Drop Bytes  ->  99880                0                    0                    0                    0                    0                    99880               
              Drop Pkts   ->  136762074            0                    0                    0                    0                    0                    136762074           
              WRED Pkts   ->  0                    0                    0                    0                    0                    0                    0                   
              WRED Bytes  ->  0                    0                    0                    0                    0                    0                    0                   
              |
              GigabitEthernet0/0/1
              Policy Direction: outbound
              Policy Name: 100-Meg
              |
              Queue       ->  class-default        Real-Time            Premium              Standard             Best-Effort          class-default       
              Class Rate  ->  337                  0                    0                    0                    337                  0                   
              Class Pkts  ->  302388449269         220845109            0                    0                    276006844295         26160759865         
              Class Bytes ->  415458227            2021838              0                    0                    395732303            17704086            
              Out Bytes   ->  302038878373         0                    0                    0                    0                    302038878373        
              Out Pkts    ->  414582275            0                    0                    0                    0                    414582275           
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
                |
                Queue       ->  class-default        Real-Time            Premium              Standard             Best-Effort          class-default       
                Class Rate  ->  337                  0                    0                    0                    337                  0                   
                Class Pkts  ->  302388449269         220845109            0                    0                    276006844295         26160759865         
                Class Bytes ->  415458227            2021838              0                    0                    395732303            17704086            
                Out Bytes   ->  302038878373         0                    0                    0                    0                    302038878373        
                Out Pkts    ->  414582275            0                    0                    0                    0                    414582275           
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
