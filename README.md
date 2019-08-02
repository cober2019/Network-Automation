Project Description:

Utilizing NETCONF/YANG, provide automation of configurations to network devices. In an effort to avoid assigning variables with values of static XML configuration payload,
this programs dynamiclly creatse XML files depending on the disired configuration i.e. SNMP, User credential etc. The program also allow the deltetion on confugration with dynamic
XML creation example: "What user do you want to delete?" 'user.'

Python Modules:

ncclient
xlrd
xml.etree.ElementTree
xmltodict
ncclient.operations

Enviroment:

Vendor Testing - Cisco
Cisco Image: IOS XE 16.7.2
Devices: Catalyst 3850 & ISR 4331
Server: CentOS:Yang-Explorer
Yang Model: Cisco-IOS-XE-native

User Dependencies:

1.For multi device configuration, reading from an xml files works fine. Create a excel and read device IPs from sheet using xlrd
2.Local directory to store XML dynamic XML files. The program will read and write from this directory.

Known Issues:

1.Program errors when viewing config if config on has only one item to view.Example. If one username exist on device, program will error, or one SNMPv2 community program will error etc.
