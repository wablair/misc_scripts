"""
Script to add scan folder to HP MFP M521dn, which lacks an address book fuction
for scan folders.
"""

import requests
import urllib3

# Certs are self signed so let's ignore.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# IP addresses of printers to set the scan folders on.
printers = [,]

# Display names are also used for scan folder path in manner below.
display_names = [,]

url_path = "/hp/device/set_config_folderAddNew.html/config"
server = ""
user_name = ""
password = ""
postfix = ""

for ip in printers:
    names_so_far = []
    for name in display_names:
        # Scan folder path is {server}{lower case display name}{postfix}
        path = ("{}{}{}".format(server, name.lower(), postfix))
        post_data = {"displayName": name, "networkFolderPath": path,
          "UserName": user_name, "PassWord": password, "folderPin": None,
          "pinConfirm": None, "fileType": "Scan_PDF", "DefaultPaperSize":
          "LETTER", "ScanQualitySelection": "DPI_150", "scanColorSelection":
          "SCAN_COLOR", "filePrefix": "scan", "Save_button": "Save Only",
          "Entry_Num": None, "eProfileNameList":
          ", ".join(names_so_far) + ", " * 10, "duplicateError": "Duplicate " +
          "display name.\nEnter a different display\nname and try again.",
          "requiredField": "* required field", "invalidEntry":
          "Entry is invalid.", "pinMismatchErr": "Confirm PIN entry " +
          "doesn't match. Try again.", "pinTooShortErr": "PIN must be 4 " +
          "digits."}
        names_so_far.append(name)
        requests.post("https://{}{}".format(ip, url_path), verify=False,
          data=post_data)
        print("{}\t{}".format(ip, path))


"""
Example of POST to /hp/device/set_config_folderAddNew.html/config:
displayName=
networkFolderPath=
UserName=
PassWord=
folderPin
pinConfirm
fileType=Scan_PDF
DefaultPaperSize=LETTER
ScanQualitySelection=DPI_150
scanColorSelection=SCAN_COLOR
filePrefix=scan
Save_button=Save Only
Entry_Num
eProfileNameList=, , , , , , , , , , , , , , , , , , , ,
duplicateError=Duplicate display name.
Enter a different display
name and try again.
requiredField=* required field
invalidEntry=Entry is invalid.
pinMismatchErr=Confirm PIN entry doesn't match. Try again.
pinTooShortErr=PIN must be 4 digits.
"""
