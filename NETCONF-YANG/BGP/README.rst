NETCONF BGP (Under Development)
==========================

Description
___________

  **This program currently allows you to view certain BGP configuration. Viewable options shown below**
  
  
          >>> 
             Local AS: 12345
                _
                Neighbors
                      _
                      Remote AS: 12345
                       Neighbor: 2.2.2.2
                  Next-Hop-Self: No
                Route-Reflector: No
                  Soft-Reconfig: No
                      _
                      Remote AS: 54321
                       Neighbor: 10.1.1.1
                  Next-Hop-Self: No
                Route-Reflector: No
                  Soft-Reconfig: No
                  _
             Address Family: unicast -------
                _
                AF Neighbor Information:
                _
                       Neighbor: 2.2.2.2   
                  Next-Hop-Self: Yes
                Route-Reflector: Yes
                      Route-Map: None           Direction: None
                    Prefix-list: None           Direction: None
                       Activate: Yes
                       _
                       Neighbor: 10.1.1.1  
                  Next-Hop-Self: No
                Route-Reflector: No
                      Route-Map: None           Direction: None
                    Prefix-list: None           Direction: None
                       Activate: Yes
                       _
                AF Redistribution:
                        _
                        Protocol: connected
                        _
                        Protocol: ospf  20
                       Route-map: None             Metric: None
                        _
                        Protocol: static 
                       Route-map: None             Metric: 30
                       _
                AF Network Statements:
                         _
                         Network:    1.1.1.0  Mask: 255.255.255.0
                         Network:    3.3.3.0  Mask: 255.255.255.0
                         Network:   10.0.0.0  Mask: 255.255.255.0
                         _
             End Program, Press Enter to Close
