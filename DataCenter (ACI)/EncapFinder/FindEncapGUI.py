module_array = [ ]
from os import system, name
try:
    from netmiko import  ConnectHandler
    from netmiko import ssh_exception
except ImportError:
    module_array.append("netmiko")
try:
    import  re
except ImportError:
    module_array.append("re")
try:
    import  time
except ImportError:
    module_array.append("time")
try:
    import  ipaddress
except ImportError:
    module_array.append("ipaddress")
try:
    import VLAN_Pools as vlanPool
except ImportError:
    module_array.append("Vlan_Pools")
try:
    import requests
except ImportError:
    module_array.append("request")
    pass
try:
    import lxml.etree as ET
except ImportError:
    module_array.append("lxml")
    pass
try:
    import warnings
except ImportError:
    module_array.append("warnings")
    pass
try:
    import collections
except ImportError:
    pass
try:
    import tkinter as tk
except ImportError:
    pass

###################################################################
#### File Used to read/write during runtime

get_file_1 = "C:\Python\ACI\Get_ACI.txt"
ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {'content-type': 'text/xml'}

class Application_login(tk.Frame):

    def __init__(self, master=None):

        # Inheirite all from tk class, or root passed to this class
        # # Create window (fame using master (root) class
        # Initialize device login funtion

        super().__init__(master)
        self.master = master
        self.frame = tk.Frame(master=self.master)
        self.frame.pack(expand=True)
        self.device_login()

    def device_login(self):

        # Create lables title, username, password, apic lables. Apply formatting
        # Create Entry boxes for user input
        # Create submit button
        # Bind enter key to funtion, enter_submit which call the apic login funtion

        self.title = tk.Label(self.frame, text="APIC Login", font=('Helvetica', '15', 'bold'), fg="green")
        self.title.pack(pady=15)

        self.label_1 = tk.Label(self.frame, text="APIC", font=('Helvetica', '10', 'bold')).pack()
        self.apic = tk.Entry(self.frame)
        self.apic.config(relief="sunken")
        self.apic.pack()

        self.label_2 = tk.Label(self.frame, text="Username", font=('Helvetica', '10', 'bold')).pack()
        self.username = tk.Entry(self.frame)
        self.username.pack()

        self.label_3 = tk.Label(self.frame, text="Password", font=('Helvetica', '10', 'bold')).pack()
        self.password = tk.Entry(self.frame)
        self.password.pack()

        self.submit_creds = tk.Button(self.frame, text="Submit", command=self.apic_login, font=('Helvetica', '10', 'bold')).pack(pady='10')
        self.master.bind('<Return>', self.enter_submit)

    def enter_submit(self, event):
        # Method calls apic login
        self.apic_login()

    def failed_login(self):
        # Method creates lable for login failure
        self.notify = tk.Label(self.frame, text="!Login Failed!", font=('Helvetica', '15', 'bold'), fg="red").pack(pady='10')

    def apic_login(self):
        # Method for authentication.
        # .get method retrieves entry box inputs. We will assign them to new varibles
        # Use variables for login URI, and login script
        # If login fails call the failed login method wich presents  a notifcation box
        # If auth successfull, call the subnet find class, pass variables
        # Close, or destroy(tkinter method) window

        apic = self.apic.get()
        username = self.username.get()
        password = self.password.get()

        uri = "https://%s/api/mo/aaaLogin.xml" % apic

        # POST username and password to the APIC

        raw_data = """<!-- AAA LOGIN -->
                 <aaaUser name="{}" pwd="{}"/> 
                 """.format(username, password)

        try:
            session = requests.Session()
            r = session.post(uri, data=raw_data, verify=False, headers=headers)  # Sends the request to the APIC
            response = r.text  # save the response to variable

            if re.findall("\\bFAILED local authentication\\b",response):
                self.failed_login()
            elif re.findall("\\bFailed to parse login request\\b",response):
                self.failed_login()
            else:

                new_window = find_encap(master=self.master,apic=apic,username=username,
                                         password=password, session=session)

                self.master.destroy()
        except (requests.exceptions.ConnectionError,requests.exceptions.InvalidURL):
            self.failed_login()

