NETCONF Interfaces
===============

Description:
-----------

**NETCONF Interfaces allows Network Engineers to view a wide range of data from a given interface:**

+ Interface policy/queueing statistics
+ Trunk Interfaces
+ Interface Input/Output
+ Interface Uptime
+ Interface Bandwidth Usage (Polled During Method Initiation)
+ Interface Status (up/down, admin up/down, phys address, speed, ip)

Usage:
------


        >>> import NetConfInterfaces.NetConfInterfaces as intconf

**Example 1 (Object Initialization/Login: )**

        >>> call_class = intconf.Netconf()
        >>> login = call_class.device_connect(host="192.168.1.1", username="JoeSmo", password="Help!")
        print(call_class.session)
        <ncclient.manager.Manager object at 0x00000157EBEC6BC8>

**Example 2 (Interface Usage: )**

        **Single Interface**

        >>> call_class.interface_usage(interface="GigabitEthernet0/0/1")
        {'GigabitEthernet0/0/1': {'Percent In': 0.01, 'Percent Out': 0.0}}

        **All Interfaces**

        >>> call_class.interfaces_usage()
        {'GigabitEthernet0': {'Percent In': 0.0, 'Percent Out': 0.0}, 'GigabitEthernet0/0/0': {'Percent In': 0.08, 'Percent Out': 0.04},
        'GigabitEthernet0/0/1': {'Percent In': 0.0, 'Percent Out': 0.0}, 'GigabitEthernet0/0/2': {'Percent In': 0.0, 'Percent Out': 0.0},
        'GigabitEthernet0/0/3': {'Percent In': 0.0, 'Percent Out': 0.0}, 'GigabitEthernet0/0/4': {'Percent In': 0.02, 'Percent Out': 0.01},
        'GigabitEthernet0/0/5': {'Percent In': 0.04, 'Percent Out': 0.01}, 'Loopback0': {'Percent In': 0.0, 'Percent Out': 0.0},
        'Port-channel1': {'Percent In': 0.0, 'Percent Out': 0.0}, 'TenGigabitEthernet0/0/0': {'Percent In': 0.0, 'Percent Out': 0.0},
        'TenGigabitEthernet0/0/1': {'Percent In': 0.0, 'Percent Out': 0.0}, 'Port-channel1.2050': {'Percent In': 0.0, 'Percent Out': 0.0}}

**Example 3 (Interface Uptime: )**

        >>> call_class.get_interface_uptime()
        {'GigabitEthernet0': datetime.timedelta(days=239, seconds=59170, microseconds=78401), 'GigabitEthernet0/0/0': datetime.timedelta(days=240, seconds=76022, microseconds=83749),
        'GigabitEthernet0/0/1': datetime.timedelta(days=64, seconds=15827, microseconds=82893), 'GigabitEthernet0/0/2': datetime.timedelta(days=214, seconds=84260, microseconds=83221),
        'GigabitEthernet0/0/3': datetime.timedelta(days=187, seconds=39201, microseconds=82855), 'GigabitEthernet0/0/4': datetime.timedelta(days=239, seconds=61452, microseconds=83318),
        'GigabitEthernet0/0/5': datetime.timedelta(days=238, seconds=69530, microseconds=82880), 'Loopback0': datetime.timedelta(days=240, seconds=76030, microseconds=83166),
        'Port-channel1': datetime.timedelta(days=187, seconds=39198, microseconds=83573), 'TenGigabitEthernet0/0/0': datetime.timedelta(days=240, seconds=76031, microseconds=82919),
        'TenGigabitEthernet0/0/1': datetime.timedelta(days=240, seconds=76030, microseconds=83293), 'Port-channel1.2050': datetime.timedelta(days=187, seconds=39198, microseconds=83746)}

**Example 4 (Get Trunks: )**

        >>> call_class.get_trunks()
        {'GigabitEthernet1/0/5': '123,201,234,455,566,10,16,17,19,20,22,30,35,45,50,51,56,57,58,60,60,70,71',
        'GigabitEthernet1/0/6': '123,201,234,455,566,10,16,17,19,20,22,30,35,45,50,51,56,57,58,60,60,70,71'}

