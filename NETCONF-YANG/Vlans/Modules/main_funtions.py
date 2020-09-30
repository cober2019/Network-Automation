"""Helper functions to create and modify vlan configurations"""

from ncclient import manager
from ncclient.operations import RPCError
import lxml.etree as ET
import Modules.config_build as config_build
import xml.etree.cElementTree as xml
import logging
import Modules.connection as ConnectWith
from Database import ormdb

build_object = None
db_ops = None
logging.basicConfig(filename='Logging/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def database_write(op_type, op_cat) -> None:
    """Check operational and operartion category types, calls updates DB"""

    # Check if operation arugment is delete
    if op_type == "delete":
        if op_cat == "1":
            db_ops.db_delete_vlan(build_object._vl_id_input)
        elif op_cat == "2":
            db_ops.db_delete_name( build_object._vl_name_input)
        else:
            db_ops.db_delete_vlan(build_object._vl_id_input)
    # Check if operation arugment is update
    elif op_type == "update":
        if op_cat == "1":
            db_ops.db_vlan_name_update(build_object._vl_id_input, build_object._vl_name_input)
        elif op_cat == "2":
            db_ops.db_desc_vlan_update(build_object._vl_id_input, build_object._vl_descr_input)
    elif op_type == "from_db":
        pass
    else:
        db_ops.db_vlan_insert(build_object.vl_id_input, build_object.vl_name_input, "Added From Device")


def clear_object_attributes() -> None:
    """Clears object attributtes using setters for next config"""

    build_object._vl_id_input = None
    build_object._vl_name_input = None
    build_object._vl_descr_input = None


def set_object_credentials(username, password, host, netconf_session, netmiko_session) -> None:
    """Updates object properties using setters for next config"""

    build_object._username = username
    build_object._password = password
    build_object._host = host
    build_object._netconf_session = netconf_session
    build_object._netmiko_session =  netmiko_session

def prepare_config(op_type=None, op_cat=None) -> None:
    """Prepare config for sending directly from string"""

    xmlstr = xml.tostring(build_object.root, method='xml')
    converted_config = xmlstr.decode('utf-8')

    if op_type is None:
        ConnectWith.send_configuration(converted_config, build_object.netconf_session, build_object, db_ops)
    else:
        ConnectWith.send_configuration(converted_config, build_object.netconf_session, build_object, db_ops, op_type=op_type, op_cat=op_cat)


def create_vlan_router() -> None:
    """Create a new vlan from router, insert into DB"""

    build_object.create_vlans(db_ops)
    prepare_config()


def create_from_database() -> None:
    """Create vlan from database input, config is sent to router """

    build_object.create_from_database(db_ops)
    prepare_config(op_type="from_db")


def delete_from_router() -> None:
    """Delete vlan directly from router, update DB"""

    build_object.delete_from_router(db_ops)
    prepare_config(op_type="delete")


def delete_from_db() -> None:
    """Delte vlan directly from router, update DB"""

    config_build.view_vlans_db(db_ops)
    print("1. ID\n2. Name\n")
    selection = input("Selection: ")
    print("\n")

    build_object.delete_from_database(selection, db_ops)
    prepare_config(op_type="delete", op_cat=selection)


def update_from_router() -> None:
    """Update vlan information from exisiting config on router, update db"""

    build_object.update_from_router(db_ops)
    prepare_config(op_type="update", op_cat="1")


def update_from_database() -> None:
    """Update device from database"""

    selection = build_object.update_from_database(db_ops)

    if build_object.root is None:
        pass
    else:
        prepare_config(op_type="update", op_cat=selection)

def login():

    global db_ops, build_object

    # Initial device login
    print("\nDevice Login\n")
    device = input("Device: ")
    user = input("Username: ")
    pwd = input("Password: ")
    print("\n")

    # Create connection object, set object attributes, view and sync device vlans to db, clear rows for next device
    build_object = config_build.BuildConfig()
    db_ops = ormdb.DbOps()
    db_ops.session.query(ormdb.Vlans).delete()
    netconf_session = ConnectWith.create_netconf_connection(user, pwd, device)
    netmiko_session = ConnectWith.netmiko_login(user, pwd, device)
    set_object_credentials(user, pwd, device, netconf_session, netmiko_session)
    build_object.get_netmiko_vlans(db_ops)
    main()

def main() -> None:
    """Main menu"""

    build_object.reset()

    while True:

        print("\n1. Add new vlan via DB")
        print("2. Add new vlan directly to router")
        print("3. Update Vlan From Database")
        print("4. Update Vlan From Router")
        print("5. Delete Vlan From Router")
        print("6. Delete Vlan From DB")
        print("7. View DB Vlans")
        print("8. Credentials\n")

        selection = input("Selection: ")
        print("\n")

        if selection == "1":
            create_from_database()
        elif selection == "2":
            create_vlan_router()
        elif selection == "3":
            update_from_database()
        elif selection == "4":
            update_from_router()
        elif selection == "5":
            delete_from_router()
        elif selection == "6":
            delete_from_db()
        elif selection == "7":
            config_build.view_vlans_db(db_ops)
        elif selection == "8":
            login()
        else:
            print("Invalid Selection")