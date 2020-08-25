"""Helper class to create configuration using ios-xw-native YANG model"""

import xml.etree.cElementTree as xml


class Templates:
    """Helper methods to create class-maps using YNAG models"""

    def __init__(self, class_name, match_type):

        self.root = xml.Element("config")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.policy_element = xml.Element("policy")
        self.native_element.append(self.policy_element)
        self.class_element = xml.Element("class-map")
        self.class_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
        self.policy_element.append(self.class_element)
        self.class_input = class_name
        self.class_id = xml.SubElement(self.class_element, "name")
        self.class_id.text = self.class_input
        self.match_type = match_type
        self.prematch_element = xml.SubElement(self.class_element, "prematch")
        self.prematch_element.text = self.match_type
        self.match_element = xml.SubElement(self.class_element, "match")

    def dscp(self):
        """DSCP XML Configuration"""

        dscp = [str(i) for i in range(0, 63)]
        tags = ("af11", "af12", "af13", "af21", "af22", "af23", "af31", "af32", "af33", "af41", "af42", "af43", "cs1",
                "cs2", "cs3", "cs4", "cs5", "cs6", "cs7", "ef", "default")

        while True:
            try:
                print("CTRL + C to exit")
                value = input("Tag:  ")
                if value in tags or value in dscp:
                    match_1_element = xml.SubElement(self.match_element, "dscp")
                    match_1_element.text = value
                else:
                    print("Invalid Tag")
            except KeyboardInterrupt:
                break

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def access_group(self):
        """Access Group XML Configuration"""

        number = [str(i) for i in range(1, 2799)]
        selection = input("Name or value? ").lower()
        print("Valid Group, 1-2799\n")
        while True:
            try:
                print("CTRL + C to exit")
                value = input("Group:  ")
                match_1_element = xml.SubElement(self.match_element, "access-group")
                match_2_element = xml.SubElement(match_1_element, selection)
                match_2_element.text = value
            except KeyboardInterrupt:
                break

        return self.root


    def any(self):

        match_1_element = xml.SubElement(self.match_element, "any")

        return self.root


    def atm(self):
        """Not Supported"""

        match_1_element = xml.SubElement(self.match_element, "atm")
        match_1_element.text = "clp"

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def atm_vci(self):
        """Not Supported"""

        number = [str(i) for i in range(32, 65535)]
        match_1_element = xml.SubElement(self.match_element, "atm-vci")
        print("Valid Tag, 32-655354\n")
        while True:
            try:
                print("CTRL + C to exit")
                vci_num = input("vci num:  ")
                if vci_num in number:
                    match_1_element.text = vci_num
                else:
                    print("Invalid vci num")
            except KeyboardInterrupt:
                break

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def class_map(self):
        """Not supported"""

        class_map = input("Class-map:  ")
        match_1_element = xml.SubElement(self.match_element, "class-map")
        match_1_element.text = class_map

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def cos(self):
        """COS XML Configuration"""

        number = [str(i) for i in range(0, 7)]
        print("Valid Tag, 0-7\n")
        while True:
            try:
                print("CTRL + C to exit")
                tag_value = input("Tag:  ")
                if tag_value in number:
                    match_1_element = xml.SubElement(self.match_element, "cos")
                    match_1_element.text = tag_value
                else:
                    print("Invalid Tag")
            except KeyboardInterrupt:
                break

        return self.root


    def dest_address(self):
        """Not supported"""

        mac = input("MAC:  ")
        match_1_element = xml.SubElement(self.match_element, "destination-address")
        match_1_element.text = mac

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def discard_class(self):
        """Discard class XML Configuration"""

        number = [str(i) for i in range(0,7)]
        print("Valid Tag, 0-7\n")
        while True:
            try:
                print("CTRL + C to exit")
                discard = input("Class:  ")
                if discard in number:
                    match_1_element = xml.SubElement(self.match_element, "discard-class")
                    match_1_element.text = discard
                else:
                    print("Invalid Value")
            except KeyboardInterrupt:
                break

        return self.root


    def mpls(self):
        """MPLS Experimental XML Configuration"""

        number = [str(i) for i in range(0, 7)]
        match_1_element = xml.SubElement(self.match_element, "mpls")
        match_2_element = xml.SubElement(match_1_element, "experimental")
        print("Valid Tag, 0-7\n")

        while True:
            try:
                print("CTRL + C to exit")
                value = input("Value:  ")
                if value in number:
                    match_3_element = xml.SubElement(match_2_element, "topmost")
                    match_3_element.text = value
                else:
                    print("Invalid Tag")
            except KeyboardInterrupt:
                break

        return self.root


    def precedence(self):
        """IP Precedence Group XML Configuration"""

        number = [str(i) for i in range(0,7)]
        options = ("critical", "flash", "flash-override", "immediate", "internet", "network", "priority", "routine")
        print("Valid Tag, 0-7 or:\n")
        [print(i) for i in options]
        print("\n")
        while True:
            try:
                print("CTRL + C to exit")
                value = input("Precendence:  ")
                if value in number or value in options:
                    match_1_element = xml.SubElement(self.match_element, "precedence")
                    match_1_element.text = value
                else:
                    print("Invalid Tag")
            except KeyboardInterrupt:
                break

        return self.root


    def qos_group(self):
        """QoS Group XML Configuration"""

        number = [str(i) for i in range(0,99)]
        print("Valid Tag, 0-99\n")
        while True:
            try:
                print("CTRL + C to exit")
                value= input("Group:  ")
                if value in number:
                    match_1_element = xml.SubElement(self.match_element, "qos-group")
                    match_1_element.text = value
                else:
                    print("Invalid Group")
            except KeyboardInterrupt:
                break

        return self.root


    def src_address(self):
        """Not supported"""

        mac = input("MAC:  ")
        match_1_element = xml.SubElement(self.match_element, "source-address")
        match_1_element.text = mac

        config = xml.ElementTree(element=self.root)
        self.save_to_file(config)


    def vlan(self):
        """Vlans XML Configuration"""

        number = [str(i) for i in range(1,4094)]
        selection = input("Value or Inner? ").lower()
        print("Valid Tag, 1-4094\n")
        while True:
            try:
                print("CTRL + C to exit")
                tag_value = input("Tag:  ")
                if tag_value in number:
                    match_1_element = xml.SubElement(self.match_element, "vlan")
                    match_2_element = xml.SubElement(match_1_element, selection)
                    match_2_element.text = tag_value
                else:
                    print("Invalid Tag")
            except KeyboardInterrupt:
                break

        return self.root

    def protocol(self):
        """Protocols XML Configuration"""

        protocols = ('application-group',
                     'arp'
                         , 'attribute'
                         , 'bgp'
                         , 'bittorrent'
                         , 'bridge'
                         , 'cdp'
                         , 'cifs'
                         , 'citrix'
                         , 'clns'
                         , 'clns_es'
                         , 'clns_is'
                         , 'cmns'
                         , 'compressedtcp'
                         , 'cuseeme'
                         , 'dhcp'
                         , 'dht'
                         , 'directconnect'
                         , 'dns'
                         , 'edonkey'
                         , 'egp'
                         , 'eigrp'
                         , 'exchange'
                         , 'fasttrack'
                         , 'finger'
                         , 'ftp'
                         , 'gnutella'
                         , 'gopher'
                         , 'gre'
                         , 'http'
                         , 'http-local-net'
                         , 'https'
                         , 'icmp'
                         , 'imap'
                         , 'ip'
                         , 'ipinip'
                         , 'ipsec'
                         , 'ipv6'
                         , 'ipv6-icmp'
                         , 'irc'
                         , 'kazaa2'
                         , 'kerberos'
                         , 'l2tp'
                         , 'ldap'
                         , 'llc2'
                         , 'mgcp'
                         , 'ms-rpc'
                         , 'netbios'
                         , 'netshow'
                         , 'nfs'
                         , 'nntp'
                         , 'notes'
                         , 'novadigm'
                         , 'ntp'
                         , 'ospf'
                         , 'pad'
                         , 'pop3'
                         , 'pppoe'
                         , 'pppoe-discovery'
                         , 'pptp'
                         , 'printer'
                         , 'rip'
                         , 'rsrb'
                         , 'rsvp'
                         , 'rtcp'
                         , 'rtp'
                         , 'rtsp'
                         , 'secure-ftp'
                         , 'secure-http'
                         , 'secure-imap'
                         , 'secure-irc'
                         , 'secure-ldap'
                         , 'secure-nntp'
                         , 'secure-pop3'
                         , 'secure-telnet'
                         , 'sip'
                         , 'skinny'
                         , 'skype'
                         , 'smtp'
                         , 'snapshot'
                         , 'snmp'
                         , 'socks'
                         , 'sqlnet'
                         , 'sqlserver'
                         , 'ssh'
                         , 'ssl'
                         , 'stun-nat'
                         , 'sunrpc'
                         , 'syslog'
                         , 'telepresence-control'
                         , 'telnet'
                         , 'teredo-ipv6-tunneled'
                         , 'tftp'
                         , 'vdolive'
                         , 'winmx'
                         , 'xmpp-client'
                         , 'xwindows'
                         , " "
                         , " "
                         , " ")

        [print(' | '.join(protocols[i * 10:(i + 1) * 10])) for i in range(10)]
        print("\n")
        while True:
            try:
                protocol = input("Protocol:  ")
                if protocol in protocols:
                    match_1_element = xml.SubElement(self.match_element, "protocol")
                    match_2_element = xml.SubElement(match_1_element, "protocols-list")
                    match_3_element = xml.SubElement(match_2_element, "protocols")
                    match_3_element.text = protocol
                else:
                    print("Invalid protocol")
            except KeyboardInterrupt:
                break

        return self.root

    def ip(self):
        """Protocols XML Configuration"""

        options = ['dscp', 'precedence']
        [print(i) for i in options]
        print("\n")
        selection = input("Selection:  ").lower()

        while True:
            try:
                print("CTRL + C to exit")
                if selection in options and selection != "rtp":
                    protocol = input("Tag:  ")
                    match_1_element = xml.SubElement(self.match_element, "ip")
                    match_2_element = xml.SubElement(match_1_element, selection)
                    match_2_element.text = protocol
                else:
                    print("Invalid protocol")
            except KeyboardInterrupt:
                break

        return self.root