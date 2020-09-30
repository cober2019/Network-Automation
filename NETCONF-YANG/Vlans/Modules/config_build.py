"""Helper class that creates vlan conigurations with XML"""

from os import system, name
import xml.etree.cElementTree as xml
from ncclient import manager
import xmltodict
from Database import ormdb
import Modules.connection as ConnectWith
import Modules.main_funtions
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def clear() -> None:
    """Clears terminal"""

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

def view_vlans_db(db_ops) -> None:
    """View and print vlans in database"""

    print("\nVlans:\n")
    print(f"{'VLAN':<2}{'Name':>14}{'Description':>20}\n------------------------------------------\n")
    for vlan_id  in db_ops.session.query(ormdb.Vlans).order_by(ormdb.Vlans.vlan):
        print(f"{vlan_id.vlan:<2}{vlan_id.vlan_name:>14}{vlan_id.vlan_description:>20}")
    print("\n")


def sync_device_vlan_to_db(vlans, db_ops) -> None:
    """Check router for vlan, if vlan not in DB, insert vlan in DB"""

    def check_vlan_name(vlan, vlan_id):
        """Updates vlan db entry if vln name is different"""

        # If vlan in DB but name is different, UPDATE
        if vlan.get('id') == vlan_id.vlan:
            if vlan_id.vlan_name != vlan.get("name"):
                db_ops.db_vlan_name_update(vlan.get('id'), vlan.get('name'))

    for vlan in vlans:
        # Query for vlan ID, if query return 0, insert into DB
        query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(vlan.get('id')))).count()
        if query == 0:
            db_ops.db_vlan_insert(vlan.get('id'), vlan.get('name'), "Added From Device")
        else:
            # Check if DB VLANS DB entries need UPDATE
           [check_vlan_name(vlan, vlan_id) for vlan_id in db_ops.session.query(ormdb.Vlans).order_by(ormdb.Vlans.vlan)]

