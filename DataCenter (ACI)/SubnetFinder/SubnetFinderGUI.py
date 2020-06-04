module_array = [ ]
try:
    import re
except ImportError:
    module_array.append("request")
try:
    import requests
except ImportError:
    module_array.append("request")
try:
    import lxml.etree as ET
except ImportError:
    module_array.append("lxml")
try:
    import warnings
except ImportError:
    module_array.append("warnings")
try:
    import json
except ImportError:
    module_array.append("json")
try:
    from socket import  gaierror
except ImportError:
    module_array.append("time")
import tkinter as tk

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


                new_window = subnet_find(master=self.master,apic=apic,username=username,
                                         password=password, session=session)

                self.master.destroy()
        except (requests.exceptions.ConnectionError,requests.exceptions.InvalidURL):
            self.failed_login()

class subnet_find():

    def __init__(self, master=None, apic=None, username=None, password=None, session=None):

        # Initialize new windown, set size, set heading, create window
        # Initialize, get_tenant method to retrieve fabric tenants
        # Initialize main method, which takes subnet/user input

        self.window = tk.Tk()
        self.window.geometry("300x200")
        self.window.title("ACI Subnet Finder")
        self.master = self.window
        self.frame = tk.Frame(master=self.master)
        self.frame.pack(expand=True)

        self.apic = apic
        self.username = username
        self.password = password
        self.session = session
        self.status = None
        self.tenant_array = []

        self.get_tenants()
        self.main()

    def main(self):
        # Main method
        # Present example, entry box, entry box get verticle padding from label
        # Create button for subnet submission
        # Binds enter button to enter_submit method
        # Both button and enter call the find subnet method

        self.title = tk.Label(self.frame, text="Subnet (ex 1.1.1.1/24)", font=('Helvetica', '10', 'bold')).pack()
        self.subnet = tk.Entry(self.frame)
        self.subnet.pack(pady=5)
        self.submit_subnet = tk.Button(self.frame, text="Submit", command=self.find_subnet, font=('Helvetica', '10', 'bold')).pack(pady='10')
        self.master.bind('<Return>', self.enter_submit)

    def enter_submit(self, event):
        # Method call find_subnet method
        self.find_subnet()

    def not_found(self):
        # Method creates a window when a subnet is not found.
        # Allows for enter and button click to close window

        self.notice = tk.Tk()
        self.notice.geometry("200x100")
        self.notice.title("ACI Subnet Finder")
        self.master = self.notice
        self.window_3 = tk.Frame(master=self.master)
        self.window_3.pack(expand=True)
        self.status = tk.Label(self.window_3, text="Subnet Not Found!", font=('Helvetica', '10', 'bold')).pack()
        self.close = tk.Button(self.window_3, text="Close", padx = 15, command=self.notice.destroy, font=('Helvetica', '10', 'bold')).pack(pady=10)
        self.master.bind('<Return>', self.destroy_not_found)

    def destroy_not_found(self, event):
        # Method closes not found window
        self.notice.destroy()

    def get_tenants(self):

        # Find all Tenants that are configured in ACI

        uri = "https://%s/api/class/fvTenant.json" % self.apic

        r = self.session.get(uri, verify=False, headers=headers)
        response_dict = r.json()
        total_count = int(response_dict["totalCount"])

        try:
            index = 0
            for i in range(0, total_count):
                self.tenant_array.append(response_dict["imdata"][index]["fvTenant"]["attributes"]["name"])
                index = index + 1
        except IndexError:
            pass

    def find_subnet(self):

        subnet_id = self.subnet.get()
        if subnet_id == "":
            raise  UnboundLocalError(self.not_found())
        else:

            uri = "https://%s/api/class/fvBD.xml?query-target=subtree" % self.apic
            r = self.session.get(uri, verify=False, headers=headers)

            try:
                file = open(get_file, 'w')
                file.write(r.text)
                file.close()
            except:
                pass

            tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
            root = tree.getroot()

            try:
                for fvSubnet in root.iter("fvSubnet"):
                    location = fvSubnet.get("dn")
                    ip = fvSubnet.get("ip")
                    if subnet_id in ip:
                        gps = location
                        gps_ip = ip
                        scope = fvSubnet.get("scope")

            # Iterates through the xml document and finds the bridge domain atrributes. Checks to see if the variable gps,
            # line 180, contains the bridge domain string. Use regex with boarder to find the exact string. Grabse unicast
            # route as well to check if routing is enabled.

                for fvBD in root.iter("fvBD"):
                    bridge_domain = fvBD.get("name")
                    if re.findall('[?<=/BD-]' + bridge_domain + '(?=/)', gps):
                        gps_bd = bridge_domain
                        uni_route = fvBD.get("unicastRoute")
                        unkwn_uni = fvBD.get("unkMacUcastAct")

                # Iterates through the xml document to find vrf attributes. Checks to see which vrf matches the location
                # create on line 177. Uses regex to find and exact string match.

                for fvRsCtx in root.iter("fvRsCtx"):
                    vrf = fvRsCtx.get("tnFvCtxName")
                    location = fvRsCtx.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', location):
                        gps_vrf = vrf

                # Iterate through class fvRtBD which will give you a DN showing the tenant, app profile, and endpoint groups.
                # We will use regex to search the dn with out BD
                # We will store these to list since a BD can live in more that one location

                aps = []
                epgs = []
                for fvRtBd in root.iter("fvRtBd"):
                    dn = fvRtBd.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                        ap = re.findall(r'(?<=ap-).*(?=/ep)', dn)
                        aps.append(ap[0])
                        epg = re.findall(r'(?<=epg-).*(?=\])', dn)
                        epgs.append(epg[0])

                    else:
                        pass

                # Iterate through the fvRsBDToOut class to find the L3Out the BD is associated with
                # We will use regex to search the dn with out BD
                # Sometime a BD isnt advertised externall so we ad a condition to the logic. Now leout variable will always have something
                # avoid issues down the road

                for fvRsBDToOut in root.iter("fvRsBDToOut"):
                    dn = fvRsBDToOut.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                        if not fvRsBDToOut.get("tnL3extOutName"):
                            l3out = "N/A"
                        else:
                            l3out = fvRsBDToOut.get("tnL3extOutName")

                for tenant in self.tenant_array:
                    if tenant in gps:
                        gps_tenant = tenant
                    else:
                        continue

            except UnboundLocalError:
                self.not_found()

            else:

                # If subnet found, call the result class. A new window will open and another subnet can be search without
                # closing previous lookups

                open_window = results(subnet_id=subnet_id, tenant=gps_tenant, bd=gps_bd, epg=epg, vrf=gps_vrf,
                                         l3out=l3out,uni_route=uni_route, scope=scope, unkwn_uni=unkwn_uni,ap=ap)



