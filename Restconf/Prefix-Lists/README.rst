XE Prefix-List Ops
==================

This is a program  that allows you to view, and check prefix-lists. **This program does not modify your device config**:

- View current prefix-lists
- Find a prefix in the device prefix-list
- Find a prefix in the routing table
- Propose a prefix and check it against the current lists
- Find overlapping prefix in all prefix-lists


YANG Models:
------------
**RESTCONF REQUIRED!**

- Cisco-IOS-XE-native:native/ip/prefix-list
- Cisco-IOS-XE-native:native/ip/prefix-lists
- ietf-routing:routing-state

Tested Devices:
------------

- ASR
- CSR
- ISR
- CATALYST 3000 Series

Menu Options:
-------------
1. View Prefix-lists
2. Find Prefix
3. Check Overlapping, User Selected Prefix
4. Check All List For Overlapping
5. Find Prefix in RIB
6. Back To Login

**View All Lists:**

.. image:: https://github.com/cober2019/xe-prefix-list-ops/blob/main/images/prefix-op-1.PNG

**Find a Proposed Prefix:**

.. image:: https://github.com/cober2019/xe-prefix-list-ops/blob/main/images/prefix-ops-3.PNG

**Find a Prefix:**

.. image:: https://github.com/cober2019/xe-prefix-list-ops/blob/main/images/prefix-ops-2.PNG
