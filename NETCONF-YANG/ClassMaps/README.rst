ClassMaps
============

Description
------------
  **View, build, and send class-map configuration via NETCONF/YANG. YANG Model: CISCO-IOS-XE-Native. *NOTE Most configuration match options were avaiable and some did not
  reflect in the xml configuration**
  
Usage
-------

 **Tested: OS: IOS-XE (16.07.02, 16.09.04, 16.06.01)  ------>**
 **Device Models: Cat 3850, ISR 4331, ASR1000-X**

**Main Menu:**

          >>> NETCONF QoS using ios-xe-native YANG model
              1. Create Classmaps
              2. View Classmaps
              3. Send Config
              Selection:

**View Class-maps:**

          >>>     Class: TEST
                  Prematch: match-all
                     Match: Any
               AccGrp(int): 20
              AccGrp(name): Tets
             Discard-class: 1, 3
                   IP Dscp: ef
             IP Precedence: 1, 5, 6
                      MPLS: 5
                 Protocols: ssh, tftp
              SecGrp(dest): 12
              InnerVlan(s): 10, 20, 30
                   Vlan(s): 10

**Build Config:**

              >>> Cass-map name: Test
                  Match Type (match-any/all): match-any
                  |
                  access-group
                  any
                  cos
                  discard_class
                  dscp
                  group_object
                  input_interface
                  ip
                  mpls
                  not
                  packet
                  precedence
                  protocol
                  qos_group
                  security_group
                  vlan
                  |
                  Match: cos
                  Valid Tag, 0-7
                  |
                  CTRL + C to exit
                  |
                  Tag: 5
                  Tag: <- Use CTRL + C to exit loop after desire tags are enetered

**Send Config: Config file is stored in local directory**

            >>> Configuration Files:
                ClassMaps.xml   <- Newly created config file
                Selection: ClassMaps.xml
