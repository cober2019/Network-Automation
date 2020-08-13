Encap Finder
==============
**Description**
--------------

 Use EncapFinder to find where a encapsulation is assigned and what policies its associtied with.
  

**Usages**
___________

**Just simply input your apic, username, and password when prompted.**

           >>> APIC: 192.168.1.1
               Username: JoeSmo
               Password: Bananas
               
**Enter desired encap when prompted:**

           >>> |-Target Encap
               |---------------------------------|
               Encap: 2000
               
**EPG Attached Encapsulation:**

           >>>   Access Policy Details:
                 VLAN Pool(s): Pool-1
                               Pool-2
                               Pool-3
                 Domain(s):    PhyDom-1
                               PhyDom-2
                               PhyDom-3
                               PhyDom-4
                               PhyDom-5
                 AAEP(s):      aaep-1
                               aaep-2
                               aaep-3
                               aaep-4
                               aaep-5
                 Encap Loc.:   Tenant: Internet
                               App Profile: Internet-Transit
                               EPG: Internet-Endpoints
                 Path Attach:  Path: 101-102: Firewall-1
                               Path: 101-102: Firewall-2
                               Path: 101-102: VPN-1
                               Path: 101-102: VPN-2
                               Path: 101: eth1/30

           
**Tenant L3Out Encapsulation:**

            >>>    Access Policy Details:
                   VLAN Pool(s): Pool-1
                                 Pool-2
                   Domain(s):    Dom-1
                                 DOM-1
                                 DOM-1
                   AAEP(s):      AEP-1
                                 AEP-2
                                 AEP-3
                   Encap Loc:    Tenant: DMZ
                                 L3Out: Internet-Edge
                                 Interface: IFP-SVI1000
                   Path Attach:  EP: Edge-RTR-01
                                 EP: Edge-RTR-02


    
