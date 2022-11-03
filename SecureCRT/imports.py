# $language = "Python3"
# $interface = "1.0"


import datetime
import os
import platform
import re
import shutil
import sys
import time
import subprocess
import getFromSource




MsgBox = crt.Dialog.MessageBox
# The g_strDefaultProtocol variable will only be defined within the
# ValidateFieldDesignations function if the protocol field has a default value
# (e.g., protocol=SSH2), as read in from the first line of the data file.
global g_strDefaultProtocol
g_strDefaultProtocol = ""

# The g_strDefaultFolder variable will only be defined within the
# ValidateFieldDesignations function if the folder field has a default value
# (e.g., folder=Site34), as read in from the first line of the data file.
global g_strDefaultFolder
g_strDefaultFolder = ""

# The g_strDefaultUsername variable will only be defined within the
# ValidateFieldDesignations function if the protocol field has a default value
# (e.g., username=bobofet), as read in from the first line of the data file.
global g_strDefaultUsername
g_strDefaultUsername = ""

# If your data file uses spaces or a character other than comma as the
# delimiter, you would also need to edit the g_strDelimiter value a few lines
# below to indicate that fields are separated by spaces, rather than by commas.
# For example:
#       g_strDelimiter = " "
# Using a ";" might be a good alternative for a file that includes the comma
# character as part of any legitimate session name or folder name, etc.
global g_strDelimiter
g_strDelimiter = ","  # comma
# g_strDelimiter = " "    # space
# g_strDelimiter = ";"    # semi-colon
# g_strDelimiter = chr(9) # tab
# g_strDelimiter = "|||"  # a more unique example of a delimiter.


# The g_strSupportedFields indicates which of all the possible fields, are
# supported in this example script.  If a field designation is found in a data
# file that is not listed in this variable, it will not be imported into the
# session configuration.
global g_strSupportedFields
g_strSupportedFields = \
    "description,emulation,folder,hostname,port,protocol,session_name,username,logon_script,domain"

# If you wish to overwrite existing sessions, set the
# g_bOverwriteExistingSessions to True; for this example script, we're playing
# it safe and leaving any existing sessions in place :).
global g_bOverwriteExistingSessions
g_bOverwriteExistingSessions = False

strHome = os.path.expanduser("~")
global g_strMyDocs
g_strMyDocs = strHome + "/Documents"

g_strMyDesktop = strHome + "/Desktop"

global g_strHostsFile
g_strHostsFile = g_strMyDocs + "/MyDataFile.csv"

global g_strExampleHostsFile
g_strExampleHostsFile = \
    "\thostname,protocol,username,folder,emulation\n" + \
    "\t192.168.0.1,SSH2,root,Linux Machines,XTerm\n" + \
    "\t192.168.0.2,SSH2,root,Linux Machines,XTerm\n" + \
    "\t...\n" + \
    "\t10.0.100.1,SSH1,admin,CISCO Routers,VT100\n" + \
    "\t10.0.101.1,SSH1,admin,CISCO Routers,VT100\n" + \
    "\t...\n" + \
    "\tmyhost.domain.com,SSH2,administrator,Windows Servers,VShell\n" + \
    "\t...\n"

g_strExampleHostsFile = g_strExampleHostsFile.replace(",", g_strDelimiter)

global g_strConfigFolder, strFieldDesignations, g_vFieldsArray, vSessionInfo

global strSessionName, strHostName, strPort
global strUserName, strProtocol, strEmulation, strDomain
global strPathForSessions, g_strLine, nFieldIndex
global strSessionFileName, strFolder, nDescriptionLineCount, strDescription

global g_strLastError, g_strErrors, g_strSessionsCreated
global g_nSessionsCreated, g_nDataLines, g_nCurLineNumber
g_strLastError = ""
g_strErrors = ""
g_strSessionsCreated = ""
g_nSessionsCreated = 0
g_nDataLines = 0
g_nCurLineNumber = 0

global g_objReFolders, g_objReSession
# Folders as specified in the data file can have
# / chars since they can include sub-folder components
g_objReFolders = re.compile(r'([\|\:\*\?\"\<\>])')
# Session names, however, cannot have / chars
g_objReSession = re.compile(r'([\|\:\*\?\"\<\>/])')

global g_objReSpecialsFolders, g_objReSpecialsSession
g_objReSpecialsFolders = re.compile(r'/(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])/', re.I)
g_objReSpecialsSession = re.compile(r'^(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])$', re.I)

