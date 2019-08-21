Project Description:

Utilizing NETCONF/YANG, this program allows for automation of network configurations. The goal was to build XML files within the program without having to use static XML payloads. Static payloads are an option and can be sent from the desired directory. Network Engineers should fit the program to their own needs as this program only shows the capabilities of what can be done with python and NETCONF/YANG.

Configurable Options:

1:OSPF - Add/Remove OSPF Process

2:SNMPv2 Add/Remove SNMPv2 communities/ACLs

3:Credential - Add/Remove local crdentials

4:Interface - Add/Remove interfaces

5:DMVPN - Add NHRP/OSPF to tunnel interfaces

6:QoS - Add Class-maps/Policy-Maps/Interface Service-Policies

7.TACACS - Add/Delete/Modify

8.Prefix-List - Add/Delete 

9.Device Admin - View capabilites/Send configuration (dynamix XML payload or static if desired)or View configs

10:FTP Inventory - Download Inventory Files

How did i build this program, recomendations?

1. Use YANG EXPLORER to see how XML trees are strucutred
2. Send configurations via command line, then use the get-config to see how XML elements are tagged/structured and what  namepsaces are used etc. From this you will be able to build your program with configration options of your choice Ex. What do you want to automate, Policy-Maps: 

3 Learn Python (DISCLAIMER, IM NOT A PYTHON EXPERT)

Not all elements below have to be included in the python code. I can remove policing if i dont intend to uses that option. In the example below I've given an option to shape or police.


Program output for nested policy-map with shaping. The python code can be viewed on the qos_configuration function.

-<config>
-	<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
-		<policy>
			<policy-map xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-policy">
				<name>parentpolicy</name>
				-	<class>
						<name>class-default</name> <-------- class-map to use
						<action-list>
							<action-type>police</action-type> <-------  police or shape? 
							<police-target-bitrate>
								<police>
									<bit-rate>15000</bit-rate> <------------ bit rate
								</police>
							</police-target-bitrate>
						</action-list>
						<action-list>
							<action-type>service-policy</action-type>
							<service-policy>ChildPolicy</service-policy> <-------- Attach a child policy
						</action-list>
					</class>
			</policy-map>
		</policy>
	</native>
</config>



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


