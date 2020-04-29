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

get_file = "C:\Python\ACI\Get_ACI.xml"
vlan_dict = collections.defaultdict(list)

def body(session, apic):

    uri = "https://" + apic + "/api/node/mo/uni/infra.xml?query-target=subtree&target-subtree-class=fvnsVlanInstP&target-subtree-class=fvnsEncapBlk&query-target=subtree&rsp-subtree=full&rsp-subtree-class=tagAliasInst"
    headers = {'content-type': 'text/xml'}

    r_1 = session.get(uri, verify=False, headers=headers)
    file_operation_1(r_1)  # Write xml repsonse to file, carry r_1 to funtion - Line 238

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
            parse_dn = string_manipulation_1(re.search(r'[\[][a-zA-Z0-9].*?[\]]', dn))
            vlans = string_manipulation_2(vlan_pool_array)
            vlan_dict[parse_dn].append(vlans)

def string_manipulation_1(string):

    strip_1 = string[0].replace("[", "")
    strip_2 = strip_1.replace("]", "")
    return strip_2

def string_manipulation_2(strings):

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
        vlan_end = int(vlans[1])

        if vlan_start == vlan_end:
            vlans_unpacked.append(str(vlan_end))
        else:
            begin = vlan_start
            for i in range(vlan_start, vlan_end):
                vlans_unpacked.append(str(begin))
                begin = begin + 1

        return  vlans_unpacked


def find_duplicatee_vlan(vlan):

    pools = [ ]
    for k,v in vlan_dict.items():
        for v in v:
            for v in v:
                if vlan == v:
                    pools.append(k)
                else:
                    continue

    return  pools


def file_operation_1(r):

    try:
        file = open(get_file, 'w')     # Open/creates a file to write XML data to
        file.write(r.text)
        file.close()

    except:
        print("File Error")

if __name__ == '__main__':

    body()