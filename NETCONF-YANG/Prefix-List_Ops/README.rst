Prefix-List Operations (Coming Soon!)
==============
Description
--------------

Prefix-List Ops has the following features:

+ View prefix-list
+ Find prefix by prefix or prefix length
+ Find overlapping prefixes in the same list (ge, le)
+ Find duplicate prefixes in different list

Depedency Modules
__________

+ ipaddress
+ re
+ collections
+ xmltodict
+ ncclient
+ socket
+ netmiko

Device Modules Tested
---------------

**Different device modules return different configuration/XML. I've tested on the following**

+ ISR 4331
+ ASR 1001-X
+ Catalyst 3850

Usage
--------------

**Import**
            >>> import IPOperations.isr_lists as ipops

**Create Objects/Call Class**

            >>> call_class = ipops.IpOps(host="10.48.1.130", username="cisco", password="cisco")
            print(call_class)
            <IPOperations.isr_lists.IpOps object at 0x0000024A786C8248>

**View Prefix Lists**

            >>> call_class.view_prefix_list()
            local-prefixes
            5 permit 1.1.1.0/24 25
            10 permit 3.1.1.0/26 27
            15 permit 2.1.1.0/26 27

**Find Prefix Length**

            >>> call_class.find_prefix_length(length="25")
            defaultdict(<class 'list'>, {'test22': [{'seq': '25', 'prefix': '1.1.1.0/25'},
            {'seq': '30', 'prefix': '2.2.2.0/25'}],
            'test23': [{'seq': '25', 'prefix': '1.1.1.0/25'},
            {'seq': '30', 'prefix': '2.2.2.0/25'}]})

**Find Perfix**

            >>> call_class.find_prefix(prefix="1.1.1.0/24")
            defaultdict(<class 'list'>, {'local-prefixes': [{'seq': '5', 'prefix': '1.1.1.0/24'}],
            'test22': [{'seq': '5', 'prefix': '1.1.1.0/24'}],
            'test23': [{'seq': '5', 'prefix': '1.1.1.0/24'}]})

