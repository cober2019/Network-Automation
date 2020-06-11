import requests
import json
import warnings
import xml.etree.ElementTree as ET
import re
import collections
import ipaddress


class AciOps:

    """Collects authentication information from user, returns session if successfull, or response if not"""

    def __init__(self):

        self.session = None
        self.response = None
        self.apic = None
        self.vlan_dict = collections.defaultdict(list)
        self.policies_dict = collections.defaultdict(list)
        self.device_info = []
        self.tenant_array = []

    def login(self, **kwargs):

        """APIC authentication method. Takes username, password, apic kwargs and returns session"""

        ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        uri = "https://%s/api/aaaLogin.json" % kwargs["apic"]
        json_auth = {'aaaUser': {'attributes': {'name': kwargs["username"], 'pwd': kwargs["password"]}}}
        json_credentials = json.dumps(json_auth)
        self.session = requests.Session()
        self.apic = kwargs["apic"]

        try:
            request = self.session.post(uri, data=json_credentials, verify=False)
            self.response = json.loads(request.text)
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            raise ConnectionError("Login Failed, Verify APIC Address")

        try:
            if self.response["imdata"][0]["error"]["attributes"]["code"] == "401":
                raise ValueError("Login Failed, please verify credentials | Credential Submitted:\n{}\n{}".format(
                                                                            kwargs["username"], kwargs["password"]))
        except TypeError:
            raise TypeError("Something Went Wrong")
        except KeyError:
            pass
        else:
            return self.session


    def vlan_pools(self):

        """Get fabric vlan pools, return pool in a dictionary data structure"""

        vlan_range_dict = collections.defaultdict(list)

        uri = "https://" + self.apic + "/api/node/mo/uni/infra.xml?query-target=subtree&target-subtree-class=fvnsVlanInstP&target-subtree-class=fvnsEncapBlk&query-target=subtree&rsp-subtree=full&rsp-subtree-class=tagAliasInst"
        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fvnsEncapBlk in root.iter("fvnsEncapBlk"):
            vlan_pool_array = []
            if "vxlan" in fvnsEncapBlk.get("from"):
                continue
            else:
                vlan_pool_array.append(fvnsEncapBlk.get("from"))
                vlan_pool_array.append(fvnsEncapBlk.get("to"))
                start_range = fvnsEncapBlk.get("from")
                end_range = fvnsEncapBlk.get("to")
                dn = fvnsEncapBlk.get("dn")
                parse_dn = re.findall(r'(?<=vlanns-\[).*?(?=]-[a-z])', dn)
                vlan_range_dict[parse_dn[0]] = start_range + "-" + end_range

                vlans = []
                for vlan in vlan_pool_array:
                    remove_vlan = vlan.replace("vlan-", "")
                    vlan_range = remove_vlan.split("-")
                    vlans.append(vlan_range[0])

                if "vxlan" in vlans:
                    pass
                else:
                    vlans_unpacked = []
                    vlan_start = int(vlans[0])
                    vlan_end = int(vlans[1]) + 1

                    if vlan_start == vlan_end:
                        vlans_unpacked.append(str(vlan_end))
                    else:
                        begin = vlan_start
                        for i in range(vlan_start, vlan_end):
                            vlans_unpacked.append(str(begin))
                            begin = begin + 1

                self.vlan_dict[parse_dn[0]].append(vlans_unpacked)

        return vlan_range_dict

    def find_encap(self, **kwargs):

        """Takes in the vlan encapsulation, intiaates vlan_pool(0 and policy_mappings. Calls _find_encap_comiple to fin fabric information about the encapsulation
        Returns a series of list to the caller"""

        vlan_pool = collections.defaultdict(list)
        phys_doms = collections.defaultdict(list)
        aaeps = collections.defaultdict(list)
        location = collections.defaultdict(list)
        path = collections.defaultdict(list)

        self.vlan_pools()
        self.policy_mappings()

        pools = self._find_encap_compile(vlan=kwargs["vlan"])
        vlan_pool[kwargs["vlan"]].append(pools[0])
        phys_doms[kwargs["vlan"]].append(pools[1])
        aaeps[kwargs["vlan"]].append(pools[2])
        location[kwargs["vlan"]].append(pools[3])
        path[kwargs["vlan"]].append(pools[4])

        unpacked_vlan_pools = [v for k, v in vlan_pool.items() for v in v for v in v]
        unpacked_phys_doms = [v for k, v in phys_doms.items() for v in v for v in v]
        unpacked_aaep = [v for k, v in aaeps.items() for v in v for v in v]
        unpacked_location = [v for k, v in location.items() for v in v for v in v]
        unpacked_path = [v for k, v in path.items() for v in v for v in v]

        return unpacked_vlan_pools, unpacked_phys_doms, unpacked_aaep, unpacked_location, unpacked_path


    def _find_encap_compile(self, **kwargs):

        """ This method is for local use only. It works with vlan_pool() to produce a series of list and return them to the call find_encap"""

        pools = []
        phy_doms = []
        aaep = []
        location = []
        path = []

        uri = "https://{}/api/class/fvRsPathAtt.xml?query-target-filter=eq(fvRsPathAtt.encap,\"vlan-{}\")".format(self.apic, kwargs["vlan"])
        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        if "\"0\"" in request.text:
            print("Encap not Found")
        else:
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

            for key_1, value_1 in self.vlan_dict.items():
                for v in value_1:
                    for v in v:
                        if kwargs["vlan"] == v:
                            pools.append(key_1)
                            for key_2, value_2 in self.policies_dict.items():
                                if key_2 == key_1:
                                    for v in value_2:
                                        phy_doms.append(v)
                            for key_3, value_3 in self.policies_dict.items():
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
            dup_location = list(dict.fromkeys(location))
            dup_aaep = list(dict.fromkeys(aaep))

            return dup_pools, phy_doms, dup_aaep, dup_location, path

    def policy_mappings(self):

        """Maps AAEPS, Vlan Pools, and phys/vmm/routed domain. Return dictionary data structure"""

        uri = "https://" + self.apic + "/api/node/mo/uni.xml?query-target=subtree&target-subtree-class=physDomP&target-subtree-class=infraRsVlanNs,infraRtDomP&query-target=subtree"
        headers = {'content-type': 'text/xml'}

        request = self.session.get(uri, verify=False, headers=headers)
        root = ET.fromstring(request.text)

        for infraRtDomP in root.iter("infraRtDomP"):
            string = infraRtDomP.get("dn")
            if re.findall(r'phys-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                phys_dom = re.findall(r'(?<=phys-).*(?=/rt)', string)
                self.policies_dict["AAEP " + aaeps[0]].append(phys_dom)
            elif re.findall(r'l3dom-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                l3_dom = re.findall(r'(?<=l3dom-).*(?=/rt)', string)
                self.policies_dict["AAEP " + aaeps[0]].append(l3_dom)
            elif re.findall(r'vmmp-.*?[/]\b', string):
                aaeps = re.findall(r'(?<=attentp-).*(?=])', string)
                vmm_dom = re.findall(r'(?<=vmmp-).*(?=/rt)', string)
                self.policies_dict["AAEP " + aaeps[0]].append(vmm_dom[0])
            else:
                continue

        for infraRsVlanNs in root.iter("infraRsVlanNs"):

            vl_pool_dn = infraRsVlanNs.get("tDn")
            phys_dom_dn = infraRsVlanNs.get("dn")

            if re.findall(r'(?<=phys-).*(?=/)', phys_dom_dn):
                phys_dom = re.findall(r'(?<=phys-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                self.policies_dict[vlan_pool[0]].append(phys_dom)
            elif re.findall(r'(?<=ledom-).*(?=/)', phys_dom_dn):
                l3_dom = re.findall(r'(?<=l3dom-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                self.policies_dict[vlan_pool[0]].append(l3_dom)
            elif re.findall(r'(?<=vmmp-).*(?=/)', phys_dom_dn):
                vmm_dom = re.findall(r'(?<=vmmp-).*(?=/)', phys_dom_dn)
                vlan_pool = re.findall(r'(?<=vlanns-\[).*(?=])', vl_pool_dn)
                self.policies_dict[vlan_pool[0]].append(vmm_dom[0])
            else:
                continue

        return self.policies_dict

    def infr(self, **kwargs):


        """Takes in pod number , and return all information about the fabric hardware. Greate for TAC use"""

        pod_num = kwargs["pod"]
        pod_number = "pod-{}".format(pod_num)

        uri = "https://{}/api/node/mo/topology/{}.xml?query-target=children".format(self.apic, pod_number)

        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fabricNode in root.iter("fabricNode"):
            fabric_node = fabricNode.get("name")
            model_node = fabricNode.get("model")
            serial_node = fabricNode.get("serial")
            self.device_info.append(fabric_node)
            self.device_info.append(model_node)
            self.device_info.append(serial_node)

        if not self.device_info:
            return "No Infrastructor Information"
        else:
            return self.device_info

    def view_tenants(self):

        """Returns ACI Tenant from the arbitrary APIC"""

        uri = "https://{}/api/class/fvTenant.json".format(self.apic)

        request = self.session.get(uri, verify=False)
        response_dict = request.json()
        total_count = int(response_dict["totalCount"])

        try:
            index = 0
            for i in range(0, total_count):
                self.tenant_array.append(response_dict["imdata"][index]["fvTenant"]["attributes"]["name"])
                index = index + 1
        except IndexError:
            pass

        return self.tenant_array

    def subnet_finder(self, **kwargs):

        """ Takes in kwarg subnet and finds all details about the subnet (BD, Tenant, scope etc."""


        self.view_tenants()

        uri = "https://{}/api/class/fvBD.xml?query-target=subtree".format(self.apic)
        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fvSubnet in root.iter("fvSubnet"):
            location = fvSubnet.get("dn")
            ip = fvSubnet.get("ip")
            if kwargs["subnet"] in ip:
                gps = location
                gps_ip = ip
                scope = fvSubnet.get("scope")

        try:
            for fvBD in root.iter("fvBD"):
                bridge_domain = fvBD.get("name")
                if re.findall('[?<=/BD-]' + bridge_domain + '(?=/)', gps):
                    gps_bd = bridge_domain
                    uni_route = fvBD.get("unicastRoute")
                    unkwn_uni = fvBD.get("unkMacUcastAct")

            for fvRsCtx in root.iter("fvRsCtx"):
                vrf = fvRsCtx.get("tnFvCtxName")
                location = fvRsCtx.get("dn")
                if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', location):
                    gps_vrf = vrf

            aps = []
            epgs = []

            for fvRtBd in root.iter("fvRtBd"):
                dn = fvRtBd.get("dn")
                if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                    ap = re.findall(r'(?<=ap-).*(?=/ep)', dn)
                    aps.append(ap[0])
                    epg = re.findall(r'(?<=epg-).*(?=\])', dn)
                    epgs.append(epg[0])
                else:
                    pass

            for fvRsBDToOut in root.iter("fvRsBDToOut"):
                dn = fvRsBDToOut.get("dn")
                if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                    if not fvRsBDToOut.get("tnL3extOutName"):
                        l3out = "N/A"
                    else:
                        l3out = fvRsBDToOut.get("tnL3extOutName")

            for tenant in self.tenant_array:
                if tenant in gps:
                    gps_tenant = tenant
                else:
                    continue

            unpack_ap = [i for i in aps]
            unpack_epg = [i for i in epgs]

        except UnboundLocalError:
            pass

        return gps_ip, gps_tenant, gps_bd, vrf, l3out, uni_route, scope, unkwn_uni, unpack_ap, unpack_epg

    def tenant_vrf(self, **kwargs):

        """View Tenant vrf, return Tenant vrf names"""

        vrf_dict = collections.defaultdict(list)
        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvCtx"\
                                                                    .format(self.apic, kwargs["tenant"])
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)

        try:
            index = 0
            for i in range(0, 100):
                vrf_dict["vrf"].append(response["imdata"][index]["fvCtx"]["attributes"]["name"])
                index = index + 1
        except IndexError:
            pass

        return vrf_dict

    def view_bd(self, **kwargs):

        """View Bridge domains of a Tenant, returns bridge domain names"""

        bd_dict = collections.defaultdict(list)
        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvBD"\
                                                                    .format(self.apic, kwargs["tenant"])
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        for i in range(0, total_count):
            bd_dict["name"].append(response["imdata"][index]["fvBD"]["attributes"]["name"])
            index = index + 1

        return bd_dict

    def view_app_profiles(self, **kwargs):

        """View Application profiles of a particular Tenant, return App profiles"""

        app_dict = collections.defaultdict(list)
        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvAp"\
                                                                    .format(self.apic, kwargs["tenant"])
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        for i in range(0, total_count):
            app_dict["name"].append(response["imdata"][index]["fvAp"]["attributes"]["name"])
            index = index + 1

        return app_dict

    def view_epgs(self, **kwargs):

        """View endpoint groups of a particular Tenant-App profile, returns EPG names"""

        epg_dict = collections.defaultdict(list)
        uri = "https://{}/api/node/mo/uni/tn-{}/ap-{}.json?query-target=children&target-subtree-class=fvAEPg"\
                                                            .format(self.apic, kwargs["tenant"], kwargs["app"])
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        for i in range(0, total_count):
            epg_dict["name"].append(response["imdata"][index]["fvAEPg"]["attributes"]["name"])
            index = index + 1

        return epg_dict

    def enpoint_tracker(self, **kwargs):

        """This method take in a IP or MAC address and returns the endpoint data. Return string if no endpoint is found"""

        try:
            ipaddress.IPv4Address(kwargs["endpoint"])
            uri = "https://%s" % self.apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-include=" \
                                     "required&rsp-subtree-filter=eq(fvIp.addr," + "\"%s\"" % kwargs["endpoint"]

        except ValueError:
            uri = "https://%s" % self.apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-class=" \
                  "fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm&query-target-filter=eq(fvCEp.mac," \
                  + "\"%s\"" % kwargs["endpoint"]

        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fvCEp in root.iter("fvCEp"):
            print(fvCEp)
            ep_name = fvCEp.get("name")
            ep_mac = fvCEp.get("mac")
            encap = fvCEp.get("encap")
            ep_loc = fvCEp.get("dn")
            ep_ip = fvCEp.get("ip")

            endpoint = ("Name: {0:20}\nEP: {1:<20}\nEncapsulation: {2:<20}\nLocation: {3:<20}\nIP: {4:<20}"
                                                                .format(ep_name,ep_mac,encap,ep_loc,ep_ip))


        try:
            return endpoint
        except UnboundLocalError:
            return  "Endpoint Not Found"

