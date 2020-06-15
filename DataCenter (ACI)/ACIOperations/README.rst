ACIOps
==============
Description
--------------

ACIOps is a collection of my personal method/functions used in my programs. The module will return all the the requested
information for you unformatted. Within this module you will find the following
tools:

+ APIC Login
+ Subnet Finder
+ View Tenants
+ Vlans Pools
+ Encapsulation Finder
+ Access Policy Mappings
+ Tenant vrfs
+ Application Profiles
+ Endpoint Groups
+ Bridge Domains
+ Endpoint Finder

Depedency Modules
__________

+ xml.etree.ElementTree
+ ipaddress
+ collections
+ json
+ warnings
+ request
+ re

Usage
_____

**Import**

        >>>import ACIOperations.ACIOps as ops

Examples
---
Some method can be run without any argument and some dont. The seed method is always the login() which produces the session

**Example 1 (Authentication: )**

            >>> call_class = ops.AciOps()
            >>> login = call_class.login(apic="192.168.1.1", username="JoeSmo", password="helpme!")
            >>> print(call_class.session)
            <requests.sessions.Session object at 0x00000253743CFB48>
            >>>

**Example 2 (Fetch VLAN Pools: )**

            >>>call_class.vlan_pools()
            defaultdict(<class 'list'>, {'Pool1': 'vlan-10-vlan-20', 'Pool2': 'vlan-1000-vlan-2000'}
            >>> pools = call_class.vlan_pools()
            >>> for k, v in pools.items():
                    print("Pool: {}    Range: {}".format(k, v))

                    Pool: Pool1    Range: vlan-10-vlan-20
                    Pool: Pool2    Range: vlan-1000-vlan-2000

**Example 3 (Find Encap: )**

            >>>find_encap = call_class.find_encap(vlan="2000")
            * Output omitted due to length
            This will produce all access policies associated with an external fabric encapsulation

**Example 4 (Policy Mappings:)**

            >>> policy_maps = call_class.policy_mappings()
            * Output omitted due to length
            This will map vlan pools, AAEP, phydoms, routeddoms, vmmdoms and return to user.

**Example 5 (Infrastructure Info: )**

            >>> infra = call_class.infr(pod=1)
            >>> print(infra)
            ['Leaf101', 'N9K-C93180YC-EX', 'FDO21eddfrr', 'Leaf102', 'N9K-C93108TC-EX', 'FDO21rfeff', 'Spine101', 'N9K-C9336PQ', 'FDO2rffere']

**Example 6 (Find Subnet: )**

            >>> find_subnet = call_class.subnet_finder(subnet="10.1.1.1/24")
            >>> print(find_subnet)
            ('10.1.1.1/24', 'Customer1', 'BD-VL100', 'Customer1-VRF', 'Customer1-l3out', 'yes', 'public,shared', 'flood', ['ANP-Web'], ['EPG-WebServer'])

**Example 7 (View Tenants: )**

            >>> tenants = call_class.view_tenants()
            >>> print(tenants)
            ['infra', 'Customer-1', 'common', 'Customer-2']
            >>>

**Example 8 (View Vrf: )**

            >>> vrf = call_class.tenant_vrf(tenant="Customer-1")
            >>> print(vrf)
            defaultdict(<class 'list'>, {'vrf': ['Customer-1']})
            >>>

**Example 9 (View Bridge Domains: )**

            >>> bd = call_class.view_bd(tenant="Customer-1")
            >>> print(bd)
            defaultdict(<class 'list'>, {'name': ['BD-VL100', 'BD-VL200']}
            >>>

**Example 9 (View App Profiles: )**

            >>> ap = call_class.view_app_profiles(tenant="Customer-1")
            >>> print(ap)
            defaultdict(<class 'list'>, {'name': ['ANP-WEB', 'ANP-DB']}
            >>>

**Example 10 (View EPG: )**

            >>> epg = call_class.view_epgs(tenant="Customer-1", app="ANP-WEB")
            >>> print(epg)
            defaultdict(<class 'list'>, {'name': ['EPG-WEB']})
            >>>

**Example 11 (Endpoint Tracker: )**

            >>> endpoint = call_class.enpoint_tracker(endpoint="10.1.1.10")
            >>> print(endpoint)
            Name: 00:50:56:A0:77:88
            EP: 00:50:56:A0:77:88
            Encapsulation: vlan-200
            Location: uni/tn-Customer-1/ap-ANP-WEB/epg-EPG-WEB/cep-00:50:56:A0:77:88
            IP: 10.1.1.10
            >>>

Coming Soon
____

**The next release will feature configuration send . You can run it from you own program or just use**
**the python console. Simple easy methods inherited from our parent class in v1.0.0. Examples show below**


**Example 1 (Create Tenant: )**

            >>> call_class = ops.AciOpsSend(apic="192.168.1.1", username="JoeSmo", password="Help!")
            >>> create_tenant = call_class.create_tenant(tenant="Example")
            >>> call_class.view_tenants()
            ['Example']
            >>>

**Example 2 (Create App Profile: )**

            >>> create_app = call_class.create_app_profile(tenant="Example", app="Web")
            >>> call_class.create_app_profile()
            >>> call_class.create_app_profile(tenant="Example")
            (<Response [200]>, defaultdict(<class 'list'>, {'name': ['Web', 'None']}))
            >>>

**Example 3 (Create EPG: )**

            >>> call_class.create_epg(tenant="Example", app="Web", epg="Servers")
            (<Response [200]>, defaultdict(<class 'list'>, {'name': ['Servers']}))
            >>>

**Example 4 (Create BD: )**

            >>> call_class.create_bd_l3(tenant="Example", bd="L3BD", subnet="4.4.4.4/32")
            (<Response [200]>, defaultdict(<class 'list'>, {'name': ['L3BD']}))
            >>> call_class.subnet_finder(subnet="4.4.4.4/32")
            ('4.4.4.4/32', 'Example', 'L3BD', 'vrf', 'None', 'yes', 'private', 'proxy', 'None', 'None')
            >>>

**Example 5 (Create vrf: )**

            >>> call_class.create_vrf(tenant="Example", vrf="vrf-1")
            (<Response [200]>, defaultdict(<class 'list'>, {'vrf': ['vrf-1']}))
            >>>

**Example 6 (Enable Unicast Route: )**

            >>> call_class.enable_unicast(tenant="Example", bd="L3BD", enable="no") **yes/no**
            (<Response [200]>, '{"fvBD":{"attributes": {"name": "L3BD", "unicastRoute": "no"}}}')
            >>>

**Example 7 (Assign vrf to BridgeDomain: )**

            >>> call_class.vrf_to_bd(tenant="Example", bd="BDL3", vrf="vrf-1")
            (<Response [200]>, defaultdict(<class 'list'>, {'vrf': ['vrf-1']}))
            >>>

**Example 8 (Routing Scope: )**

            >>> call_class.routing_scope(tenant="Example", bd="BDL3", scope="private", subnet="4.4.4.4/32") **share|public|shared***
            (<Response [200]>, defaultdict(<class 'list'>, {'name': ['L3BD', 'BDL3']}), {'IP': 'uni/tn-Example/BD-BDL3/subnet-[4.4.4.4/32]',
            'Tenant': 'Example', 'BD': 'BDL3', 'vrf': 'vrf-1', 'L3Out': 'None', 'Route Enable': 'yes', 'Scope': 'private', 'Uni Flood': 'proxy',
            'APs': 'None', 'EPGs': 'None'})
            >>>