# Use current date/time info to avoid overwriting existing sessions by
# importing sessions into a new folder named with a unique timestamp.
g_strDateTimeTag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:19]

global g_bUseDefaultSessionOptions
g_bUseDefaultSessionOptions = False

global g_strBogusLinesNotImported
g_strBogusLinesNotImported = ""

global g_nMajorVersion, g_nMinorVersion, g_nMaintVersion
strVersion = crt.Version
strVersionPart = strVersion.split(" ")[0]
vVersionElements = strVersionPart.split(".")
g_nMajorVersion = int(vVersionElements[0])
g_nMinorVersion = int(vVersionElements[1])
g_nMaintVersion = int(vVersionElements[2])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def GetConfigPath():
    objConfig = crt.OpenSessionConfiguration("Default")
    # Try and get at where the configuration folder is located. To achieve
    # this goal, we'll use one of SecureCRT's cross-platform path
    # directives that means "THE path this instance of SecureCRT
    # is using to load/save its configuration": ${VDS_CONFIG_PATH}.

    # First, let's use a session setting that we know will do the
    # translation between the cross-platform moniker ${VDS_CONFIG_PATH}
    # and the actual value... say, "Upload Directory V2"
    strOptionName = "Upload Directory V2"

    # Stash the original value, so we can restore it later...
    strOrigValue = objConfig.GetOption(strOptionName)

    # Now set the value to our moniker...
    objConfig.SetOption(strOptionName, "${VDS_CONFIG_PATH}")
    # Make the change, so that the above templated name will get written
    # to the config...
    objConfig.Save()

    # Now, load a fresh copy of the config, and pull the option... so
    # that SecureCRT will convert from the template path value to the
    # actual path value:
    objConfig = crt.OpenSessionConfiguration("Default")
    strConfigPath = objConfig.GetOption(strOptionName)

    # Now, let's restore the setting to its original value
    objConfig.SetOption(strOptionName, strOrigValue)
    objConfig.Save()

    # Now return the config path
    return strConfigPath


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ValidateFieldDesignations(strFields):
    global g_strDelimiter, g_strExampleHostsFile, g_strDefaultProtocol
    global g_vFieldsArray, g_strDefaultFolder, g_strDefaultUsername
    if strFields.find(g_strDelimiter) == -1:
        if len(g_strDelimiter) > 1:
            strDelimiterDisplay = g_strDelimiter
        else:
            if ord(g_strDelimiter) < 33 or ord(g_strDelimiter) > 126:
                strDelimiterDisplay = "ASCII[{0}]".format(ord(g_strDelimiter))
            else:
                strDelimiterDisplay = g_strDelimiter
        strDelim = crt.Dialog.Prompt(
            "Delimiter character [" + strDelimiterDisplay + "] was not found " +
            "in the header line of your data file.\r\n\r\n" +
            "What is the delimiter (field separator) that your file " +
            "is using?\r\n\r\n\t Enter \"NONE\" if your data file only has a single field.")

        if strDelim == "":
            MsgBox("Script cannot continue w/o a field delimiter.")
            return

        if strDelim != "NONE":
            g_strDelimiter = strDelim

    g_vFieldsArray = strFields.split(g_strDelimiter)
    if not "hostname" in [x.lower() for x in g_vFieldsArray]:
        strErrorMsg = "Invalid header line in data file. " + \
                      "'hostname' field is required."
        if len(g_strDelimiter) > 1:
            strDelimiterDisplay = g_strDelimiter
        else:
            if ord(g_strDelimiter) < 33 or ord(g_strDelimiter) > 126:
                strDelimiterDisplay = "ASCII[{0}]".format(ord(g_strDelimiter))
            else:
                strDelimiterDisplay = g_strDelimiter

        MsgBox(strErrorMsg + "\n" +
               "The first line of the data file is a header line " +
               "that must include\n" +
               "a '" + strDelimiterDisplay +
               "' separated list of field keywords.\n" +
               "\n" +
               "'hostname' is a required keyword." +
               "\n\n" +
               "The remainder of the lines in the file should follow the " +
               "\n" +
               "pattern established by the header line " +
               "(first line in the file)." + "\n" + "For example:\n" +
               g_strExampleHostsFile,
               "Import Data To SecureCRT Sessions")
        return

    if not "protocol" in [x.lower() for x in g_vFieldsArray]:
        if strFields.lower().find("protocol=") == -1:
            # Load the default configuration and use that as the default
            # protocol.
            objConfig = crt.OpenSessionConfiguration("Default")
            g_strDefaultProtocol = objConfig.GetOption("Protocol Name")

    for strField in g_vFieldsArray:
        # MsgBox("{0}\nHas 'protocol': {1}\nHas '=': {2}".format(strField, strField.find("protocol"), strField.find("=")))
        if strField.lower().find("protocol") > -1 and \
                strField.lower().find("=") > -1:
            g_strDefaultProtocol = strField.split("=")[1].upper()
            # MsgBox(("Found a default protocol spec: {0}".format(g_strDefaultProtocol)))
            # Fix the protocol field since we know the default protocol
            # value
            strFields = strFields.replace(strField, "protocol")
        if strField.lower().find("folder") > -1 and \
                strField.lower().find("=") > -1:
            g_strDefaultFolder = strField.split("=")[1]
            strFields = strFields.replace(strField, "folder")

        if strField.lower().find("username") > -1 and \
                strField.lower().find("=") > -1:
            g_strDefaultUsername = strField.split("=")[1]
            strFields = strFields.replace(strField, "username")

    g_vFieldsArray = strFields.split(g_strDelimiter)
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def SessionExists(strSessionPath):
    # Returns True if a session specified as value for strSessionPath already
    # exists within the SecureCRT configuration.
    # Returns False otherwise.
    try:
        objTosserConfig = crt.OpenSessionConfiguration(strSessionPath)
        return True
    except Exception as objInst:
        return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def OpenPathInDefaultApp(strFile):
    strPlatform = sys.platform
    crt.Session.SetStatusText("Platform: {0}".format(strPlatform))
    crt.Sleep(200)
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', strFile))
        elif strPlatform == "win32":
            os.startfile(strFile)
        elif sys.platform.startswith('linux'):
            subprocess.call(('xdg-open', strFile))
        else:
            MsgBox("Unknown operating system:  " + os.name)
    except Exception as objErr:
        MsgBox(
            "Failed to open " + strFile + " with the default app.\n\n" +
            str(objErr).replace('\\\\', '\\').replace('u\'', '\''))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ValidateSessionFolderComponent(strComponent, strType):
    # strType can be either:
    #    folder
    #    session
    strOrigComponent = strComponent
    strType = strType.lower()

    global g_objReSession, g_objReFolders, g_strErrors, g_strLine
    global g_strBogusLinesNotImported

    # Check strComponent name for any invalid characters
    if strType == "folder":
        regexp = g_objReFolders
    else:
        regexp = g_objReSession

    objMatch = regexp.search(strComponent)
    if objMatch:
        strOffendingComponent = objMatch.group(1)
        if g_strErrors != "":
            g_strErrors = "\r\n{0}".format(g_strErrors)

        g_strErrors = (
                "Error: Invalid character '{0}' ".format(strOffendingComponent) +
                "in {0} name \"{1}\" specified on line #{2:04d}".format(
                    strType,
                    strOrigComponent,
                    g_nCurLineNumber) +
                ": {0}{1}".format(g_strLine, g_strErrors))

        g_strBogusLinesNotImported = "{0}\r\n{1}".format(
            g_strBogusLinesNotImported,
            g_strLine)
        return False

    # Now check for reserved names if we're on Windows
    if hasattr(sys, 'getwindowsversion'):
        global g_objReSpecialsFolders, g_objReSpecialsSession
        if strType == "folder":
            regexp = g_objReSpecialsFolders
            if strComponent[:1] != "/":
                strComponent = "/{0}".format(strComponent)
            if strComponent[1:] != "/":
                strComponent = "{0}/".format(strComponent)
        else:
            regexp = g_objReSpecialsSession

        objMatch = regexp.search(strComponent)
        if objMatch:
            strOffendingComponent = objMatch.group(1)
            if g_strErrors != "":
                g_strErrors = "\r\n{0}".format(g_strErrors)

            g_strErrors = (
                    "Error: Invalid {0} name ".format(strType) +
                    "\"{0}\" specified on line #{1:04d}".format(
                        strOrigComponent,
                        g_nCurLineNumber) +
                    ": {0} ---> '{1}' is a reserved name on Windows OS.{2}".format(
                        g_strLine,
                        strOffendingComponent,
                        g_strErrors)
            )
            g_strBogusLinesNotImported = "{0}\r\n{1}".format(
                g_strBogusLinesNotImported,
                g_strLine
            )

            return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ValidateProtocolComponent(strProtocol):
    global g_nMaintVersion, g_nCurLineNumber, g_strLine, g_strErrors
    global g_strBogusLinesNotImported

    bReturnValue = True
    strErrorText = ""
    if "rdp" in strProtocol.lower():
        if int(g_nMajorVersion) < 9:
            strErrorText = "Error: RDP protocol support requires SecureCRT version 9.0 or newer."
            bReturnValue = False
        elif not sys.platform == "win32":
            strErrorText = "Error: RDP protocol support is only available in SecureCRT for Windows."
            bReturnValue = False

        if bReturnValue == False:
            if g_strErrors != "":
                g_strErrors = "\r\n{0}".format(g_strErrors)

            g_strErrors = (
                    strErrorText +
                    "\r\n\tSession data on line line #{} will not be imported.".format(int(g_nCurLineNumber)) +
                    ": {}{}".format(g_strLine, g_strErrors))

            g_strBogusLinesNotImported = "{}\r\n{}".format(
                g_strBogusLinesNotImported,
                g_strLine)

    return bReturnValue


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def Import():
    global g_nMajorVersion, g_nMinorVersion, g_nMaintVersion
    global g_strHostsFile, strFieldDesignations, g_strErrors, g_strDelimiter
    global g_strDefaultProtocol, g_nDataLines, g_strSessionsCreated, g_nSessionsCreated
    global g_strDefaultFolder, g_strDefaultUsername, g_strLine, g_nCurLineNumber
    global g_strBogusLinesNotImported, g_bUseDefaultSessionOptions, strHostName
    strFolderOrig = g_strDefaultFolder

    g_strHostsFile = f'{os.path.dirname(os.path.realpath(__file__))}/devices.csv'

    nStartTime = time.time()
    bFoundHeader = False
    g_nCurLineNumber = 0
    vSessionInfo = []
    # Open our data file for reading
    with open(g_strHostsFile, "r") as objDataFile:

        jumphost = crt.Dialog.Prompt("Enter a jumphost: ")
        username = crt.Dialog.Prompt("Enter a username for your sessions. Leave blank to skip: ")

        # Iterate over each of the lines in the file, processing them one by one.
        for strLine in objDataFile:
            g_strLine = strLine.strip("\r\n")
            g_nCurLineNumber += 1
            # if g_nCurLineNumber == 1 or (g_nCurLineNumber % 10) == 0:
            crt.Session.SetStatusText(
                "Processing line #{0} from import file: {1}".format(
                    g_nCurLineNumber, str(g_strLine)))
            bSaveSession = False
            strSessionPath = ""
            strPort = ""
            strProtocol = ""
            strHostName = ""
            strUserName = ""
            strEmulation = ""
            strFolder = ""
            strFolderOrig = ""
            strDescription = ""
            strLogonScript = ""
            strDomain = ""

            if not bFoundHeader:
                strFieldDesignations = g_strLine
                # Validate the data file
                if not ValidateFieldDesignations(strFieldDesignations):
                    return
                else:
                    # Get a timer reading so that we can calculate how long it takes to import.
                    nStartTime = time.time()
                    bFoundHeader = True
            else:
                vSessionInfo = g_strLine.split(g_strDelimiter)
                if len(vSessionInfo) < len(g_vFieldsArray):
                    if g_strLine.strip() == "":
                        g_strLine = "[Empty Line]"
                    g_strErrors = ("\n" +
                                   "Insufficient data on line #{0:04d}: ".format(g_nCurLineNumber) +
                                   "{1}{2}".format(g_nCurLineNumber, g_strLine, g_strErrors))
                elif len(vSessionInfo) > len(g_vFieldsArray):
                    g_strErrors = g_strErrors + (
                            "\n" +
                            "==> Number of data fields on line #" +
                            "{0:04d} ".format(g_nCurLineNumber) +
                            "({0:d}) ".format(len(vSessionInfo)) +
                            "does not match the number of fields in the " +
                            "header ({0:d}).\r\n".format(
                                len(g_vFieldsArray)) +
                            "    This line will not be imported " +
                            "(Does the session name have a character " +
                            "that matches the delimiter you're using?):" +
                            "\r\n" +
                            "        " + g_strLine)
                    g_strBogusLinesNotImported = (g_strBogusLinesNotImported +
                                                  "\r\n" + g_strLine)
                    bSaveSession = False
                else:
                    # Variable used to determine if a session file should actually be
                    # created, or if there was an unrecoverable error (and the session
                    # should be skipped).
                    bSaveSession = True

                    # Now we will match the items from the new file array to the correct
                    # variable for the session's ini file
                    for nFieldIndex in range(0, len(vSessionInfo)):
                        # MsgBox("nFieldIndex: {0}\nlen(vSessionInfo):{1}\n{2}:{3}".format(nFieldIndex, len(vSessionInfo), g_vFieldsArray[nFieldIndex], vSessionInfo[nFieldIndex]))
                        strFieldLabel = g_vFieldsArray[nFieldIndex].strip().lower()
                        if "session_name" in strFieldLabel:
                            strSessionName = vSessionInfo[nFieldIndex].strip()

                        elif "logon_script" in strFieldLabel:
                            strLogonScript = vSessionInfo[nFieldIndex].strip()

                        elif "port" in strFieldLabel:
                            strPort = vSessionInfo[nFieldIndex].strip()
                            if not strPort == "":
                                if not strPort.isdigit():
                                    bSaveSession = False
                                    g_strErrors = (
                                    "\nError: Invalid port \"{0}\" specified on line #{1:04d}: {2}{3}".format(
                                        strPort, g_nCurLineNumber, g_strLine, g_strErrors))

                        elif "protocol" in strFieldLabel:
                            strProtocol = vSessionInfo[nFieldIndex].lower().strip()

                            if strProtocol == "ssh2":
                                strProtocol = "SSH2"
                            elif strProtocol == "ssh1":
                                strProtocol = "SSH1"
                            elif strProtocol == "telnet":
                                strProtocol = "Telnet"
                            elif strProtocol == "serial" or strProtocol == "tapi":
                                bSaveSession = False
                                g_strErrors = ("\n" +
                                               "Error: Unsupported protocol \"" + vSessionInfo[nFieldIndex].strip() +
                                               "\" specified on line #" +
                                               "{0:04d}: {1}".format(g_nCurLineNumber, g_strLine) +
                                               g_strErrors)
                            elif strProtocol == "rlogin":
                                strProtocol = "RLogin"
                            elif "rdp" in strProtocol.lower():
                                strProtocol = "RDP"
                            else:
                                if g_strDefaultProtocol != "":
                                    strProtocol = g_strDefaultProtocol
                                else:
                                    bSaveSession = False
                                    g_strErrors = ("\n" +
                                                   "Error: Invalid protocol \"" + strProtocol +
                                                   "\" specified on line #" +
                                                   "{0:04d}: {1}".format(g_nCurLineNumber, g_strLine) +
                                                   g_strErrors)

                        elif "hostname" in strFieldLabel:
                            strHostName = vSessionInfo[nFieldIndex].strip()
                            if strHostName == "":
                                bSaveSession = False
                                g_strErrors = ("\n" +
                                               "Error: Hostname field on line #{0:04d} is empty: {1}".format(
                                                   g_nCurLineNumber, g_strLine) +
                                               g_strErrors)

                        elif "username" in strFieldLabel:
                            strUserName = vSessionInfo[nFieldIndex].strip()

                        elif "emulation" in strFieldLabel:
                            strEmulation = vSessionInfo[nFieldIndex].lower().strip()
                            if strEmulation == "xterm":
                                strEmulation = "Xterm"
                            elif strEmulation == "vt100":
                                strEmulation = "VT100"
                            elif strEmulation == "vt102":
                                strEmulation = "VT102"
                            elif strEmulation == "vt220":
                                strEmulation = "VT220"
                            elif strEmulation == "vt320":
                                if g_nMajorVersion < 8:
                                    bSaveSession = False
                                    g_strErrors = ("\n" +
                                                   "Error: VT320 emulation is not available in versions prior to 8.0. " +
                                                   "Session specified on line #{0:04d} is invalid: {1}{2}".format(
                                                       g_nCurLineNumber, g_strLine, g_strErrors))
                                else:
                                    strEmulation = "VT320"

                            elif strEmulation == "ansi":
                                strEmulation = "ANSI"
                            elif strEmulation == "linux":
                                strEmulation = "Linux"
                            elif strEmulation == "scoansi":
                                strEmulation = "SCOANSI"
                            elif strEmulation == "vshell":
                                strEmulation = "VShell"
                            elif strEmulation == "wyse50":
                                strEmulation = "WYSE50"
                            elif strEmulation == "wyse60":
                                strEmulation = "WYSE60"
                            else:
                                bSaveSession = False
                                g_strErrors = ("\n" +
                                               "Error: Invalid emulation \"{0}\" specified on line #{1:04d}: {2}{3}".format(
                                                   strEmulation, g_nCurLineNumber, g_strLine, g_strErrors))

                        elif "folder" in strFieldLabel:
                            strFolderOrig = vSessionInfo[nFieldIndex][:-1].strip()
                            strFolder = strFolderOrig.lower()
                            if strFolder == "":
                                strFolder = g_strDefaultFolder
                                strFolderOrig = g_strDefaultFolder

                        elif "description" in strFieldLabel:
                            strCurDescription = vSessionInfo[nFieldIndex].strip()
                            if strDescription == "":
                                strDescription = strCurDescription
                            else:
                                strDescription = "{0}\\r{1}".format(strDescription, strCurDescription)
                                strDescription = strDescription.replace("\\r", "\r")

                        elif "domain" in strFieldLabel:
                            strDomain = vSessionInfo[nFieldIndex].strip()

                        else:
                            # If there is an entry that the script is not set to use
                            # in strFieldDesignations, stop the script and display a
                            # message
                            strMsg1 = (
                                    "Error: Unknown field designation: {0}\n".format(
                                        g_vFieldsArray[nFieldIndex]) +
                                    "\tSupported fields are as follows:\n\n\t" +
                                    "{0}\n\n".format(g_strSupportedFields) +
                                    "For a description of the supported fields, " +
                                    "see the comments in the sample script file." +
                                    "")

                            if g_strErrors.strip() != "":
                                strMsg1 = (strMsg1 + "\n\n" +
                                           "Other errors found so far include: " +
                                           g_strErrors)
                            MsgBox(strMsg1, "Import Data To SecureCRT Sessions: Data File Error")
                            return

                    # Use hostname if a session_name field wasn't present
                    if strSessionName == "":
                        strSessionName = strHostName

                    if not ValidateSessionFolderComponent(strSessionName, "session"):
                        bSaveSession = False

                    if strFolderOrig == "":
                        strFolderOrig = g_strDefaultFolder

                    if not ValidateSessionFolderComponent(strFolderOrig, "folder"):
                        bSaveSession = False

                    if not ValidateProtocolComponent(strProtocol):
                        bSaveSession = False

                    if bSaveSession:
                        # Canonicalize the path to the session, as needed
                        strSessionPath = strSessionName

                        if strFolderOrig.strip() != "":
                            if strFolderOrig[1:] != "/":
                                strSessionPath = "{0}/{1}".format(strFolderOrig, strSessionName)
                            else:
                                strSessionPath = "{0}/{1}".format(strFolderOrig, strSessionName)

                        if strUserName.strip() == "":
                            strUserName = g_strDefaultUsername

                        # Strip any leading '/' characters from the session path
                        strSessionPath = strSessionPath.lstrip('/')
                        if SessionExists(strSessionPath):
                            if not g_bOverwriteExistingSessions:
                                continue
                                # Append a unique tag to the session name, if it already exists
                                # strSessionPath = "{0}(import_({1})".format(strSessionPath, datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:19])

                        # MsgBox(
                        #    "Line #{0}: {1}\nbSaveSession: {2}\nSessionPath: {3}\n\nPort: {4}\nProtocol: {5}\nHostname: {6}\nUsername: {7}\nEmulation: {8}\nFolder: {9}\nDescription: {10}\n\n{11}".format(
                        #        g_nCurLineNumber, g_strLine, bSaveSession, strSessionPath, strPort, strProtocol, strHostName, strUserName, strEmulation, strFolder, strDescription, g_strErrors))

                        # Now: Create the session.
                        # ===================================================================
                        # Copy the default session settings into new session name and set the
                        # protocol.  Setting protocol protocol is essential since some variables
                        # within a config are only available with certain protocols.  For example,
                        # a telnet configuration will not be allowed to set any port forwarding
                        # settings since port forwarding settings are specific to SSH.
                        objConfig = crt.OpenSessionConfiguration("Default")

                        objConfig.SetOption("Protocol Name", strProtocol)

                        # We opened a default session & changed the protocol, now we save the
                        # config to the new session path:
                        objConfig.Save(strSessionPath)

                        # Now, let's open the new session configuration we've saved, and set
                        # up the various parameters that were specified in the file.
                        objConfig = crt.OpenSessionConfiguration(strSessionPath)
                        if objConfig.GetOption("Protocol Name") != strProtocol:
                            MsgBox("Error: Protocol not set. Expected \"{0}\", but got \"{1}\"".format(strProtocol,
                                                                                                       objConfig.GetOption(
                                                                                                           "Protocol Name")))
                            return

                        if strDescription != "":
                            vDescription = strDescription.split("\r")
                            objConfig.SetOption("Description", vDescription)

                        if strLogonScript != "":
                            if not "rdp" in strProtocol.lower():
                                objConfig.SetOption("Script Filename V2", strLogonScript)
                                objConfig.SetOption("Use Script File", True)
                            else:
                                MsgBox("Error: Logon Script is not supported for RDP sessions.")
                                return

                        if strEmulation != "":
                            if not "rdp" in strProtocol.lower():
                                objConfig.SetOption("Emulation", strEmulation)
                            else:
                                MsgBox("Error: Emulation is not supported for RDP sessions.")
                                return

                        if strProtocol.lower() != "serial":
                            if strHostName != "":
                                objConfig.SetOption("Hostname", strHostName)

                            if strUserName != "":
                                # Handle RDP sessions uniquely since the domain setting is
                                # tacked on to the username for such, if specified.
                                if ("rdp" in strProtocol.lower()) and (strDomain != ""):
                                    objConfig.SetOption("Username", "{}\{}".format(strDomain, strUserName))
                                else:
                                    objConfig.SetOption("Username", strUserName)

                            if username != "":
                                # Handle RDP sessions uniquely since the domain setting is
                                # tacked on to the username for such, if specified.
                                objConfig.SetOption("Username", username)

                        if strProtocol.upper() == "SSH2":
                            if strPort == "":
                                strPort = 22
                            objConfig.SetOption("[SSH2] Port", int(strPort))
                        elif strProtocol.upper() == "SSH1":
                            if strPort == "":
                                strPort = "22"
                            objConfig.SetOption("[SSH1] Port", int(strPort))
                        elif strProtocol.upper() == "TELNET":
                            if strPort == "":
                                strPort = "23"
                            objConfig.SetOption("Port", int(strPort))
                        elif "rdp" in strProtocol.lower():
                            if strPort == "":
                                strPort = "3389"
                            objConfig.SetOption("Port", int(strPort))

                        try:

                            # Only enter this next block if the individual decided to
                            # use this script's settings, not "Default" session's values.
                            if (not g_bUseDefaultSessionOptions) and (not "rdp" in strProtocol.lower()):
                                # If you don't want ANSI Color enabled for all imported sessions (regardless
                                # of value in Default session, comment out the following line)
                                # ---------------------------------------------------------------------------
                                # objConfig.SetOption("ANSI Color", True)
                                # objConfig.SetOption("Color Scheme", "Solarized Darcula") # Requires 8.3 or newer
                                # objConfig.SetOption("Color Scheme Overrides Ansi Color", True)

                                # Additional "SetOption" calls desired here... Comment out those you don't
                                # want, un-comment those you do want, and add more lines for other options
                                # you desire to be set by default for all sessions created from the import
                                # operation. Note: ${VDS_USER_DATA_PATH} = a cross-platform representation
                                #                  of the current user's "Documents" folder.
                                # ---------------------------------------------------------------------------
                                # objConfig.SetOption("Auto Reconnect", True)

                                # If you desire templated log file naming to be enabled
                                # for all imported sessions, uncommment the following 3
                                # lines of code:
                                # objDefaultConfig = crt.OpenSessionConfiguration("Default")
                                # if objDefaultConfig.GetOption("Log Filename V2") == "":
                                #     objConfig.SetOption("Log Filename V2", "${VDS_USER_DATA_PATH}\_ScrtLog(%S)_%Y%M%D_%h%m%s.%t.txt")

                                # objConfig.SetOption("Start Log Upon Connect", False)
                                # objConfig.SetOption("Rows", 60)
                                # objConfig.SetOption("Cols", 140)
                                # objConfig.SetOption("Use Word Delimiter Chars", True)
                                # if str(objConfig.GetOption("Word Delimiter Chars")) == "":
                                #     objConfig.SetOption("Word Delimiter Chars", " <>()+=$%!#*")

                                # if int(objConfig.GetOption("Scrollback")) == 500:
                                #     objConfig.SetOption("Scrollback", 12345)

                                # objConfig.SetOption("Key Exchange Algorithms", "diffie-hellman-group-exchange-sha256,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1")
                                # objConfig.SetOption("Idle NO-OP Check", True)
                                # objConfig.SetOption("Idle NO-OP Timeout", 60)

                                # objConfig.SetOption("Keyword Set", "MyCiscoKeywords")
                                # objConfig.SetOption("Highlight Color", True)
                                # objConfig.SetOption("Highlight Reverse Video", True)
                                # objConfig.SetOption("Ignore Window Title Change Requests", True)
                                # objConfig.SetOption("SSH2 Authentications V2", "publickey,keyboard-interactive,password")
                                # objConfig.SetOption("Identity Filename V2", "${VDS_USER_DATA_PATH}\Identity")
                                objConfig.SetOption("Firewall Name", "Session:" + jumphost)
                                # objConfig.SetOption("Firewall Name", "GlobalOptionDefinedFirewallName")
                                objConfig.SetOption("Auth Prompts in Window", True)
                        except Exception as objInst:
                            MsgBox("failure detected:\n\t{0}".format(str(objInst)))

                        objConfig.Save()

                        if g_strSessionsCreated != "":
                            g_strSessionsCreated = g_strSessionsCreated + "\n"

                        g_strSessionsCreated = g_strSessionsCreated + "    " + strSessionPath
                        g_nSessionsCreated += 1

            # Reset all variables in preparation for reading in the next line of
            # the hosts info file.
            strEmulation = ""
            strPort = ""
            strHostName = ""
            strFolder = ""
            strFolderOrig = ""
            strUserName = ""
            strSessionName = ""
            strDescription = ""
            strProtocol = ""
            strDomain = ""
            nDescriptionLineCount = 0
            g_nDataLines += 1

    nTimeElapsed = time.time() - nStartTime
    strResults = "Import operation completed in %2.3f seconds." % (nTimeElapsed)

    if g_nSessionsCreated > 0:
        strResults = (strResults + "\r\n" +
                      "-" * 70 + "\r\n" +
                      "Number of Sessions created: %d\r\n" % (g_nSessionsCreated))
        strResults = strResults + "\r\n" + g_strSessionsCreated
    else:
        strResults = (strResults + "\r\n" +
                      "-" * 70 + "\r\n" +
                      "No sessions were created from %d lines of data." % (g_nDataLines))

    crt.Session.SetStatusText("Import operation completed in {0:2.3f} seconds".format(nTimeElapsed))

    # Log activity information to a file for debugging purposes...
    strFilename = "{0}/__SecureCRT-Session-ImportLog-{1}.txt".format(g_strMyDocs, g_strDateTimeTag)
    if g_strErrors == "":
        strResults = (
            "No errors/warnings encountered from the import operation.\r\n\r\n{0}".format(strResults))
    else:
        strResults = "Errors/warnings from this operation include: \r\n{0}\r\n{1}\r\n{2}\r\n\r\n".format(
            g_strErrors, "-" * 70, strResults)

    if g_strBogusLinesNotImported != "":
        strResults = (
                "The following lines from the data file were *not* imported for " +
                "various reasons detailed below:\r\n" +
                "=" * 70 + "\r\n" +
                strFieldDesignations +
                g_strBogusLinesNotImported + "\r\n" +
                "-" * 70 + "\r\n" +
                "Fix the above lines to resolve the issues and save " +
                "the fixed lines to a new file. You can then run this " +
                "script again to import these skipped sessions.\r\n\r\n" +
                strResults)

    cFilenames = [
        "{0}/__SecureCRT-Session-ImportLog-{1}.txt".format(g_strMyDocs, g_strDateTimeTag).replace("\\", "/"),
        "{0}/__SecureCRT-Session-ImportLog-{1}.txt".format(g_strMyDesktop, g_strDateTimeTag).replace("\\", "/"),
        "{0}/__SecureCRT-Session-ImportLog-{1}.txt".format(GetConfigPath(), g_strDateTimeTag).replace("\\", "/")
    ]

    bSuccess = False

    for strFilename in cFilenames:
        try:
            objFile = open(strFilename, "w")
            bSuccess = True
        except:
            crt.Session.SetStatusText("Unable to open results file.")
            strResults = (strResults + "\n" +
                          "Failed to write summary results to: {0}".format(strFilename))
        if not os.path.isfile(strFilename):
            bSuccess = False
        else:
            break

    if not bSuccess:
        if ":\\" in g_strMyDocs:
            strResults = strResults.replace("\n", "\r\n")
        crt.Clipboard.Text = strResults
        MsgBox(
            "Attempted to write summary results to the file locations below, " +
            "but access was denied.\r\n\t{0}".format("\r\n\t".join(cFilenames)) +
            "\r\n\r\nResults are in the clipboard. " +
            "Paste them into your favorite app now to see what occurred.")
        return

    objFile.write(strResults.replace("\r\n", "\n"))
    objFile.close()

    # Display the log file as an indication that the information has been
    # imported.
    OpenPathInDefaultApp(strFilename)
    crt.Session.SetStatusText("")


if '__name__' in '__main__':

    getFromSource.request_record_by_extattrb()
    Import()