Interface QoS
-------------

Description:
============

  **Interfaces QoS uses IETF YANG model to retrive interface stats via NETCONFIG. You can view a single interface, all interfaces or do a simple check to see if any policies are       assigned**
  
Usage
========

    **View All Interfaces:**
  
          >>> get_interfaces(username="admin", password="cisco", host="192.168.1.1")
              GigabitEthernet0/0/0
              Policy Direction: outbound
              Policy Name: 100-Meg
              Queue      ->  class-default        Premium+             Premium              Enhanced+            Enhanced             Default-Class        class-default       
              Bytes In   ->  727815236947         269935401            0                    0                    227966               681353194177         46191879403         
              Bytes Out  ->  2753352918           2589756              0                    0                    2781                 2719738929           31021452            
              Drop Bytes ->  99880                0                    0                    0                    0                    0                    99880               
              Drop Pkts  ->  136762074            0                    0                    0                    0                    0                    136762074           
              GigabitEthernet0/0/1
              Policy Direction: outbound
              Policy Name: 100-Meg
              Queue      ->  class-default        Real-Time            Premium              Standard             Best-Effort          class-default       
              Bytes In   ->  294355392709         216179955            0                    0                    268845227885         25293984869         
              Bytes Out  ->  406206744            1982138              0                    0                    387098095            17126511            
              Drop Bytes ->  416159               0                    0                    0                    0                    416159              
              Drop Pkts  ->  177878082            0                    0                    0                    0                    177878082           

  **View Single Interfaces:**
  
           >>>  get_interfaces(username="admin", password="cisco#", host="192.168.1.1", interface="GigabitEthernet0/0/0")
                GigabitEthernet0/0/0
                Policy Direction: outbound
                Policy Name: 100-Meg
                Queue      ->  class-default        Premium+             Premium              Enhanced+            Enhanced             Default-Class        class-default       
                Bytes In   ->  727815236947         269935401            0                    0                    227966               681353194177         46191879403         
                Bytes Out  ->  2753352918           2589756              0                    0                    2781                 2719738929           31021452            
                Drop Bytes ->  99880                0                    0                    0                    0                    0                    99880               
                Drop Pkts  ->  136762074            0                    0                    0                    0                    0                    136762074       

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