**Find Overlapping Prefixes**

            >>> call_class.find_overlapping_prefixes()
            defaultdict(<class 'list'>,
            {'local-prefixes': [OrderedDict([('prefix', '1.1.1.0/24'), ('overlapping-seq', '5'), ('ge', '25'), ('le', '32'), ('overlapping-prefixes', ['1.1.1.0/25', '1.1.1.0/26', '1.1.1.0/27', '1.1.1.0/28', '1.1.1.0/29', '1.1.1.0/30', '1.1.1.0/31', '1.1.1.0/32'])]),
            OrderedDict([('prefix', '1.1.1.0/25'), ('overlapping-seq', '5'), ('ge', '25'), ('le', '32'), ('overlapping-prefixes', ['1.1.1.0/25', '1.1.1.0/26', '1.1.1.0/27', '1.1.1.0/28', '1.1.1.0/29', '1.1.1.0/30', '1.1.1.0/31', '1.1.1.0/32'])]),
            OrderedDict([('prefix', '1.0.0.0/8'), ('overlapping-seq', '5'), ('ge', '25'), ('le', '32'), ('overlapping-prefixes', ['1.1.1.0/25', '1.1.1.0/26', '1.1.1.0/27', '1.1.1.0/28', '1.1.1.0/29', '1.1.1.0/30', '1.1.1.0/31', '1.1.1.0/32'])]),
            OrderedDict([('prefix', '3.1.1.0/26'), ('overlapping-seq', '10'), ('ge', '27'), ('le', '32'), ('overlapping-prefixes', ['3.1.1.0/27', '3.1.1.0/28', '3.1.1.0/29', '3.1.1.0/30', '3.1.1.0/31', '3.1.1.0/32'])]),
            OrderedDict([('prefix', '2.1.1.0/26'), ('overlapping-seq', '15'), ('ge', '27'), ('le', '32'), ('overlapping-prefixes', ['2.1.1.0/27', '2.1.1.0/28', '2.1.1.0/29', '2.1.1.0/30', '2.1.1.0/31', '2.1.1.0/32'])]),
            OrderedDict([('prefix', '4.1.1.0/26'), ('overlapping-seq', '20'), ('ge', '27'), ('le', '32'), ('overlapping-prefixes', ['4.1.1.0/27', '4.1.1.0/28', '4.1.1.0/29', '4.1.1.0/30', '4.1.1.0/31', '4.1.1.0/32'])]),
            OrderedDict([('prefix', '5.1.1.0/26'), ('overlapping-seq', '25'), ('ge', '27'), ('le', '32'), ('overlapping-prefixes', ['5.1.1.0/27', '5.1.1.0/28', '5.1.1.0/29', '5.1.1.0/30', '5.1.1.0/31', '5.1.1.0/32'])]),
            OrderedDict([('prefix', '6.1.1.0/26'), ('overlapping-seq', '30'), ('ge', '27'), ('le', '32'), ('overlapping-prefixes', ['6.1.1.0/27', '6.1.1.0/28', '6.1.1.0/29', '6.1.1.0/30', '6.1.1.0/31', '6.1.1.0/32'])]),
            OrderedDict([('prefix', '7.1.1.0/26'), ('overlapping-seq', '35'), ('le', '27'), ('overlapping-prefixes', ['7.1.1.0/27', '7.1.1.0/25', '7.1.1.0/24'])])],

        **View Overlapping Prefixes, Formatted**

        >>> call_class.view_overlapping_prefixes()
        local-prefixes
        Prefix: 1.1.1.0/24
        Overlapping Sequence: 5
        Range: GE: 25
        Range: LE 32
        Overlapping Prefixes: 1.1.1.0/25, 1.1.1.0/26, 1.1.1.0/27, 1.1.1.0/28, 1.1.1.0/29, 1.1.1.0/30, 1.1.1.0/31, 1.1.1.0/32
        Prefix: 1.1.1.0/25
        Overlapping Sequence: 5
        Range: GE: 25
        Range: LE 32
        Overlapping Prefixes: 1.1.1.0/25, 1.1.1.0/26, 1.1.1.0/27, 1.1.1.0/28, 1.1.1.0/29, 1.1.1.0/30, 1.1.1.0/31, 1.1.1.0/32
        Prefix: 1.0.0.0/8
        Overlapping Sequence: 5
        Range: GE: 25
        Range: LE 32
        Overlapping Prefixes: 1.1.1.0/25, 1.1.1.0/26, 1.1.1.0/27, 1.1.1.0/28, 1.1.1.0/29, 1.1.1.0/30, 1.1.1.0/31, 1.1.1.0/32

**View Duplicate Prefixes**

        >>> call_class.duplicate_prefix()
        defaultdict(<class 'list'>, {'prefixes': [defaultdict(<class 'list'>,
        {'local-prefixes': [{'seq': '5', 'prefix': '1.1.1.0/24'}],
        'test22': [{'seq': '5', 'prefix': '1.1.1.0/24'}],
        'test23': [{'seq': '5', 'prefix': '1.1.1.0/24'}]})

**View Routing Prefixes (No next hop)**
**Example only shows local and connected. The method will display all routing protocols and types if configured**

        >>> call_class.get_routing_table()
        >>> call_class.routing_prefixes
        {'1.0.0.0/8': 'C', '1.1.1.1/32': 'L', '4.0.0.0/8': 'L', '4.4.4.0/24': 'C', '4.4.4.4/32': 'L', '5.0.0.0/8': 'L',
            '5.5.5.0/24': 'C', '5.5.5.5/32': 'L', '6.0.0.0/8': 'L', '6.6.6.0/24': 'C', '6.6.6.6/32': 'L', '7.0.0.0/8': 'L',
        '7.7.7.0/24': 'C', '7.7.7.7/32': 'L', '8.0.0.0/8': 'L', '8.8.8.0/24': 'C', '8.8.8.8/32': 'L', '9.0.0.0/8': 'L',
        '9.9.9.0/24': 'C', '9.9.9.9/32': 'L', '10.0.0.0/8': 'L', '10.1.3.0/24': 'S', '10.10.10.0/24': 'C', '10.10.10.10/32': 'L',
        '10.10.11.0/24': 'C', '10.10.11.1/32': 'L', '192.168.1.0/24': 'C'}

**Sending Prefixes**

    **Send with prefix only**

            >>> call_class.send_prefix_list(name="HelpMe", prefix="192.168.1.0/24", seq="5", action="permit")
            HelpMe
                5 permit 192.168.1.0/24

    **Send with prefix and ge**

            >>> call_class.send_prefix_list(name="HelpMe", prefix="192.168.2.0/24", seq="10", action="permit", ge="26")
            HelpMe
                5 permit 192.168.1.0/24
                10 permit 192.168.2.0/24 26

    **Send with prefix, ge, le**

            >>> call_class.send_prefix_list(name="HelpMe", prefix="192.168.3.0/24", seq="15", action="permit", ge="26", le="32")
            HelpMe
                5 permit 192.168.1.0/24
                10 permit 192.168.2.0/24 26
                15 permit 192.168.3.0/24 26 32

**When sending new prefixes, the following checks will be done**

    **Seqeunce Check**

        >>> call_class.send_prefix_list(name="HelpMe", prefix="172.16.1.0/24", seq="5", action="permit")
        Traceback (most recent call last):
          File "<input>", line 1, in <module>
          File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 422, in send_prefix_list
            raise ValueError("Sequence Exist")
        ValueError: Sequence Exist

    **Prefix Check**

        >>> call_class.send_prefix_list(name="HelpMe", prefix="192.168.1.0/24", seq="20", action="permit")
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 424, in send_prefix_list
                raise ValueError("Prefix Exist")
            ValueError: Prefix Exist

    **Overlapping Prefix Check**

        >>> call_class.send_prefix_list(name="HelpMe", prefix="192.168.1.0/26", seq="20", action="permit")
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File "C:\Users\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 502, in send_prefix_list
                self._find_dups_internal(prefix=kwargs["prefix"])
              File "C:\JoeSmo\PycharmProjects\IPOperations\IPOperations\isr_lists.py", line 561, in _find_dups_internal
                raise ValueError("{} overlapps with {}".format(kwargs["prefix"], network))
            ValueError: 192.168.1.0/26 overlaps with 192.168.1.0/24