class results():
        # This class output all data about the subnet

        def __init__(self, subnet_id=None, tenant=None, bd=None, epg=None, vrf=None,
                                 l3out=None,uni_route=None, scope=None, unkwn_uni=None,
                                 ap=None):
            # Initialize new window and prodcues results. Since this is a class itself you can keep window open and
            # search for a new subnet

            self.window = tk.Tk()
            self.window.geometry("300x300")
            self.window.title("ACI Subnet Finder")
            self.master = self.window
            self.frame = tk.Frame(master=self.master)
            self.frame.grid()

            self.padding =tk.Label(self.frame, text="").grid(row=3, column=1, padx=25)
            self.title = tk.Label(self.frame, text=subnet_id).grid(row=4, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Subnet: ", font=('Helvetica', '10', 'bold')).grid(row=4, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=tenant).grid(row=5, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Tenant: ", font=('Helvetica', '10', 'bold')).grid(row=5, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=bd).grid(row=6, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Bridge Domain: ", font=('Helvetica', '10', 'bold')).grid(row=6, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=epg).grid(row=7, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="EPG: ", font=('Helvetica', '10', 'bold')).grid(row=7, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=vrf).grid(row=8, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Vrf: ", font=('Helvetica', '10', 'bold')).grid(row=8, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=l3out).grid(row=9, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="L3Out: ", font=('Helvetica', '10', 'bold')).grid(row=9, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=uni_route).grid(row=10, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Unicast Route: ", font=('Helvetica', '10', 'bold')).grid(row=10, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=scope).grid(row=11, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Scope: ", font=('Helvetica', '10', 'bold')).grid(row=11, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=unkwn_uni).grid(row=12, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="Uknown Unicast: ", font=('Helvetica', '10', 'bold')).grid(row=12, column=2, sticky ="W")

            self.title = tk.Label(self.frame, text=ap).grid(row=13, column=3, sticky ="W")
            self.title = tk.Label(self.frame, text="App Profile", font=('Helvetica', '10', 'bold')).grid(row=13, column=2, sticky ="W")

            self.close = tk.Button(self.frame, text="Close", command=self.window.destroy, width=10).grid(row=14, columnspan=4, pady=15)
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
    root.title("ACI Subnet Finder")
    app = Application_login(master=root)
    app.mainloop()