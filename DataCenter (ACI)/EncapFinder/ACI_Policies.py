"""Helper functions to get Cisco ACI policies"""

import xml.etree.ElementTree as ET
from typing import Any
import collections
import FindEncap


vlan_dict = collections.defaultdict(list)
policies_dict = collections.defaultdict(list)
aaep_dict = collections.defaultdict(list)

# ----------------------Begin Policy Helper functions------------------------------


def get_vlan_ranges(begin_range, end_range):
    """Expands vlan ranged from vlan pools"""

    vlans = []
    for vlan in range(int(begin_range), int(end_range) + 1):
        vlans.append(str(vlan))

    return vlans


def find_policy_groups(dn) -> str:
    """Finds interface policy groups assigned to encap"""

    if dn.rfind("eth") != -1:
        ply_group = dn.split("[")[2].strip("]")
    else:
        ply_group = dn.split("[")[2].strip("]")

    return ply_group


def find_paths(dn) -> tuple:
    """Find assigned path of encap"""

    path = None
    path_ep = None

    if dn.rfind("rspathL3OutAtt-") != -1:
        path = dn.split("/")[7].strip("protpaths-")
        path_ep = dn.split("/")[8].split("[")[1].strip("]")
    elif dn.rfind("protpaths-") != -1:
        path = dn.split("/")[6].strip("protpaths-")
    elif dn.rfind("paths-") != -1:
        path = dn.split("/")[6].strip("paths-")

    return path, path_ep


def request_pools(session, apic) -> Any:
    """Request configuration from APIC."""

    root = None
    uri = f"https://{apic}/api/node/mo/uni/infra.xml?query-target=subtree&target-subtree-class=fvnsVlanInstP&" \
          f"target-subtree-class=fvnsEncapBlk&query-target=subtree&rsp-subtree=full&rsp-subtree-class=tagAliasInst"
    response = session.get(uri, verify=False)

    # Check to see if the config in the reponse is valid. Returns to login if exception is raised
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Something went wrong. Please try again")
        FindEncap.apic_login()

    return root


def request_domains(session, apic) -> Any:
    """Request ACI domain types"""

    root = None
    uri = f"https://{apic}/api/node/mo/uni.xml?query-target=subtree&target-subtree-class=physDomP&target-subtree-class" \
          f"=infraRsVlanNs,infraRtDomP&query-target=subtree"

    response = session.get(uri, verify=False)

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Something went wrong. Please try again")
        FindEncap.apic_login()

    return root


def request_policy_attachments(session, apic, vlan) -> Any:
    """Request current policy enformation for encap"""

    root = None
    uri = f"https://{apic}/api/class/fvRsPathAtt.xml?query-target-filter=eq(fvRsPathAtt.encap,\"vlan-{vlan}\")"

    response = session.get(uri, verify=False)

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Something went wrong. Please try again")
        FindEncap.apic_login()

    # If reponse has totalcount of 0, notify user that encap wasnt found
    if response.text.rfind("totalCount=\"0\"") != -1 or response.text.rfind("error code") != -1:
        print("\n######## Encapsulation not Attached to any EPGs, Looking for External Assignments ##########")

    return root


def request_l3_attachments(session, apic) -> Any:
    """Request current policy enformation for encap for Outs"""

    root = None
    uri = f"https://{apic}/api/class/l3extRsPathL3OutAtt.xml"

    response = session.get(uri, verify=False)

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Something went wrong. Please try again")
        FindEncap.apic_login()

    # If reponse has totalcount of 0, notify user that encap wasnt found
    if response.text.rfind("totalCount=\"0\"") != -1 or response.text.rfind("error code") != -1:
        print("\n######## No External Policy Assigned ##########")

    return root


# ^^^^^^^^^^^^^^^^^^^^ End Policy Helper functions ^^^^^^^^^^^^^^^^^^^^

# ----------------------Begin Policy functions------------------------------


def vlan_pools(session, apic) -> None:
    """Parses vlan pool names and assigned vlans"""

    root = request_pools(session, apic)

    for fvnsEncapBlk in root.iter("fvnsEncapBlk"):
        if "vxlan" in fvnsEncapBlk.get("from"):
            continue
        else:
            dn = fvnsEncapBlk.get("dn")
            pool_name = dn.split("[")[1].split("]")[0]
            begin_range = dn.split("[")[2].split("-")[1].strip("]")
            end_range = dn.split("[")[3].split("-")[1].strip("]")
            vlans = get_vlan_ranges(begin_range, end_range)
            vlan_dict[pool_name].append(vlans)


