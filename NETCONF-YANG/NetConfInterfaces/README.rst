NETCONF Interfaces
==========

**Supported YANG Models**

+ ietf-interfaces
+ Cisco-IOS-XE-native

Description:
-----------


**NETCONF Interfaces allows Network Engineers to view a wide range of data from a given interface:**

+ Interface policy/queueing statistics
+ Trunk Interfaces
+ Interface Input/Output
+ Interface Uptime
+ Interface Bandwidth Usage (Polled During Method Initiation)
+ Interface Status (up/down, admin up/down, phys address, speed, ip)

**Example 3 (Interface Uptime: )**

        >>> get_interface_uptime(username="cisco", password="cisco", host="192.168.1.1", select_int="TenGigabitEthernet0/0/1")
            TenGigabitEthernet0/0/1: 2019-10-21T00:46:29.000162+00:00
        >>> get_interface_uptime(username="cisco", password="cisco", host="192.168.1.1")
                TenGigabitEthernet0/0/0: 2019-10-21T00:46:29.000537+00:00
                TenGigabitEthernet0/0/1: 2019-10-21T00:46:29.000554+00:00
                GigabitEthernet0/0/0: 2019-10-21T00:46:37.000328+00:00
                GigabitEthernet0/0/1: 2020-04-14T17:29:52.000753+00:00
                GigabitEthernet0/0/2: 2019-11-15T22:29:19.000889+00:00
                GigabitEthernet0/0/3: 2019-12-13T11:00:19.000642+00:00
                GigabitEthernet0/0/4: 2019-10-22T04:49:27.000573+00:00
                GigabitEthernet0/0/5: 2019-10-23T02:34:50.000401+00:00
                GigabitEthernet0: 2019-10-22T05:27:29.000183+00:00
                Loopback0: 2019-10-21T00:46:29.000507+00:00
                Port-channel1: 2019-12-13T11:00:21.000491+00:00
                Port-channel1.2050: 2019-12-13T11:00:21.000491+00:00
                Control Plane: 2019-10-21T00:46:24.000734+00:00

**Example 4 (Get Trunks: )**

        >>> get_trunk_ports(username="cisco", password="cisco", host="192.168.1.1")
                GigabitEthernet1/0/15
                Allowed Vlans: 566
                GigabitEthernet1/0/3
                Allowed Vlans: 10-17,19,20,22,30,35,45,50,51,56,58,60,66,70,71
                GigabitEthernet1/0/4
                Allowed Vlans: 10-17,19,20,22,30,35,45,50,51,56,58,60,66,70,71

**Example 5 (Get Interfaces: )**

        All Interfaces:

        >>> get_interface_stats(username="cisco", password="cisco", host="192.168.1.1")
                Vlan17
                Admin: up
                Operational: up
                Speed: 1024000000
                Last Change: 2020-04-07T21:56:10.000244+00:00
                MAC: 6c:dd:30:54:28:e0
                In Octets: 461845192
                In Unicast: 4676854
                In Multicast: 0
                In Discards: 0
                In Errors: 0
                Protocol Drops: 0
                Out Octets: 8979660
                Out Unicast: 149661
                Out Multicast: 0
                Out Discards: 0
                Out Errors: 0
                Out Boradcast: 0
                Out Multicast: 0

        >>>  get_interface_uptime(username="cisco", password="cisco", host="192.168.1.1", select_int="TenGigabitEthernet0/0/1")
                TenGigabitEthernet0/0/1
                Admin: down
                Operational: down
                Speed: 1650065408
                Last Change: 2019-10-21T00:46:29.000514+00:00
                MAC: a0:e0:af:e9:f0:81
                In Octets: 0
                In Unicast: 0
                In Multicast: 0
                In Discards: 0
                In Errors: 0
                Protocol Drops: 0
                Out Octets: 0
                Out Unicast: 0
                Out Multicast: 0
                Out Discards: 0
                Out Errors: 0
                Out Boradcast: 0
                Out Multicast: 0


**Example 7 (Get VLAN Access Ports: )**

        >>> get_access_ports(username="cisco", password="cisco", host="192.168.1.1")
                GigabitEthernet1/0/1
                Vlan: 10
                GigabitEthernet1/0/2
                Vlan: Native
        
**Example 8 (Interface up/down: )**

        >>> get_int_up_down(username="cisco", password="cisco", host="192.168.1.1")
                GigabitEthernet 0 is up
                GigabitEthernet 0/0/0 is up
                GigabitEthernet 0/0/1 is up
                GigabitEthernet 0/0/2 is up
                GigabitEthernet 0/0/3 is up
                GigabitEthernet 0/0/4 is up
                GigabitEthernet 0/0/5 is up
                Loopback 0 is up
                Port-channel 1 is up
                TenGigabitEthernet 0/0/0 is down
                TenGigabitEthernet 0/0/1 is down
                Port-channel-subinterface None is up

**Example 9 (Get IP Interfaces w/HSRP: )**

        >>> get_ip_interfaces(username="cisco", password="cisco", host="192.168.1.1")
                Vlan45
                IP: 10.10.45.2 255.255.255.0
                Priority: 110
                Group: 100
                Standby Address: 10.10.45.1
                Vlan50
                IP: 10.10.50.2 255.255.255.0
                Priority: 110
                Group: 100
                Standby Address: 10.10.50.1
                Vlan51
                IP: 10.10.51.2 255.255.255.0
                Priority: 110
                Group: 100
                Standby Address: 10.10.51.1
        
