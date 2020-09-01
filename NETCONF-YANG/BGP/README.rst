NETCONF BGP (Under Development)
==========================

Description
___________

  This program currently allows you to view certain BGP configuration. All avaible output option are show in the example below,
  
  
          >>> -----------------------
              Local AS: 12345 -------
                 Neighbors
                       Remote AS: 12345
                        Neighbor: 2.2.2.2
                   Next-Hop-Self: No
                 Route-Reflector: No
                   Soft-Reconfig: No
                       Remote AS: 54321
                        Neighbor: 10.1.1.1
                   Next-Hop-Self: No
                 Route-Reflector: No
                   Soft-Reconfig: No
              Address Family: unicast
                 AF Neighbor Information:
                        Neighbor: 2.2.2.2   
                       Route-Map: None           Direction: None
                     Prefix-list: None           Direction: None
                        Activate: Yes
                        Neighbor: 10.1.1.1  
                       Route-Map: None           Direction: None
                     Prefix-list: None           Direction: None
                        Activate: Yes
                 AF Redistribution:
                         Protocol: connected      Route-map: None
                         Protocol: ospf           Route-map: None
                 AF Network Statements:
                          Network:    1.1.1.0  Mask: 255.255.255.0
                          Network:    3.3.3.0  Mask: 255.255.255.0
                          Network:   10.0.0.0  Mask: 255.255.255.0
              End Program, Press Enter to Close