def domains(session, apic) -> None:
    """Parses DNs for ACI policy data store to aaep dictionary"""

    root = request_domains(session, apic)

    # Map AAEP to domains, l3, phy, vmm
    for infraRtDomP in root.iter("infraRtDomP"):
        dn = infraRtDomP.get("dn")

        if dn.rfind("phys-") != -1:
            aaeps = dn.split("/")[4].strip("attentp-").strip("]")
            phy_dom = dn.split("/")[1].strip("phys-")
            aaep_dict[f"{aaeps}"].append(phy_dom)
        elif dn.rfind("l3dom") != -1:
            aaeps = dn.split("/")[4].strip("attentp-").strip("]")
            l3_dom = dn.split("/")[1].strip("l3dom-")
            aaep_dict[f"{aaeps}"].append(l3_dom)
        elif dn.rfind("vmmp-") != -1:
            aaeps = dn.split("/")[5].strip("attentp-").strip("]")
            vmm_dom = dn.split("/")[1].strip("vmmp-")
            aaep_dict[f"{aaeps}"].append(vmm_dom)
        else:
            continue

    # Map vlan pool to domains, l3, phy, vmm
    for infraRsVlanNs in root.iter("infraRsVlanNs"):

        vl_pool_dn = infraRsVlanNs.get("tDn")
        dom_dn = infraRsVlanNs.get("dn")

        if dom_dn.rfind("phys-") != -1:
            domain = dom_dn.split("/")[1].strip("phys-")
            vlan_pool = vl_pool_dn.split("[")[1].split("]")[0]
        elif dom_dn.rfind("l3dom-") != -1:
            domain = dom_dn.split("/")[1].strip("l3dom-")
            vlan_pool = vl_pool_dn.split("[")[1].split("]")[0]
        elif dom_dn.rfind("vmmp-") != -1:
            domain = dom_dn.split("/")[1].strip("vmmp-")
            vlan_pool = vl_pool_dn.split("[")[1].split("]")[0]
        else:
            continue

        policies_dict[domain].append(vlan_pool)


def map_policy_configurations(session, apic, vlan) -> tuple:
    """Finds the requested encap locations and configurations"""

    pools = []
    phy_doms = []
    aaeps = []
    location = []
    paths = []

    # Request L3Outs attachments, parse strings
    root = request_l3_attachments(session, apic)
    for l3extRsPathL3OutAtt in root.iter("l3extRsPathL3OutAtt"):
        encap = l3extRsPathL3OutAtt.get('encap').strip("vlan-")
        if vlan == encap:
            dn = l3extRsPathL3OutAtt.get("dn")
            path = find_paths(dn)

            tenant = dn.split("/")[1].strip("tn-")
            l3out = dn.split("/")[2].strip("out-")
            interface = dn.split("/")[4].strip("lifp-")

            location.append(f" Tenant: {tenant}")
            paths.append(f"EP: {path[1]}")
            location.append(f"L3Out: {l3out}")
            location.append(f"Interface: {interface}")

    # Request EPG attachments, parse strings
    root = request_policy_attachments(session, apic, vlan)
    for fvRsPathAtt in root.iter("fvRsPathAtt"):
        dn = fvRsPathAtt.get("dn")

        path = find_paths(dn)
        ply_group = find_policy_groups(dn)

        tenant = dn.split("/")[1].strip("tn-")
        ap = dn.split("/")[2].strip("ap-")
        epg = dn.split("/")[3].strip("epg-")

        paths.append(f"Path: {path[0]}: {ply_group}")
        location.append(f"Tenant: {tenant}")
        location.append(f"App Profile: {ap}")
        location.append(f"EPG: {epg}")

    # Remove duplicate locations
    locations = list(dict.fromkeys(location))

    # Check if request encap is assigned to any vlan pools
    for vlan_pool, vlans in vlan_dict.items():
        for i in vlans:
            for index in i:
                if vlan == index:
                    pools.append(vlan_pool)

    # Cross reference pools name with pools assigned to domains
    for pool in pools:
        for dom_type, vl_pool in policies_dict.items():
            if pool in vl_pool:
                phy_doms.append(dom_type)

    # Cross reference domains assigned to aaeps and domains assign to vlan pools
    for aaep, dom in aaep_dict.items():
        if list(set(dom) & set(phy_doms)):
            aaeps.append(aaep)

    return pools, phy_doms, aaeps, locations, paths

# ^^^^^^^^^^^^^^^^^^^^ End Policy Funtions^^^^^^^^^^^^^^^^^^^^
