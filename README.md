Project Description:

Utilizing NETCONF/YANG, this program allows for automation of network configurations. The goal was to build XML files within the program without having to use static XML payloads. Static payloads are an option and can be sent from the desired directory. Network Engineers should fit the program to their own needs as this program only shows the capabilities of what can be done with python and NETCONF/YANG.

How did i build this program, recomendations?

1. Use YANG EXPLORER to see how XML trees are strucutred
2. Send configurations via command line, then use the get-config to see how XML elements are tagged/structured and what  namepsaces are used etc. From this you will be able to build your program with configration options of your choice.
3. Learn Python (DISCLAIMER, IM NOT A PYTHON EXPERT)

Not all configuration options are included in the python code

Environment:

-Vendor Testing - Cisco

-Image: IOS XE 16.7.2

-Devices: Catalyst 3850 & ISR 4331

-Server: CentOS:Yang-Explorer

-Yang Model: Cisco-IOS-XE-native

User Dependencies:

1. For multi device configuration, reading from an xml files works fine. Create a excel and read device IPs from sheet using openpyxl.
2. Local directory to store dynamic XML files. The program will read and write from this directory.

Optional:

1. FTP server to download a copy of the inventory excel file

Please reach out to me if you have any questions:

Email - cober91130@gmail.com
LinkedIn - http://linkedin.com/in/chris-oberdalhoff-43292b56