class find_encap():

    def __init__(self, master=None, apic=None, username=None, password=None, session=None):

        # Initialize new windown, set size, set heading, create window
        # Initialize, get_tenant method to retrieve fabric tenants
        # Initialize main method, which takes subnet/user input

        self.window = tk.Tk()
        self.window.geometry("300x200")
        self.window.title("ACI Encap Finder")
        self.master = self.window
        self.frame = tk.Frame(master=self.master)
        self.frame.pack(expand=True)

        self.apic = apic
        self.username = username
        self.password = password
        self.session = session
        vlanPool.aci_gets.vlan_pools(session, apic)
        vlanPool.aci_gets.phys_domains(session, apic)
        self.main()

    def main(self):
        # Main method
        # Present example, entry box, entry box get verticle padding from label
        # Create button for subnet submission
        # Binds enter button to enter_submit method
        # Both button and enter call the find subnet method

        self.title = tk.Label(self.frame, text="Vlan Encapsulation", font=('Helvetica', '10', 'bold')).pack()
        self.encap = tk.Entry(self.frame)
        self.encap.pack(pady=5)
        self.submit = tk.Button(self.frame, text="Submit", command=self.search_fabric, font=('Helvetica', '10', 'bold')).pack(pady='10')
        self.master.bind('<Return>', self.enter_submit)

    def enter_submit(self, event):
        # Method call find_subnet method
        self.search_fabric()

    def not_found(self):
        # Method creates a window when a subnet is not found.
        # Allows for enter and button click to close window

        self.notice = tk.Tk()
        self.notice.geometry("200x100")
        self.notice.title("ACI Encap Finder")
        self.master = self.notice
        self.window_3 = tk.Frame(master=self.master)
        self.window_3.pack(expand=True)
        self.status = tk.Label(self.window_3, text="Encap Not Found!", font=('Helvetica', '10', 'bold')).pack()
        self.close = tk.Button(self.window_3, text="Close", padx = 15, command=self.notice.destroy, font=('Helvetica', '10', 'bold')).pack(pady=10)
        self.master.bind('<Return>', self.destroy_not_found)

    def destroy_not_found(self, event):
        # Method closes not found window
        self.notice.destroy()

    def search_fabric(self):

        encap_id = self.encap.get()

        if encap_id == "":
            raise UnboundLocalError(self.not_found())
        else:
            try:
                vlan_pool = collections.defaultdict(list)
                phys_doms = collections.defaultdict(list)
                aaeps = collections.defaultdict(list)
                location = collections.defaultdict(list)
                path = collections.defaultdict(list)

                pools = vlanPool.aci_gets.find_duplicatee_vlan(self.session, self.apic, encap_id)
                vlan_pool[encap_id].append(pools[0])
                phys_doms[encap_id].append(pools[1])
                aaeps[encap_id].append(pools[2])
                location[encap_id].append(pools[3])
                path[encap_id].append(pools[4])

                unpacked_vlan_pools = [v for k, v in vlan_pool.items() for v in v for v in v]
                unpacked_phys_doms = [v for k, v in phys_doms.items() for v in v for v in v ]
                unpacked_aaep = [v for k, v in aaeps.items() for v in v for v in v ]
                unpacked_location = [v for k, v in location.items() for v in v for v in v ]
                unpacked_path = [v for k, v in path.items() for v in v for v in v]

                open_window = results(encap=encap_id, unpacked_vlan_pools=unpacked_vlan_pools, unpacked_phys_doms=unpacked_phys_doms, unpacked_aaep=unpacked_aaep,
                                      unpacked_location=unpacked_location, unpacked_path=unpacked_path)
            except TypeError:
                self.not_found()

