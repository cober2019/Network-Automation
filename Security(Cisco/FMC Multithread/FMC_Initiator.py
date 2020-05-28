import socket
import FMC
import ipaddress
from multiprocessing import  Process
import  time

nic_list = []

def get_nic_ip():
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    for i in addrs:
        for i in i:
            try:
                nic_list.append(ipaddress.IPv4Address(i[0]))
            except (TypeError, IndexError, ValueError):
                continue

    return  nic_list

# Credentials and FMC go is the funtion variables. Each username and password need to be unique

def initiate_1(ip):

    net_loc = "1.1.1.1"
    username = "admin1"
    password = "admin"

    initiate_1 = FMC.fmc()
    initiate_1.username = username
    initiate_1.password = password
    initiate_1.net_loc = net_loc
    initiate_1.query = "?offset=1&limit=250"
    initiate_1.ip = ip
    initiate_1.get_rules()

def initiate_2(ip):

    net_loc = "1.1.1.1"
    username = "admin2"
    password = "admin"


    initiate_2 = FMC.fmc()
    initiate_2.username = username
    initiate_2.password = password
    initiate_2.net_loc = net_loc
    initiate_2.query = "?offset=501&limit=250"
    initiate_2.ip = ip
    initiate_2.get_rules()

def initiate_3(ip):

    net_loc = "1.1.1.1"
    username = "admin3"
    password = "admin"


    initiate_3 = FMC.fmc()
    initiate_3.username = username
    initiate_3.password = password
    initiate_3.net_loc = net_loc
    initiate_3.query = "?offset=1001&limit=250"
    initiate_3.ip = ip
    initiate_3.get_rules()

if __name__ == '__main__':

    process_1 = Process(target=initiate_1, args=("10.1.3.249",))
    process_1.start()
    time.sleep(10)
    process_2 = Process(target=initiate_2, args=("10.1.3.250",))
    process_2.start()
    time.sleep(10)
    process_3 = Process(target=initiate_3, args=("10.1.3.251",))
    process_3.start()
    stop = input("")