**Example 5 (Get Interfaces: )**

        >>> call_class.get_interfaces()
        {'GigabitEthernet0': {'admin-status': 'up', 'oper-status': 'up', 'speed': '1024000000', 'last-change': '2019-10-22T05:27:29.000439+00:00', 'phys-address': 'a0:e0:af:e9:f0:a0'},
        'GigabitEthernet0/0/0': {'admin-status': 'up', 'oper-status': 'up', 'speed': '1024000000', 'last-change': '2019-10-21T00:46:37.000096+00:00', 'phys-address': 'a0:e0:af:e9:f0:82'},
        'GigabitEthernet0/0/1': {'admin-status': 'up', 'oper-status': 'up', 'speed': '1024000000', 'last-change': '2020-04-14T17:29:52.000952+00:00', 'phys-address': 'a0:e0:af:e9:f0:83'},
        'GigabitEthernet0/0/2': {'admin-status': 'up', 'oper-status': 'up', 'speed': '1024000000', 'last-change': '2019-11-15T22:29:19.000624+00:00', 'phys-address': 'a0:e0:af:e9:f0:c0'},
        'Vlan99': {'admin-status': 'down', 'oper-status': 'lower-layer-down', 'speed': '1024000000', 'last-change': '2020-04-06T20:30:47.000692+00:00', 'phys-address': 'ec:1d:8b:54:39:5d', 'ip': '99.99.99.3 255.255.255.0'},
        'Port-channel10': {'admin-status': 'up', 'oper-status': 'up', 'speed': '2048000000', 'last-change': '2020-04-16T23:05:34.00078+00:00', 'phys-address': 'ec:1d:8b:54:39:02'},
        'Port-channel20': {'admin-status': 'up', 'oper-status': 'up', 'speed': '2048000000', 'last-change': '2020-04-16T23:05:42.000751+00:00', 'phys-address': 'ec:1d:8b:54:39:04'},
        'Port-channel30': {'admin-status': 'down', 'oper-status': 'lower-layer-down', 'speed': '102400000', 'last-change': '2020-04-02T23:21:30.000529+00:00', 'phys-address': '00:00:00:00:00:00'},
        'TenGigabitEthernet1/1/1': {'admin-status': 'down', 'oper-status': 'lower-layer-down', 'speed': '1650065408', 'last-change': '2019-10-21T17:51:04.000301+00:00', 'phys-address': 'ec:1d:8b:54:39:35'}

**Example 6 (Get Interface Stats: )**

        >>> call_class.get_interface_stats()
        {<class 'type'>: {'GigabitEthernet0': {'In-octets': '13573007855', 'In-unicast': '128755053', 'In-multicast': '18137634', 'In-discards': '0', 'In-errors': '0', 'In-unknown-protocol': '0', 'Out-octets': '104788195', 'Out-unicast': '229684', 'Out-multicast': '0', 'Out-discards': '0', 'Out-errors': '0', 'Out-broad-errors': '0', 'Out-multi-errors': '0'},
        'GigabitEthernet0/0/0': {'In-octets': '0', 'In-unicast': '0', 'In-multicast': '0', 'In-discards': '0', 'In-errors': '0', 'In-unknown-protocol': '0', 'Out-octets': '0', 'Out-unicast': '0', 'Out-multicast': '0', 'Out-discards': '0', 'Out-errors': '0', 'Out-broad-errors': '0', 'Out-multi-errors': '0'},
        'GigabitEthernet0/0/1': {'In-octets': '0', 'In-unicast': '0', 'In-multicast': '0', 'In-discards': '0', 'In-errors': '0', 'In-unknown-protocol': '0', 'Out-octets': '0', 'Out-unicast': '0', 'Out-multicast': '0', 'Out-discards': '0', 'Out-errors': '0', 'Out-broad-errors': '0', 'Out-multi-errors': '0'}

**Example 6 (Get QoS Stats: )**

        >>> call_class.get_interface_qos(interface="GigabitEthernet0/0/0")
        defaultdict(<class 'list'>, {'Shape-100-Meg': [{'policy_direction': 'outbound', 'class_name': 'class-default', 'parent_policy': 'Shape-100-Meg class-default', 'class_bytes': '469434337785', 'class_pkts': '2075264740', 'class_rate': '84', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '69534', 'drop_bytes': '95303074'},
        {'policy_direction': 'outbound', 'class_name': 'class-default', 'parent_policy': 'Shape-100-Meg class-default', 'class_bytes': '469434337785', 'class_pkts': '2075264740', 'class_rate': '84', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '69534', 'drop_bytes': '95303074'},
        {'class_name': 'Premium+', 'parent_policy': 'Shape-100-Meg class-default Child-Policy Premium+', 'class_bytes': '179772900', 'class_pkts': '1689356', 'class_rate': '0', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '0', 'drop_bytes': '0'},
        {'class_name': 'Premium', 'parent_policy': 'Shape-100-Meg class-default Child-Policy Premium', 'class_bytes': '0', 'class_pkts': '0', 'class_rate': '0', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '0', 'drop_bytes': '0'},
        {'class_name': 'Enhanced+', 'parent_policy': 'Shape-100-Meg class-default Child-Policy Enhanced+', 'class_bytes': '0', 'class_pkts': '0', 'class_rate': '0', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '0', 'drop_bytes': '0'},
        {'class_name': 'Enhanced', 'parent_policy': 'Shape-100-Meg class-default Child-Policy Enhanced', 'class_bytes': '0', 'class_pkts': '0', 'class_rate': '0', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '0', 'drop_bytes': '0'},
        {'class_name': 'Default-Class', 'parent_policy': 'Shape-100-Meg class-default Child-Policy Default-Class', 'class_bytes': '438654809568', 'class_pkts': '2053037519', 'class_rate': '591', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '0', 'drop_bytes': '0'},
        {'class_name': 'class-default', 'parent_policy': 'Shape-100-Meg class-default Child-Policy class-default', 'class_bytes': '30599755317', 'class_pkts': '20537865', 'class_rate': '608', 'queue_size_pkts': '0', 'queue_size_bytes': '0', 'drop_pkts': '69534', 'drop_bytes': '95303074'}]})



