Project Description:

Utilizing NETCONF/YANG, this program allows for automation of network configurations. By building XML files via the program, there is no need to create static payloads. Although this program prevents static payloads, the configurable options within the program are limited. An Engineer would have to fit the program to their needs using this program as an expample to do so.

ENVIRNOMENT:

-Vendor Testing - Cisco

-Image: IOS XE 16.7.2

-Devices: Catalyst 3850 & ISR 4331

-Server: CentOS:Yang-Explorer

-Yang Model: Cisco-IOS-XE-native

User Dependencies:

1. For multi device configuration, reading from an xml files works fine. Create a excel and read device IPs from sheet using xlrd.
2. Local directory to store dynamic XML files. The program will read and write from this directory.

Optional:

1. FTP server to download a copy of the inventory excel file


