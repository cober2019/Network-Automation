UnPackIps
==============
Description
--------------

IpRanges was designed for Network Engineer to quickly unpack IP ranges. The intention is to avoid spreadsheets, and other
methods of IP importing.

Dependency
__________

+ Python3

Usage
--------------
+ A pipe "|" separator is used to separate subnets within the string, and commas and dashes to expand IP addresses.

**Example 1: Unpacking IPs**

          >>> ips = get_ips(user_input="10.1.1.130, 131, 133| 192.168.1.22-50, 1|8.8.8.8")
          ['10.1.1.130', '10.1.1.131', '10.1.1.133', '192.168.1.22', '192.168.1.23', '192.168.1.24', '192.168.1.25', '192.168.1.26', '192.168.1.27', '192.168.1.28',
          '192.168.1.29', '192.168.1.30', '192.168.1.31', '192.168.1.32', '192.168.1.33', '192.168.1.34', '192.168.1.35', '192.168.1.36', '192.168.1.37'
          , '192.168.1.38', '192.168.1.39', '192.168.1.40', '192.168.1.41', '192.168.1.42', '192.168.1.43', '192.168.1.44', '192.168.1.45', '192.168.1.46', '192.168.1.47',
          '192.168.1.48', '192.168.1.49', '192.168.1.50', '192.168.1.1', '8.8.8.8']


**Example 2: Unpacking w/ Ping**

          >>> ping(user_input="10.1.1.130, 131, 133| 192.168.1.22, 1|8.8.8.8")
          10.1.1.130 up | Latency: 314ms Time: Mon, 19 Oct 2020 20:56:01 +0000
          10.1.1.130 up | Latency: 326ms Time: Mon, 19 Oct 2020 20:56:01 +0000
          10.1.1.130 up | Latency: 246ms Time: Mon, 19 Oct 2020 20:56:01 +0000
          10.1.1.130 up | Latency: 269ms Time: Mon, 19 Oct 2020 20:56:01 +0000
          _
          10.1.1.131 up | Latency: 332ms Time: Mon, 19 Oct 2020 20:56:05 +0000
          10.1.1.131 up | Latency: 251ms Time: Mon, 19 Oct 2020 20:56:05 +0000
          10.1.1.131 up | Latency: 274ms Time: Mon, 19 Oct 2020 20:56:05 +0000
          10.1.1.131 up | Latency: 296ms Time: Mon, 19 Oct 2020 20:56:05 +0000
          _
          !!! 10.1.1.133 Request timed out. | Status: Down | Time: Mon, 19 Oct 2020 20:56:24 +0000 !!!
          !!! 10.1.1.133 Request timed out. | Status: Down | Time: Mon, 19 Oct 2020 20:56:24 +0000 !!!
          !!! 10.1.1.133 Rsquest timed out. | Status: Down | Time: Mon, 19 Oct 2020 20:56:24 +0000 !!!
          !!! 10.1.1.133 Rsquest timed out. | Status: Down | Time: Mon, 19 Oct 2020 20:56:24 +0000 !!!
          _
          192.168.1.22 up | Latency: 180ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          192.168.1.22 up | Latency: 203ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          192.168.1.22 up | Latency: 226ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          192.168.1.22 up | Latency: 145ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          _
          192.168.1.1 up | Latency: 142ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          192.168.1.1 up | Latency: 125ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          192.168.1.1 up | Latency: 187ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          192.168.1.1 up | Latency: 214ms Time: Mon, 19 Oct 2020 20:56:30 +0000



**All ping output saved to log with latency**

          >>> INFO:root:
          192.168.156.22 up | Latency: 180ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          INFO:root:
                    192.168.1.22 up | Latency: 203ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          INFO:root:
                    192.168.1.22 up | Latency: 226ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          INFO:root:
                    192.168.1.22 up | Latency: 145ms Time: Mon, 19 Oct 2020 20:56:27 +0000
          INFO:root:
                    192.168.1.1 up | Latency: 142ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          INFO:root:
                    192.168.1.1 up | Latency: 125ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          INFO:root:
                    192.168.1.1 up | Latency: 187ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          INFO:root:
                    192.168.1.1 up | Latency: 214ms Time: Mon, 19 Oct 2020 20:56:30 +0000
          INFO:root:
                    8.8.8.8 up | Latency: 35ms Time: Mon, 19 Oct 2020 20:56:33 +0000
          INFO:root:
                    8.8.8.8 up | Latency: 39ms Time: Mon, 19 Oct 2020 20:56:33 +0000
          INFO:root:
                    8.8.8.8 up | Latency: 37ms Time: Mon, 19 Oct 2020 20:56:33 +0000
          INFO:root:
                    8.8.8.8 up | Latency: 43ms Time: Mon, 19 Oct 2020 20:56:33 +0000
