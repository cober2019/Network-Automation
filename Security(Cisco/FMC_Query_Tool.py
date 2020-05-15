try:
    import sqlite3
except ImportError:
    module_array.append("sqllite3")
    print("Module SQLITE3 not available.")
try:
    import readline
except ImportError:
    module_array.append("readline")
    print("readline not available")
from os import system, name


mydb = sqlite3.connect("FMC")
c = mydb.cursor()

def query(policy, where, choice):

    query = "%" + choice
    try:
        for row in c.execute('SELECT * FROM ' + policy + ' WHERE ' + where + ' LIKE ?', (query, )):
            print(" Name:            {}\n Source Int:      {}\n Dest Int:        {}\n Source Net:      {}\n Dest Net:        {}\n Source Port:     "
                "{}\n Dest Port:       {}\n Action:          {}\n\n".format(row[0],row[1],
                                                             row[2],
                                                             row[3].replace(",", "\n                  "),
                                                             row[4].replace(",", "\n                  "),
                                                             row[8].replace(",", "\n                  "),
                                                             row[9].replace(",", "\n                  "),
                                                             row[12]))
    except sqlite3.OperationalError:
        pass

def query_objects(where, object):

    query = "%" + object
    try:
        for row in c.execute('SELECT * FROM Object_Used WHERE ' + where + ' LIKE ?', (query, )):
            print(" ID:      {}\n Type:    {}\n Name:    {}\n Value:   {}\n\n".format(row[0],row[1],
                                                                                                     row[2],
                                                                                                     row[3].replace(",", "\n   ")))
    except sqlite3.OperationalError:
        pass

def db_tables():

    tables = [ ]

    try:
        for table in c.execute('SELECT name FROM sqlite_master WHERE type=? ORDER BY name;', ("table",)):
            if table[0] == "Object_Used":
                continue
            else:
                tables.append(table[0] + "\n")
                print(table[0])
    except (IndexError, NameError):
        pass

    return tables

def tab_complete(text, state):

    db_table = db_tables()

    tables = [table for table in db_table if table.startswith(text)]

    if state < len(tables):
        return tables[state]
    else:
        return None

def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')


if __name__ == '__main__':

    while True:

        print("FMC Query Tool\n")
        print("1. Rule Name")
        print("2. Source Network")
        print("3. Dest Network")
        print("4. Source Port")
        print("5. Dest Port")
        print("6. Action")
        print("7. Objects\n")

        selection = input(" Selection: ")
        print("\n")
        clear()
        print("Select Policy * Use TAB for autocomplete\n")
        db_tables()
        readline.parse_and_bind("tab: complete")
        readline.set_completer(tab_complete)
        print("\n")
        policy = input("Selection: ")
        print("\n")

        if selection == "1":
            find_name = input("Rule Name:")
            query(policy, "Name", find_name)
            print("\n")
        elif selection == "2":
            find_src_net = input("Source Network: ")
            query(policy,"srcNet", find_src_net)
            print("\n")
        elif selection == "3":
            find_dst_net = input("Dest Network: ")
            query(policy,"dstNet", find_dst_net)
            print("\n")
        elif selection == "4":
            find_src_port = input("Source Port: ")
            query(policy,"srcPort", find_src_port)
            print("\n")
        elif selection == "5":
            find_dst_port = input("Dest Port: ")
            query(policy,"dstPort", find_dst_port)
            print("\n")
        elif selection == "6":
            find_action = input("Action: ")
            query(policy, "action", find_action)
            print("\n")
        elif selection == "7":

            print("\n")
            print("1. Object Name")
            print("2. Object Type")
            print("3. Object Value\n")

            selection = input("Selection: ")
            print("\n")

            if selection == "1":
                find_obj_name = input("Object Name:")
                print("\n")
                query_objects("type", find_obj_name)
            elif selection == "2":
                find_obj_type = input("Object Type: ")
                print("\n")
                query_objects("name", find_obj_type)
            elif selection == "3":
                find_obj_value = input("Object Value: ")
                print("\n")
                query_objects("value", find_obj_value)
