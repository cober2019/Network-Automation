try:
    import  ipaddress
except ImportError:
    pass
try:
    import  re
except ImportError:
    pass
try:
    import requests
except ImportError:
    pass
try:
    import lxml.etree as ET
except ImportError:
    pass
try:
    import warnings
except ImportError:
    pass
try:
    import collections
except ImportError:
    pass
try:
    import FindEncap
except ImportError:
    pass

get_file = "C:\Python\ACI\Get_ACI.xml"
headers = {'content-type': 'text/xml'}
vlan_dict = collections.defaultdict(list)
policies_dict = collections.defaultdict(list)
username = " "
password = " "

class aci_gets():

    def vlan_pools(session, apic):

        uri = "https://" + apic + "/api/node/mo/uni/infra.xml?query-target=subtree&target-subtree-class=fvnsVlanInstP&target-subtree-class=fvnsEncapBlk&query-target=subtree&rsp-subtree=full&rsp-subtree-class=tagAliasInst"

        r_1 = session.get(uri, verify=False, headers=headers)
        aci_gets.file_operation_1(r_1)  # Write xml repsonse to file, carry r_1 to funtion - Line 238

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')  # get XML tree root and iterate through XML elements. Find attributes, store to variables Line 133-138
        root = tree.getroot()
        for fvnsEncapBlk in root.iter("fvnsEncapBlk"):
            vlan_pool_array = [ ]
            if "vxlan" in fvnsEncapBlk.get("from"):
                continue
            else:
                vlan_pool_array.append(fvnsEncapBlk.get("from"))
                vlan_pool_array.append(fvnsEncapBlk.get("to"))
                dn = fvnsEncapBlk.get("dn")
                parse_dn = re.search(r'(?<=vlanns-\[).*?(?=]-[a-z])', dn)
                vlans = aci_gets.extract_vlan_ranges(vlan_pool_array)
                vlan_dict[parse_dn[0]].append(vlans)

    def phys_domains(session, apic):

        uri = "https://" + apic + "/api/node/mo/uni.xml?query-target=subtree&target-subtree-class=physDomP&target-subtree-class=infraRsVlanNs,infraRtDomP&query-target=subtree"
        headers = {'content-type': 'text/xml'}

        r_1 = session.get(uri, verify=False, headers=headers)
        aci_gets.file_operation_1(r_1)  # Write xml repsonse to file, carry r_1 to funtion - Line 238

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')  # get XML tree root and iterate through XML elements. Find attributes, store to variables Line 133-138
        root = tree.getroot()

        for infraRtDomP in root.iter("infraRtDomP"):
            string = infraRtDomP.get("dn")
            if re.findall(r'phys-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                phys_dom = re.findall(r'(?<=phys-).*(?=/rt)', string)
                policies_dict["AAEP " + aaeps[0]].append(phys_dom[0])
            elif re.findall(r'l3dom-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                l3_dom = re.findall(r'(?<=l3dom-).*(?=/rt)', string)
                policies_dict["AAEP " + aaeps[0]].append(l3_dom[0])
            elif re.findall(r'vmmp-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                vmm_dom = re.findall(r'(?<=vmmp-).*(?=/rt)', string)
                policies_dict["AAEP " + aaeps[0]].append(vmm_dom[0])
            else:
                continue

        for infraRsVlanNs in root.iter("infraRsVlanNs"):

            vl_pool_dn = infraRsVlanNs.get("tDn")
            vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
            phys_dom_dn = infraRsVlanNs.get("dn")

            if re.findall(r'(?<=phys-).*(?=/)', phys_dom_dn):
                phys_dom = re.findall(r'(?<=phys-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                policies_dict[vlan_pool[0]].append(phys_dom[0])
            elif re.findall(r'(?<=ledom-).*(?=/)', phys_dom_dn):
                l3_dom = re.findall(r'(?<=l3dom-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                policies_dict[vlan_pool[0]].append(l3_dom[0])
            elif re.findall(r'(?<=vmmp-).*(?=/)', phys_dom_dn):
                vmm_dom = re.findall(r'(?<=vmmp-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                policies_dict[vlan_pool[0]].append(vmm_dom[0])
            else:
                continue

    def extract_vlan_ranges(strings):

        vlans = [ ]
        for vlan in strings:
            remove_vlan = vlan.replace("vlan-", "")
            vlan_range = remove_vlan.split("-")
            vlans.append(vlan_range[0])
        if "vxlan" in vlans:
            pass
        else:
            vlans_unpacked = [ ]
            vlan_start = int(vlans[0])
            vlan_end = int(vlans[1]) + 1

            if vlan_start == vlan_end:
                vlans_unpacked.append(str(vlan_end))
            else:
                begin = vlan_start
                for i in range(vlan_start, vlan_end):
                    vlans_unpacked.append(str(begin))
                    begin = begin + 1

            return  vlans_unpacked

    def find_duplicatee_vlan(session, apic, vlan):

        parent_array = [ ]
        pools = [ ]
        phy_doms = [ ]
        aaep = [ ]
        location = [ ]
        path = [ ]

        uri = "https://" + apic + "/api/class/fvRsPathAtt.xml?query-target-filter=eq(fvRsPathAtt.encap,\"vlan-" + vlan + "\")"

        r_1 = session.get(uri, verify=False, headers=headers)
        aci_gets.file_operation_1(r_1)

        if "\"0\"" in r_1.text:
            print("Encap not Found")
            FindEncap.body(session, apic, username, password)
        else:

            tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
            root = tree.getroot()

            for fvRsPathAtt in root.iter("fvRsPathAtt"):
                string = fvRsPathAtt.get("dn")
                tenant = re.findall(r'(?<=tn-).*(?=/ap)', string)
                location.append("Tenant: " + tenant[0])
                ap = re.findall(r'(?<=ap-).*(?=/ep)', string)
                location.append("App Profile: " + ap[0])
                epg = re.findall(r'(?<=epg-).*(?=/rsp)', string)
                location.append("EPG: " + epg[0])

                if re.findall(r'(?<=protpaths-).*(?=/pat)', string):
                    path_1 = re.findall(r'(?<=protpaths-).*(?=/pat)', string)
                elif re.findall(r'(?<=paths-).*(?=/pat)', string):
                    path_1 = re.findall(r'(?<=paths-).*(?=/pat)', string)

                profile = re.findall(r'(?<=pathep-\[).*(?=]])', string)
                path.append("Path: " + path_1[0] + ": " + profile[0])

            for key_1,value_1 in vlan_dict.items():
                for v in value_1:
                    for v in v:
                        if vlan == v:
                            pools.append(key_1)
                            for key_2, value_2 in policies_dict.items():
                                if key_2 == key_1:
                                   for v in value_2:
                                       phy_doms.append(v)
                            for key_3, value_3 in policies_dict.items():
                               for dom in phy_doms:
                                  if dom in value_3:
                                    if "AAEP" in key_3:
                                        aaep.append(key_3)
                                    else:
                                        continue
                                  else:
                                     pass
                        else:
                            continue

            dup_pools = list(dict.fromkeys(pools))
            dup_epg = list(dict.fromkeys(epg))
            dup_location = list(dict.fromkeys(location))
            dup_aaep = list(dict.fromkeys(aaep))

            return  dup_pools, phy_doms, dup_aaep, dup_location, path

    def file_operation_1(r):

        try:
            file = open(get_file, 'w')
            file.write(r.text)
            file.close()
        except:
            print("File Error")
