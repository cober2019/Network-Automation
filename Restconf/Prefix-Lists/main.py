import PrefixListOps
import traceback


def menu_options(ip:str, port:int, username:str, password:str) -> None:

    selection = 0
    
    try:
        while selection != '6':

            selection = input('\n------------------\n1. View Prefix-lists\n2. Find Prefix\n3. Check Overlapping, User Selected Prefix\n4. Check All List For Overlapping\n5. Find Prefix in RIB\n6. Back To Login\n\nSelection: ')

            if selection == '1':
                prefix_list = PrefixListOps.get_prefix_list(ip, port, username, password)
                PrefixListOps.view_prefix_list(prefix_list[0])
            elif selection == '2':
                prefix_list = PrefixListOps.get_prefix_list(ip, port, username, password)
                prefix = input('\nPrefix: ')
                PrefixListOps.find_prefix(prefix_list[0], prefix)
            elif selection == '3':
                prefix_list = PrefixListOps.get_prefix_list(ip, port, username, password)
                prefix = input('\nPrefix: ')
                PrefixListOps.check_proposed_overlapping(prefix_list[0], prefix)
            elif selection == '4':
                prefix_list = PrefixListOps.get_prefix_list(ip, port, username, password)
                PrefixListOps.check_overlapping(prefix_list[0])
            elif selection == '5':
                prefix = input('\nPrefix: ')
                PrefixListOps.find_prefix_in_rib(ip, port, username, password, prefix)
            elif selection == '6':
                main_menu()
            else:
                print('\nInvalid Selection\n')
    except KeyboardInterrupt:
        main_menu()

def main_menu():
    
    print('\nPrefix-List-Ops\n')
    
    ip = input('IP: ')
    username = input('Username: ')
    password = input('Password: ')
    port = input('Port: ')

    auth = PrefixListOps.get_prefix_list(ip, port, username, password)

    if not auth[1]:
        print('\nLogin Failed\n\n')
        main_menu()
    else:
        menu_options(ip, port, username, password, auth[0])

if __name__ == '__main__':

    try:
        main_menu()
    except BaseException:
        print(f'\n\n\nSomething Is Really Wrong. Please submit an issue with the following log:\n')
        print(traceback.print_exc())
        main_menu()
    





