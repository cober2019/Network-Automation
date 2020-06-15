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
        self.bd_array = []
        self.ap_array = []
        self.epg_array = []
        self.vrf_array = []
        self.json_header = headers = {'content-type': 'application/json'}

    def login(self, apic=None, username=None, password=None):

        """APIC authentication method. Takes username, password, apic kwargs and returns session"""

        ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        uri = "https://%s/api/aaaLogin.json" % apic
        json_auth = {'aaaUser': {'attributes': {'name': username, 'pwd': password}}}
        json_credentials = json.dumps(json_auth)
        self.session = requests.Session()
        self.apic = apic

        try:
            request = self.session.post(uri, data=json_credentials, verify=False)
            self.response = json.loads(request.text)
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            raise ConnectionError("Login Failed, Verify APIC Address")

        try:
            if self.response["imdata"][0]["error"]["attributes"]["code"] == "401":
                raise ValueError("Login Failed, please verify credentials | Credential Submitted:\n{}\n{}"
                                                                                .format(username, password))
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

        return request, vlan_range_dict

    def find_encap(self, encap=None):

        """Takes in the vlan encapsulation, intiaates vlan_pool(0 and policy_mappings. Calls _find_encap_comiple to fin fabric information about the encapsulation
        Returns a series of list to the caller"""

        vlan_pool = collections.defaultdict(list)
        phys_doms = collections.defaultdict(list)
        aaeps = collections.defaultdict(list)
        location = collections.defaultdict(list)
        path = collections.defaultdict(list)

        self.vlan_pools()
        self.policy_mappings()

        pools = self._find_encap_compile(encap)
        vlan_pool[encap].append(pools[0])
        phys_doms[encap].append(pools[1])
        aaeps[encap].append(pools[2])
        location[encap].append(pools[3])
        path[encap].append(pools[4])

        unpacked_vlan_pools = [v for k, v in vlan_pool.items() for v in v for v in v]
        unpacked_phys_doms = [v for k, v in phys_doms.items() for v in v for v in v]
        unpacked_aaep = [v for k, v in aaeps.items() for v in v for v in v]
        unpacked_location = [v for k, v in location.items() for v in v for v in v]
        unpacked_path = [v for k, v in path.items() for v in v for v in v]

        return unpacked_vlan_pools, unpacked_phys_doms, unpacked_aaep, unpacked_location, unpacked_path

    def _find_encap_compile(self, encap=None):

        """ This method is for local use only. It works with vlan_pool() to produce a series of list and return them
        to the call find_encap"""

        pools = []
        phy_doms = []
        aaep = []
        location = []
        path = []

        uri = "https://{}/api/class/fvRsPathAtt.xml?query-target-filter=eq(fvRsPathAtt.encap,\"vlan-{}\")".format(self.apic, encap)
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
                        if encap == v:
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

        return request, self.policies_dict

    def infr(self, pod=None):

        """Takes in pod number , and return all information about the fabric hardware. Greate for TAC use"""

        pod_num = pod
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
            self.tenant_array.clear()
            for i in range(0, total_count):
                self.tenant_array.append(response_dict["imdata"][index]["fvTenant"]["attributes"]["name"])
                index = index + 1
        except IndexError:
            pass

        return self.tenant_array

    def subnet_finder(self, subnet=None):

        """ Takes in kwarg subnet and finds all details about the subnet (BD, Tenant, scope etc."""

        endpoint_dict = {}
        uri = "https://{}/api/class/fvBD.xml?query-target=subtree".format(self.apic)
        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fvSubnet in root.iter("fvSubnet"):
            location = fvSubnet.get("dn")
            ip = fvSubnet.get("ip")
            if subnet in ip:
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
                print(location)
                if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', location):
                    print(vrf)
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
                if "fvRsBDToOut" in fvRsBDToOut:
                    dn = fvRsBDToOut.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                        if not fvRsBDToOut.get("tnL3extOutName"):
                            l3out = "N/A"
                        else:
                            l3out = fvRsBDToOut.get("tnL3extOutName")
                else:
                    l3out = "None"

            for tenant in self.tenant_array:
                if tenant in gps:
                    gps_tenant = tenant
                else:
                    continue

            unpack_ap = [i for i in aps]
            if not unpack_ap:
                unpack_ap = "None"

            unpack_epg = [i for i in epgs]
            if not unpack_epg:
                unpack_epg = "None"

            endpoint_dict["IP"] = gps
            endpoint_dict["Tenant"] = gps_tenant
            endpoint_dict["BD"] = gps_bd
            endpoint_dict["vrf"] = gps_vrf
            endpoint_dict["L3Out"] = l3out
            endpoint_dict["Route Enable"] = uni_route
            endpoint_dict["Scope"] = scope
            endpoint_dict["Uni Flood"] = unkwn_uni
            endpoint_dict["APs"] = unpack_ap
            endpoint_dict["EPGs"] = unpack_epg

            return endpoint_dict

        except UnboundLocalError:
            return "Subnet not found"

    def view_tenant_vrf(self, tenant=None):

        """View Tenant vrf, return Tenant vrf names"""

        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvCtx"\
                                                                            .format(self.apic, tenant)
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)

        try:
            index = 0
            self.vrf_array.clear()
            for i in range(0, 100):
                self.vrf_array.append(response["imdata"][index]["fvCtx"]["attributes"]["name"])
                index = index + 1
        except IndexError:
            pass

        return self.vrf_array

    def view_bd(self, tenant=None):

        """View Bridge domains of a Tenant, returns bridge domain names"""

        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvBD"\
                                                                            .format(self.apic, tenant)
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        self.bd_array.clear()
        for i in range(0, total_count):
            self.bd_array.append(response["imdata"][index]["fvBD"]["attributes"]["name"])
            index = index + 1

        return self.bd_array

    def view_app_profiles(self, tenant=None):

        """View Application profiles of a particular Tenant, return App profiles"""

        uri = "https://{}/api/node/mo/uni/tn-{}.json?query-target=children&target-subtree-class=fvAp"\
                                                                            .format(self.apic, tenant)
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        self.ap_array.clear()
        for i in range(0, total_count):
            self.ap_array.append(response["imdata"][index]["fvAp"]["attributes"]["name"])
            index = index + 1

        return self.ap_array

    def view_epgs(self, tenant=None, app=None):

        """View endpoint groups of a particular Tenant-App profile, returns EPG names"""

        uri = "https://{}/api/node/mo/uni/tn-{}/ap-{}.json?query-target=children&target-subtree-class=fvAEPg"\
                                                                                .format(self.apic, tenant, app)
        request = self.session.get(uri, verify=False)
        response = json.loads(request.text)
        total_count = int(response["totalCount"])

        index = 0
        self.epg_array.clear()
        for i in range(0, total_count):
            self.epg_array.append(response["imdata"][index]["fvAEPg"]["attributes"]["name"])
            index = index + 1

        return self.epg_array

    def enpoint_tracker(self, endpoint=None):

        """This method take in a IP or MAC address and returns the endpoint data. Return string if no endpoint
        is found"""

        try:
            ipaddress.IPv4Address(endpoint)
            uri = "https://%s" % self.apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-include=" \
                                                "required&rsp-subtree-filter=eq(fvIp.addr," + "\"%s\"" % endpoint

        except ValueError:
            uri = "https://%s" % self.apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-class=" \
                  "fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm&query-target-filter=eq(fvCEp.mac," \
                  + "\"%s\"" % endpoint

        request = self.session.get(uri, verify=False)
        root = ET.fromstring(request.text)

        for fvCEp in root.iter("fvCEp"):
            ep_name = fvCEp.get("name")
            ep_mac = fvCEp.get("mac")
            encap = fvCEp.get("encap")
            ep_loc = fvCEp.get("dn")
            ep_ip = fvCEp.get("ip")

            endpoint = ("Name: {0:20}\nEP: {1:<20}\nEncapsulation: {2:<20}\nLocation: {3:<20}\nIP: {4:<20}"
                                                                .format(ep_name, ep_mac, encap, ep_loc, ep_ip))

        try:
            return endpoint
        except UnboundLocalError:
            return  "Endpoint Not Found"


class AciOpsSend(AciOps):

    """ACI send basic configs. Return value will be APIC response in dictionary structure, or string notify the caller of
    and error"""

    def __init__(self, **kwargs):

        """ Import * from AciOps class. Use AciOps login method to create a http session. Once session has been
        intiated, call AciOps view_tenants method. The AciOps self.session and self.tenant_array will be used
        throughout"""

        super().__init__()
        self.login(apic=kwargs["apic"], username=kwargs["username"], password=kwargs["password"])
        self.view_tenants()

    def create_tenant(self, tenant=None):

        """Create tenant, arg supplied will be tenants name. Conditional check will be done o insure  no duplicates"""

        uri = """https://{}/api/mo/uni.json""".format(self.apic)

        if tenant not in self.tenant_array:

            tenants = """{"fvTenant" : { "attributes" : { "name" : "%s"}}}""" % tenant
            request = self.session.post(uri, verify=False, data=tenants, headers=self.json_header)
            tenants = self.view_tenants()

            return request, tenants
        else:
            return "Tenant: %s Exist" % tenant

    def create_app_profile(self, tenant=None, app=None):

        """Create app prof, args supplied will be tenant, and app prof name.
        Conditional check will be done to insure  no duplicates"""

        app_profiles = self.view_app_profiles(tenant=tenant)

        if app not in app_profiles:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            app_profile = "{\"fvAp\": " \
                          "{\"attributes\": " \
                          "{\"name\": \"%s\"}}}}" % app

            request = self.session.post(uri, verify=False, data=app_profile, headers=self.json_header)
            app_profiles = self.view_app_profiles(tenant=tenant)

            return request, app_profiles
        else:
            return "App Profile: %s Exist " % app

    def create_epg(self, tenant=None, app=None, epg=None):

        """Create epg, args supplied will be tenant, and app prof name, and epg name
        Conditional check will be done to insure  no duplicates"""

        epgs = self.view_epgs(tenant=tenant, app=app)

        if epg not in epgs:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + "/ap-" + app + ".json"
            epg = "{\"fvAEPg\":" \
                  "{\"attributes\": " \
                  "{\"name\": \"%s\"}}}}" % epg

            request = self.session.post(uri, verify=False, data=epg, headers=self.json_header)
            epgs = self.view_epgs(tenant=tenant, app=app)

            return request, epgs
        else:
            return "EPG: %s Exist" % epg

    def create_bd_l3(self, tenant=None, bd=None, subnet=None, scope=None):

        """Create bd, args supplied will be tenant. Conditional check will be done to insure  no duplicates"""

        bds = self.view_bd(tenant=tenant)

        if bd not in bds:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            bridge_dom = "{\"fvBD\":" \
                         "{\"attributes\": " \
                         "{\"name\": \"%s\"" % bd + "}," \
                         "\"children:[" \
                         "{\"fvSubnet\": " \
                         "{\"attributes\":" \
                         "{\"ip\": \"%s\"" % subnet + "," \
                         "{\"scope\": \"%s\"" % scope + "}}}}]}}}"

            request = self.session.post(uri, verify=False, data=bridge_dom, headers=self.json_header)
            bds = self.view_bd(tenant=tenant)
            bd_info = self.subnet_finder(subnet=subnet)

            return request, bds, bd_info

        else:
            return "BD: %s Exist" % bd

    def routing_scope(self, tenant=None, bd=None, subnet=None, scope=None):

        """Configuring routing scope (shared, private, external). First we split the scope to check for validity
        if valid, use the orignal scope arg for the variable"""

        split_scope = scope.split(",")
        scope_list = ["private", "public", "shared"]
        bds = self.view_bd(tenant=tenant)

        for scope in split_scope:
            if scope not in scope_list:
                raise ValueError("Invalid Scope \"{}\" - Expecting private|public|shared".format(scope))
            else:
                pass

        if bd in bds:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + "/BD-" + bd + "/subnet-[" + subnet + "].json"
            bridge_dom = "{\"fvSubnet\": " \
                         "{\"attributes\":" \
                         "{\"scope\": \"%s\"" % scope + "}}}"

            request = self.session.post(uri, verify=False, data=bridge_dom, headers=self.json_header)
            bds = self.view_bd(tenant=tenant)
            bd_info = self.subnet_finder(subnet=subnet)

            return request, bds, bd_info

        else:
            return "BD: %s Exist" % bd

    def enable_unicast(self, tenant=None, bd=None, enable=None):

        """Create bd, args supplied will be tenant  Conditional check will be done to insure  no duplicates,
        require yes/no input"""

        bds = self.view_bd(tenant=tenant)
        yes_no = ["yes", "no"]

        if enable not in yes_no:
            raise ValueError("Invalid arg \"{}\" - Expecting yes/no".format(enable))
        if bd in bds:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            bridge_dom = "{\"fvBD\":" \
                         "{\"attributes\": " \
                         "{\"name\": \"%s\"" % bd + ", \"" \
                         "unicastRoute\": \"%s\"" % enable + "}}}"

            request = self.session.post(uri, verify=False, data=bridge_dom, headers=self.json_header)

            return request, bridge_dom

        else:
            return "BD: %s Exist" % bd

    def create_bd_l2(self, tenant=None, bd=None):

        """Create L2 bd, args supplied will be tenant  Conditional check will be done to insure  no duplicates"""

        bds = self.view_bd(tenant=tenant)

        if bd not in bds:

            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            bridge_dom = "{\"fvBD\":" \
                         "{\"attributes\": " \
                         "{\"name\": \"%s\"" % bd + "}}}"

            request = self.session.post(uri, verify=False, data=bridge_dom, headers=self.json_header)
            bds = self.view_bd(tenant=tenant)

            return request, bds
        else:
            return "BD: %s Exist" % bd

    def create_vrf(self, tenant=None, vrf=None):

        """Create tenant vrf, args supplied will be tenant  Conditional check will be done to insure  no duplicates"""

        vrfs = self.view_tenant_vrf(tenant=tenant)

        if vrf not in vrfs:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            vrf = "{\"fvCtx\":" \
                  "{\"attributes\": " \
                  "{\"name\": \"%s\"" % vrf + "}}}"

            request = self.session.post(uri, verify=False, data=vrf, headers=self.json_header)
            vrfs = self.view_tenant_vrf(tenant=tenant)

            return request, vrfs
        else:
            return "Vrf: %s Exist" % vrf

    def vrf_to_bd(self, tenant=None, bd=None, vrf=None):

        """Assign vrf to bd, args supplied will be tenant, bd name, vrf name
        Conditional check will be done to insure vrf has been configured"""

        vrfs = self.view_tenant_vrf(tenant=tenant)

        if vrf in vrfs:
            uri = "https://" + self.apic + "/api/mo/uni/tn-" + tenant + ".json"
            vrf_bd = "{\"fvBD\":" \
                     "{\"attributes\": " \
                     "{\"name\": \"%s\"" % bd + "}," \
                     "\"children:[" \
                     "{\"fvRsCtx \": " \
                     "{\"attributes\":" \
                     "{\"tnFvCtxName\": \"%s\"" % vrf + "}}}]}}}"

            request = self.session.post(uri, verify=False, data=vrf_bd, headers=self.json_header)
            vrfs = self.view_tenant_vrf(tenant=tenant)

            return request, vrfs
        else:
            return "VRF: %s Doesn't Exist " % vrf


