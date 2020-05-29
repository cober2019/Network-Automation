import re
from urllib.parse import urlparse
import  time
import ipaddress
import  random
import socket
import base64
import ssl
import json
import FMC

# Gather all IPs from host, store to list

context = ssl._create_unverified_context()
port = 443
chunk_size = 4096
log_file = "C:\\Python\log.txt"

class contact_fmc():

    def __init__(self):

        self.username = None
        self.password = None
        self.net_loc = None
        self.ip = None
        self.status = None

    def post(self, path):

        str_cred = str.encode("{}:{}".format(self.username, self.password))
        creds = base64.b64encode(b'' + str_cred).decode("ascii")
        try:

            create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
            bind_addr_socket = create_socket.bind((self.ip, 0))

            with socket.create_connection((self.net_loc, port)) as sock:
                with context.wrap_socket(sock, server_hostname= self.net_loc) as ssock:

                    http_type = 'POST {} HTTP/1.1\r\nHost:{}\r\nAuthorization: Basic {}\r\n\r\n'.format(path,   self.net_loc, creds)
                    ssock.send(http_type.encode())
                    response = ssock.recv(4096)
                    parsed_data = contact_fmc.parse_api_auth(self, response)
                    ssock.close()

        except socket.gaierror:
            return  None
        else:
            return parsed_data

    def get(self, *args):
        str_cred = str.encode("{}:{}".format(self.username, self.password))
        creds = base64.b64encode(b'' + str_cred).decode("ascii")
        try:

            create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
            bind_addr_socket = create_socket.bind((self.ip, 0))

            with socket.create_connection((self.net_loc, port))as sock:
                with context.wrap_socket(sock, server_hostname=self.net_loc) as ssock:

                    parse =  urlparse(args[0])

                    if parse[4] != "":
                        http_type = 'GET {}?{} HTTP/1.1\r\nHost:{}\r\nAuthorization: Basic {}\r\nX-auth-access-token: {}\r\nX-auth-refresh-token: {}\r\n\r\n'.format(parse[2], parse[4], self.net_loc, creds, args[1], args[2])
                    else:
                        http_type = 'GET {} HTTP/1.1\r\nHost:{}\r\nAuthorization: Basic {}\r\nX-auth-access-token: {}\r\nX-auth-refresh-token: {}\r\n\r\n'.format(parse[2], self.net_loc, creds, args[1], args[2])

                    ssock.send(http_type.encode())
                    chunks = [ ]
                    while True:
                        chunk =  ssock.recv(chunk_size)
                        if chunk == b'':
                            ssock.close()
                            break
                        elif chunk == b'0\r\n\r\n':
                            continue
                        chunks.append(chunk)
                    parsed_data = contact_fmc.parse_reponse(self, b"".join(chunks))

        except socket.gaierror:
            return  None
        else:
            return parsed_data

    def parse_reponse(self, data):

        status_dict = {}
        decode = str(data)
        find_headers = decode.replace("\\r", "")
        req_status = re.findall(r'(?<=HTTP/1.1 )[1-9][0-9][0-9](?=\s)', find_headers)
        req_content = re.findall(r' (?<='+ req_status[0] + '\s'').*', find_headers)
        status_dict[req_status[0]] = req_content[0]
        odd_value = re.findall(r'(?<=\\r\\n\\r\\n).*(?=\\r\\n{)', decode)

        try:
            file = open(log_file, 'a+')
            file.write(decode + "\n\n")
        except (FileNotFoundError, FileExistsError):
            pass

        try:

            header,_,body = decode.partition('\\r\\n\\r\\n' + odd_value[0] + '\\r\\n')

            if "\\r\\n\'" in body:
                strip_res = body.replace("\\r\\n\'", "")
            if "\\r\\n\']" in body:
                strip_res = strip_res.replace("\\r\\n\']", "")
            if "\\" in body:
                strip_res = strip_res.replace("\\", "")
            if "\\r\\n0\\r\\n\\r\\n\'" in body:
                strip_res = strip_res.replace("\\r\\n0\\r\\n\\r\\n\'", "")
            if "rn1rn" in strip_res:
                strip_res = strip_res.replace("rn1rn", "")

            load_response = json.loads(strip_res)

        except (IndexError, UnboundLocalError, json.JSONDecodeError):
            stop = input("Error")
            return  None
        else:
            return load_response


    def parse_api_auth(self, response):

        header_dict = {}
        status_dict = {}
        res = response.decode()
        try:
            find_headers = res.replace("\r", "")
            req_status = re.findall(r'(?<=HTTP/1.1 )[1-9][0-9][0-9](?=\s)', find_headers)
            req_content = re.findall(r' (?<='+ req_status[0] + '\s'').*', find_headers)
            status_dict[req_status[0]] = req_content[0]
            http_status = [k for k in status_dict]
            self.status = http_status[0]

            header_keys = re.findall(r'[a-zA-Z].*(?=:)', find_headers)
            header_vals = re.findall(r'(?<=:\s).*(?=\s)', find_headers)

            for head, val in zip(header_keys, header_vals):
                header_dict[head] = val

        except  (IndexError, UnboundLocalError) as error:
            return None
        else:
            return  header_dict["X-auth-access-token"], header_dict["X-auth-refresh-token"], header_dict["DOMAIN_UUID"]