import csv
import requests
import os

USER = ""
PASSWORD = ""
API_VERSION = ""
BASE_URL = ''
ATTRB = ''
ATTRB_REGEX = ""
CSV_HEADERS = ['hostname', 'protocol', 'folder', 'emulation']


def request_record_by_extattrb() -> None:
    """request record by extensble attribute"""

    with open(f'{os.path.dirname(os.path.realpath(__file__))}/devices.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)

    request_record = requests.get(
        f"https://{BASE_URL}/wapi/{API_VERSION}/record:host?_return_fields%2B=extattrs&*{ATTRB_REGEX}",
        auth=(USER, PASSWORD), verify=False)

    if request_record.status_code == 200:
        record = request_record.json()
        with open(f'{os.path.dirname(os.path.realpath(__file__))}/devices.csv', 'a', newline='') as file:
            for i in record:
                for k, v in i['extattrs'].items():
                    if k == ATTRB:
                        writer = csv.writer(file)
                        writer.writerow([i["name"], 'SSH2', v["value"], 'XTerm'])