class BuildConfig:
    """Helper class that creates vlan conigurations with XML"""
    
    def __init__(self):

        self._vl_id_input = None
        self._vl_name_input = None
        self._vl_descr_input = None
        self._item_update= None
        self._username = None
        self._password = None
        self._host = None
        self._netconf_session = None
        self._netmiko_session = None
        self.config_marker = 0

        self._root = xml.Element("config")
        self._root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self._root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.vlan_element = xml.SubElement(self.native_element, "vlan")
        self.span_element = xml.SubElement(self.native_element, "spanning-tree")


    def reset(self) -> None:
        """Reset configuration instance attributes"""

        self.root = xml.Element("config")
        self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.vlan_element = xml.SubElement(self.native_element, "vlan")
        self.span_element = xml.SubElement(self.native_element, "spanning-tree")

    def get_netmiko_vlans(self, db_ops) -> None:
        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        vlans = []

        try:
            get_vlans = self.netmiko_session.send_command(command_string="show vlan brief")
        except OSError as error:
            logging.exception(f"{error}", exc_info=True)
            print(f"\n{error}")
            main_funtions.main()

        # Parse netmiko vlan reponse
        cli_line = get_vlans.split("\n")
        for line in cli_line:
            if not list(enumerate(line.split(), 0)):
                continue
            if line.split()[0] == "VLAN":
                continue
            if line.split()[0].rfind("-") != -1:
                continue
            if int(line.split()[0]) not in range(1002, 1005 + 1):
                vlans.append({'id': line.split()[0], 'name': line.split()[1]})

        # Converts netmiko vlans to YANG, sends to device. Current YANG model has  2 different tags to configure/view vlans.
        if self.config_marker != 1:
            self.reset()
            clear()
            print("Converting CLI Configuration to XML Configuration. Re-applying, Standby...")
            [self._convert_and_create_vlans(db_ops, vlan_id=vlan.get('id'), vlan_name=vlan.get('name')) for vlan in vlans]
            # Set instance attrb to 1 so latter process doesn't happen until a new object is created
            self.config_marker = 1
            print("Conversion Complete")
            clear()

        # Sync netmiko vlans to DB
        sync_device_vlan_to_db(vlans, db_ops)

    def _convert_and_create_vlans(self, db_ops, vlan_id=None, vlan_name=None) -> None:
        """Create XML vlan configuration """


        vlan_list = xml.SubElement(self.vlan_element, "vlan-list")
        vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")
        vl_id = xml.SubElement(vlan_list, "id")
        vl_id.text = str(vlan_id)
        vl_name = xml.SubElement(vlan_list,"name")
        vl_name.text = vlan_name

        ConnectWith.send_configuration_lite(self.root, self.netconf_session)
        self.reset()

    def create_vlans(self, db_ops) -> None:
        """Create XML vlan configuration """

        view_vlans_db(db_ops)

        # Get current vlans from device, used for check later
        while True:
            try:
                self._vl_id_input = int(input("VLAN: "))
                # Check if vlan exist in DB
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                if query > 0:
                    print("Vlan Exist")
                    continue
                # Verify vlan is valid
                elif self._vl_id_input not in range(1, 4097 + 1):
                    print(f"Invalid ID, range must between 1-4097")
                    continue
                else:
                    self._vl_name_input = input("VLAN name: ")
                    self._xml_config_code(self._vl_id_input, self._vl_name_input)
                    self._vl_descr_input = input("VLAN Description: ")
                    break
            except ValueError:
                print("Invalid Vlan")
                continue


    def create_from_database(self, db_ops) -> None:
        """Create XML vlan configuration via DB updates"""

        view_vlans_db(db_ops)

        while True:
            try:
                self._vl_id_input = int(input("VLAN: "))
                # Check if vlan exist in DB
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                if query > 0:
                    print("Vlan Exist")
                    continue
                # Verify vlan is valid
                elif self._vl_id_input not in range(1, 4097 + 1):
                    print(f"Invalid ID, range must between 1-4097")
                    continue
                else:
                    break
            except ValueError:
                print("Invalid Vlan")
                continue

        while True:
            self._vl_name_input = input("VLAN name: ")
            query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_name.like(self._vl_name_input)).count()
            if query > 0:
                print("Vlan Name Exist")
                continue
            else:
                break

        while True  :
            self._vl_descr_input = input("VLAN Description: ")
            query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_description.like(self._vl_descr_input)).count()
            if query > 0:
                print("Vlan Description Exist")
                continue
            else:
                break

        db_ops.db_vlan_insert(self._vl_id_input, self._vl_name_input, self._vl_descr_input)
        # Read DB, create config and return config to caller
        for vlan_id, vlan_char in db_ops.session.query(ormdb.Vlans.vlan, ormdb.Vlans.vlan_name):
            if str(self._vl_id_input) == vlan_id:
                self._xml_config_code(vlan_id, vlan_char)
                break


    def update_from_database(self, db_ops) -> str:
        """Updates XML vlan configuration from DB updates"""

        view_vlans_db(db_ops)

        while True:
            try:
                self._vl_id_input = int(input("VLAN: "))
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                if query == 0:
                    print("Vlan Doesn't Exist")
                    continue
                # Verify vlan is valid
                if self._vl_id_input not in range(1, 4097 + 1):
                    print(f"Invalid ID, range must between 1-4097")
                    continue
                else:
                    break
            except ValueError:
                print("Invalid Vlan")
                continue
                
        print("1. Name\n2. Description\n")
        selection = input("Selection: ")

        if selection == "1":

            while True:
                self._vl_name_input = input("VLAN name: ")
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_name.like(self._vl_name_input)).count()
                if query > 0:
                    print("Vlan Name Exist")
                    continue
                else:
                    break

            db_ops.db_vlan_name_update(self._vl_id_input, self._vl_name_input)
            for vlan_id, vlan_char in db_ops.session.query(ormdb.Vlans.vlan, ormdb.Vlans.vlan_name):
                if str(self._vl_id_input) == vlan_id:
                    self._xml_config_code(self._vl_id_input, vlan_char)
                    break

        elif selection == "2":

            while True:
                self._vl_descr_input = input("VLAN Description: ")
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_description.like(self._vl_descr_input)).count()
                if query > 0:
                    print("Vlan Description Exist")
                    continue
                else:
                    break

            for vlan_id in db_ops.session.query(ormdb.Vlans.vlan):
                if str(self._vl_id_input) == vlan_id.vlan:
                    db_ops.db_desc_vlan_update(vlan_id.vlan, self._vl_descr_input)
                    break

        return selection

    def delete_from_router(self, db_ops) -> None:
        """Builds and deletes vlan configuration via xml"""

        view_vlans_db(db_ops)

        while True:
            try:
                self._vl_id_input = int(input("VLAN: "))
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                if query == 0:
                    print("Vlan Doesn't Exist")
                    continue
                # Verify vlan is valid
                if self._vl_id_input not in range(1, 4097 + 1):
                    print(f"Invalid ID, range must between 1-4097")
                    continue
                else:
                    self._xml_delete_code(str(self._vl_id_input))
                    break
            except ValueError:
                print("Invalid Vlan")
                continue


    def delete_from_database(self, selection, db_ops) -> None:
        """Builds and deletes vlan configuration via xml from DB"""

        view_vlans_db(db_ops)

        if selection == "1":

            while True:
                try:
                    self._vl_id_input = int(input("VLAN: "))
                    query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                    if query == 0:
                        print("Vlan Doesn't Exist")
                        continue
                    # Verify vlan is valid
                    if self._vl_id_input not in range(1, 4097 + 1):
                        print(f"Invalid ID, range must between 1-4097")
                        continue
                    else:
                        break
                except ValueError:
                    print("Invalid Vlan")
                    continue

            for vlan_id in db_ops.session.query(ormdb.Vlans.vlan):
                if str(self._vl_id_input) == vlan_id.vlan:
                    self._xml_delete_code(vlan_id.vlan)
                    break

        elif selection == "2":

            while True:
                self._vl_name_input = input("VLAN name: ")
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_name.like(self._vl_name_input)).count()
                if query == 0:
                    print("Vlan Name Doesn't Exist")
                    continue
                else:
                    break

            for vlan_id, vl_name in db_ops.session.query(ormdb.Vlans.vlan, ormdb.Vlans.vlan_name):
                if self._vl_name_input == vl_name:
                    self._xml_delete_code(vlan_id)


    def update_from_router(self, db_ops) -> None:
        """Builds and Updates vlan configuration directly to router"""

        view_vlans_db(db_ops)

        while True:
            try:
                self._vl_id_input = int(input("VLAN: "))
                query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan.like(str(self._vl_id_input))).count()
                if query == 0:
                    print("Vlan Doesn't Exist")
                    continue
                # Verify vlan is valid
                if self._vl_id_input not in range(1, 4097 + 1):
                    print(f"Invalid ID, range must between 1-4097")
                    continue
                else:
                    break
            except ValueError:
                print("Invalid Vlan")
                continue

        while True:

            self._vl_name_input = input("VLAN name: ")
            query = db_ops.session.query(ormdb.Vlans).filter(ormdb.Vlans.vlan_name.like(self._vl_name_input)).count()
            if query > 0:
                print("Vlan Name Exist")
                continue
            else:
                self._xml_config_code(self._vl_id_input, self._vl_name_input)
                break


    def _xml_delete_code(self, vlan_id) -> None:
        """XML code for deleting vlan"""

        vlan_list = xml.SubElement(self.vlan_element, "vlan-list")
        vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")
        vlan_list.set("xc:operation", "remove")
        vl_id = xml.SubElement(vlan_list, "id")
        vl_id.text = str(vlan_id)
        vl_id.set("xc:operation", "remove")


    def _xml_config_code(self, vlan_id, vlan_name) -> None:
        """XML code for deleting vlan"""

        vlan_list = xml.SubElement(self.vlan_element, "vlan-list")
        vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")
        vl_id = xml.SubElement(vlan_list, "id")
        vl_id.text = str(vlan_id)
        vl_name = xml.SubElement(vlan_list, "name")
        vl_name.text = vlan_name

    # Getters and setters
    @property
    def vl_id_input(self):
        return self._vl_id_input
    
    @property
    def vl_name_input(self):
        return self._vl_name_input
    
    @property
    def vl_descr_input(self):
        return self._vl_descr_input

    @vl_id_input.setter
    def vl_id_input(self, value):
        self._vl_id_input = value
    
    @vl_name_input.setter
    def vl_name_input(self, value):
        self._vl_name_input = value
    
    @vl_descr_input.setter
    def vl_name_input(self, value):
        self._vl_descr_input = value

    @property
    def netconf_session(self):
        return  self._netconf_session

    @property
    def netmiko_session(self):
        return  self._netmiko_session

    @property
    def root(self):
        return self._root
    
    @property
    def username(self):
        return  self._username

    @property
    def password(self):
        return self._password

    @property
    def host(self):
        return self._host

    @username.setter
    def username(self, value):
        self._username = value

    @password.setter
    def password(self, value):
        self._password = value

    @host.setter
    def host(self, value):
        self._host = value

    @netconf_session.setter
    def netconf_session(self, value):
        self._netconf_session = value

    @root.setter
    def root(self, value):
        self._root = value

    @netmiko_session.setter
    def netmiko_session(self, value):
        self._netmiko_session = value
