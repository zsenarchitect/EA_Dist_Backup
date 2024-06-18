import sys
sys.path.append("..\lib")
import EnneadTab
import win32com.client
import json

"""
# Load the JSON data from the file
with open("/home/user/Desktop/email_data.json", "r") as json_file:
    data = json.load(json_file)

# Extract the recipient, sender email, and email content from the JSON data
recipient = data['recipient']
sender = data['sender']
content = data['content']
"""
recipient = "zsenarchitect@gmail.com; szhang@ennead.com; paula.gronda@ennead.com"
recipient = "szhang@ennead.com; "
sender = "szhang@ennead.com"

content = "EnneadTab auto email"


# Connect to Outlook and send the email
outlook = win32com.client.Dispatch("Outlook.Application")
for item in dir(outlook):
    print(item)
message = outlook.CreateItem(0)
message.To = recipient
message.Subject = "test email3"
message.Body = content


# insert hyper link to folder in the body of the email
folder_link = r"I:\2135\1_Study\test print"
message.HTMLBody = content + '<br><br><a href="{0}">Click here to access the folder: {0}</a>'.format(folder_link)

# insert image to thge body of the email, make this the EnneadTab logo
logo_image_path = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EnneadTab_Logo.png"
message.HTMLBody += '<br><br><img src="{}"><br><br>'.format(logo_image_path)





# Attach a file link
file_link = r"I:\2135\2_Record\2022-12-22 ALL PLOT 100%FDD SET\2022-12-25 100% DD addendum list.docx"
message.Attachments.Add(file_link, 1)

# Attach an image
image_path = r"I:\2135\2_Photo\01_Site\DJI_0001.JPG"
message.Attachments.Add(image_path)


message.Send()
print("finish")
