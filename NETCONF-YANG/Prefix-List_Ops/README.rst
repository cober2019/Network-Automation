Prefix-List Operations
==============
Description
--------------

Prefix-List Ops has the following features:

+ View prefix-list
+ Find Prefix
+ Send Prefix Statements

Depedency Modules
__________

+ ipaddress
+ re
+ xmltodict
+ ncclient
+ netmiko

Device Modules Tested
---------------

**Different device modules return different configuration/XML. I've tested on the following**

+ ISR 4331
+ Catalyst 3850

Usage
--------------


**View Prefix Lists**

            >>> view_prefix_list(username="cisco", password="cisco", host="10.10.10.1")
            Test1
                        5 permit 192.168.1.0/24
                        10 permit 192.168.2.0/24
                        20 permit 10.10.10.0/24 25 27
                        30 permit 10.10.11.0/24 25 27
                        40 permit 10.10.12.0/24 25 27
            Test2
                        5 permit 172.16.1.0/24
                        10 permit 172.16.1.0/24 25 30
                        15 permit 172.16.2.0/24 25 30

**Find Perfix**

            >>> find_prefix(username="cisco", password="cisco", host="10.10.10.1", prefix="10.10.12.0/24")
            List: Test1
                        Seq: 40
                        Prefix: 10.10.12.0/24

**Sending Prefixes**

    **Send with prefix only**

            >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1", name="HelpMe", prefix="192.168.1.0/24", seq="5", action="permit")
            HelpMe
                5 permit 192.168.1.0/24

    **Send with prefix and ge**

            >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1", name="HelpMe", prefix="192.168.2.0/24", seq="10", action="permit", ge="26")
            HelpMe
                5 permit 192.168.1.0/24
                10 permit 192.168.2.0/24 26

    **Send with prefix, ge, le**

            >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1", name="HelpMe", prefix="192.168.3.0/24", seq="15", action="permit", ge="26", le="32")
            HelpMe
                5 permit 192.168.1.0/24
                10 permit 192.168.2.0/24 26
                15 permit 192.168.3.0/24 26 32

**When sending new prefixes, the following checks will be done**

    **Seqeunce Check**

        >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1", name="HelpMe", prefix="172.16.1.0/24", seq="5", action="permit")
        Traceback (most recent call last):
          File "<input>", line 1, in <module>
          File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 422, in send_prefix_list
            raise ValueError("Sequence Exist")
        ValueError: Sequence Exist

    **Prefix Check**

        >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1", name="HelpMe", prefix="192.168.1.0/24", seq="20", action="permit")
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 424, in send_prefix_list
                raise ValueError("Prefix Exist")
            ValueError: Prefix Exist

    **Overlapping Prefix Check**

        >>> send_prefix_list(, name="HelpMe", prefix="192.168.1.0/26", seq="20", action="permit")
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 502, in send_prefix_list
                self._find_dups_internal(prefix=kwargs["prefix"])
              File "C:\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 561, in _find_dups_internal
                raise ValueError("{} overlapps with {}".format(kwargs["prefix"], network))
            ValueError: 192.168.1.0/26 overlaps with 192.168.1.0/2
   
**Routing Table Check**
    **Using netmiko to get the routing table, the prefix is compared to the destination prefixes. If the prefix is**
    **external the program will warn you of this. If your selection no, the prefix will be canceled and an expection will**
    **be thrown. If yes, the prefix will be added to the list.**

        >>> send_prefix_list(username="cisco", password="cisco", host="10.10.10.1",name="HelpMe", prefix="10.10.12.0/24", seq="30", action="permit")
        Prefix is external/not local, Are you sure you want to add (yes/no)?
        no
        Traceback (most recent call last):
          File "<input>", line 1, in <module>
          File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 442, in send_prefix_list
            raise ValueError("Prefix configuration aborted")
        ValueError: Prefix configuration aborted