class results():
    # This class output all data about the subnet

    def __init__(self, encap=None, unpacked_vlan_pools=None, unpacked_phys_doms=None,
                 unpacked_aaep=None, unpacked_location=None, unpacked_path=None):

        # Initialize new window and prodcues results. Since this is a class itself you can keep window open and
        # search for a new subnet

        self.window = tk.Tk()
        self.window.geometry("1500x500")
        self.window.title("ACI Encap Finder")
        self.master = self.window
        self.frame = tk.Frame(master=self.master)
        self.frame.grid()

        self.padding = tk.Label(self.frame, text="").grid(row=3, column=1, padx=25)

        self.title = tk.Label(self.frame, text=encap, font=('Helvetica', '15', 'bold')).grid(row=2,columnspan=12, column=8)
        self.title = tk.Label(self.frame, text="Encap: ", font=('Helvetica', '15', 'bold')).grid(row=2,columnspan=12, column=6)


        row = 4
        self.title = tk.Label(self.frame, text="Vlan Pools: ", font=('Helvetica', '10', 'bold')).grid(row=row,column=4,sticky="W")
        for vlan_pools in unpacked_vlan_pools:
            self.title = tk.Label(self.frame, text=vlan_pools).grid(row=row, column=5, sticky="W")
            row = row + 1

        row = 4
        self.title = tk.Label(self.frame, text="Phys Doms: ", font=('Helvetica', '10', 'bold')).grid(row=row,column=6,sticky="W")
        for phys_doms in unpacked_phys_doms:
            self.title = tk.Label(self.frame, text=phys_doms).grid(row=row, column=7, sticky="W")
            row = row + 1

        row = 4
        self.title = tk.Label(self.frame, text="AAEPs: ", font=('Helvetica', '10', 'bold')).grid(row=row, column=8,sticky="W")
        for aaeps in unpacked_aaep:
            self.title = tk.Label(self.frame, text=aaeps).grid(row=row, column=9, sticky="W")
            row = row + 1

        row = 4
        self.title = tk.Label(self.frame, text="Locations: ", font=('Helvetica', '10', 'bold')).grid(row=row, column=10,sticky="W")
        for locations in unpacked_location:
            self.title = tk.Label(self.frame, text=locations).grid(row=row, column=11, sticky="W")
            row = row + 1

        row = 4
        self.title = tk.Label(self.frame, text="Paths: ", font=('Helvetica', '10', 'bold')).grid(row=row,column=12,sticky="W")
        for path in unpacked_path:
            self.title = tk.Label(self.frame, text=path).grid(row=row, column=13, sticky="W")
            row = row + 1


        self.close = tk.Button(self.frame, text="Close", command=self.window.destroy, width=30).grid(row=15,columnspan=12,column=7, pady=30)
        self.master.bind('<Return>', self.destroy_results)

    def destroy_results(self, event):
        self.window.destroy()

def module_check():

    # Present user with missing modules

    if module_array:
        modules = tk.Tk()
        modules.geometry("250x250")
        modules.title("Module Notification")
        frame = tk.Frame(master=modules)

        warning = tk.Label(modules, text="!WARNING!", font=('Helvetica', '15', 'bold'), fg="red").pack(pady=10)
        row = tk.Label(modules, text="-Missing Modules-", font=('Helvetica', '10', 'bold'), fg="red").pack(pady=10)

        count = 1
        for module in module_array:
            missing_mod = tk.Label(modules, text=module, font=('Helvetica', '10', 'bold')).pack(pady=15)
            count = count + 1

        accept = tk.Button(modules, text="Accept", command=modules.destroy, font=('Helvetica', '10', 'bold')).pack(
            pady='15')
    else:
        pass

if __name__ == '__main__':

    # Check for empy modules required to run this program. A message box will appear if modules are missing
    module_check()

    # Initiate tkinter window
    # Set window size
    # create window heading
    # initialize app, pass root object
    # Loop the program

    root = tk.Tk()
    root.geometry("350x300")
    root.title("ACI Encap Finder")
    app = Application_login(master=root)
    app.mainloop()
