SecureCRT Imports
------------------

**This code allows you to import SecureCRT session from infoblox using extensible attributes. If you dont have SecureCRT you can modify to import from other sources as well**


Prerequisites:

    Python3 !!! SecureCRT only allows the use external libraries when using python3.
    Insure you env path is set to Python3 folder.
    If you have any other python folders in you directory, SecureCRT wont be able to find Python.

    To the make the imports run with with minimal user interaction, you will need to statically enter the following fields in getFromSource.py

    >>>
    USER = ""
    PASSWORD = ""
    API_VERSION = ""
    BASE_URL = ''
    ATTRB = ''
    ATTRB_REGEX = ""
    CSV_HEADERS = ['hostname', 'protocol', 'folder', 'emulation']

    Line #32 getFromSource.py align with CSV headers

    >>> writer.writerow([i["name"], 'SSH2', v["value"], 'XTerm'])

    For folder headers, SecureCRT will read "/" in the attribute and create directories, placing the host in the last directory

    >>>
    folder1/folder2/folder3/
    folder/
            folder2/
                    folder3/
                            host

    Remove the folder header if you dont care about folders.
    Remove arg 3 from line #32 which is the folder attribute

    >>> writer.writerow([i["name"], 'SSH2', v["value"], 'XTerm'])

    1. Once you've assign these attributes, go to SecureCRT --> Scripts --> Run...
    2. Select script.
    3. You will prompted for your username, this will be added to sessions.
    4. You will be prompted for jumpbox if connections need this. If not, leave blank.


    If you want to use any other sources, create a function in getFromSource.py and call it in __main__
    There many option you can add to your sessions, if desired. Scroll though imports.py to see. Id desired to add more
    you will need to add the headers and values

    >>>
    CSV_HEADERS = ['hostname', 'protocol', 'folder', 'emulation']
    writer.writerow([i["name"], 'SSH2', v["value"], 'XTerm'])