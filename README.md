Project Description:

This program utilizes NETCONF/YANG to configure network devices. I initailly started the program using the static XML payloads. After a while i found this very time consuming to change payload attribures, adding/removing elements, and changing the python payload code to what element/attributes I wanted to use. This program dynamiclly creats XML payloads and saves them to file. The program then reads the file and send the payload to the devices(s).The program also uses the dynamix XML files to delete configuration as well. As of now the program only offers a few options for configuration but shows the potential of what python and  NETCONF/YANG can do together.

I hope to be updating this program a few times a week with new configurations options. Please give me feedback and provided any addtions you would like to the program

Python Modules:

  ncclient, 
  xlrd, 
  xml.etree.ElementTree, 
  xmltodict, 
  ncclient.operations, 

ENVIRNOMENT:

-Vendor Testing - Cisco

-Image: IOS XE 16.7.2

-Devices: Catalyst 3850 & ISR 4331

-Server: CentOS:Yang-Explorer

-Yang Model: Cisco-IOS-XE-native

User Dependencies:

1. For multi device configuration, reading from an xml files works fine. Create a excel and read device IPs from sheet using xlrd.
2. Local directory to store dynamic XML files. The program will read and write from this directory.


