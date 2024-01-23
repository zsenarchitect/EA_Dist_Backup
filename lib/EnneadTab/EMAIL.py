import EXE
import FOLDER
import DATA_FILE
import USER
import ENVIRONMENT_CONSTANTS
import TIME
import NOTIFICATION


def email_error(traceback, tool_name, error_from_user, subject_line="EnneadTab Auto Email Error Log"):

    import time
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    try:
        if ENVIRONMENT_CONSTANTS.is_Revit_environment():
            
            app = __revit__
            if hasattr(app, "Application"):
                app = app.Application
                
            
            
            app_uptime = TIME.get_revit_uptime()
            try:
                doc_name = app.ActiveUIDocument.Document.Title
            except:
                doc_name = "N/A"
            additional_note = "Version Build: {}\nVersion Number: {}\nVersion Name: {}\nDoc name:{}\n\nRevit UpTime: {}".format(app.VersionBuild,
                                                                                                                                app.VersionNumber,
                                                                                                                                app.VersionName,
                                                                                                                                doc_name,
                                                                                                                                app_uptime)
        elif ENVIRONMENT_CONSTANTS.is_Rhino_environment():
            import rhinoscriptsyntax as rs
            import scriptcontext as sc
            additional_note = "File in trouble:{}\nCommand history before diaster:\n{}".format(sc.doc.Path or None,
                                                                                rs.CommandHistory())

            
        else:
            additional_note = ""
    except Exception as e:
        print(e)
        additional_note = str(e)
    body = "{}\nError happens on {}'s machine when running {}.\n\nDetail below:\n{}\n\n{}".format(t, 
                                                                                             error_from_user, 
                                                                                             tool_name, 
                                                                                             traceback,
                                                                                             additional_note)
    developer_emails = ["szhang@ennead.com"]
    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        developer_emails = USER.get_revit_developer_emails()
        if "h" in app_uptime and 50 < int(app_uptime.split("h")[0]):
            email_to_self(subject="I am tired...",
                          body="Hello,\nI have been running for {}.\nLet me rest and clear cache!\n\nDid you know that restarting your Revit regularly can improve performance?\nBest regard,\nYour poor Revit.". format(app_uptime))
            
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        developer_emails = USER.get_rhino_developer_emails()


    # to-do: if current user is a developer of the software, should only sent the email to self to avoid bothering other editor during test runs.
    
    
    email(sender_email=None,
          receiver_email_list=developer_emails,
          subject=subject_line,
          body=body,
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None,
          schedule_time=None)
    # print ("Email sent.")


def email_to_self(subject="EnneadTab Auto Email",
                body=None,
                body_folder_link_list=None,
                body_image_link_list=None,
                attachment_list=None,
                schedule_time=None):
    email(receiver_email_list=["{}@ennead.com".format(USER.get_user_name())],
          subject=subject,
          body=body,
          body_folder_link_list=body_folder_link_list,
          body_image_link_list=body_image_link_list,
          attachment_list=attachment_list,
          schedule_time=schedule_time)

def email(sender_email=None,
          receiver_email_list=None,
          subject="EnneadTab Auto Email",
          body=None,
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None,
          schedule_time=None):
    """sender email is not required for outlook approch
    schedule time is the desired time in uni seconds
    """

    if not receiver_email_list:
        return
    if isinstance(receiver_email_list, str):
        print("Prefer list but ok.")
        receiver_email_list = receiver_email_list.rstrip().split(";")

    if not body:
        return

    body = body.replace("\n", "<br>")

    data = dict()
    data["sender_email"] = sender_email
    data["receiver_email_list"] = receiver_email_list
    data["subject"] = subject
    data["body"] = body
    data["body_folder_link_list"] = body_folder_link_list
    data["body_image_link_list"] = body_image_link_list
    data["attachment_list"] = attachment_list
    data["schedule_time"] = schedule_time

    file_name = "EA_EMAIL.json"
    dump_folder = FOLDER.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    DATA_FILE.save_dict_to_json(data, file_path)

    if USER.is_SZ() and False:
        exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\EMAIL_1.4\\EMAIL.exe"
    else:
        exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\EA_EMAIL\\EA_EMAIL.exe"

    try:
        EXE.open_file_in_default_application(exe_location)
    except Exception as e:
        print(exe_location)
        print(str(e))


def send_email_main():

    import traceback
    import json
    import sys
    sys.path.append(
        r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\lib')
    sys.path.append(
        r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
    import win32com.client
    import EnneadTab

    file_name = "EA_EMAIL.json"
    dump_folder = EnneadTab.FOLDER.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    if not EnneadTab.FOLDER.is_file_exist_in_folder(file_name, dump_folder):
        print ("no json")
        return

    data = EnneadTab.DATA_FILE.read_json_as_dict(file_path)

    # Extract the recipient, sender email, and email content from the JSON data
    sender_email = data["sender_email"]
    receiver_email_list = data["receiver_email_list"]
    temp = ""
    for email in receiver_email_list:
        temp += "{}; ".format(email)
    receiver_email_list = temp

    subject = data["subject"]
    body = data["body"]
    body_folder_link_list = data["body_folder_link_list"]
    body_image_link_list = data["body_image_link_list"]
    attachment_list = data["attachment_list"]
    schedule_time = data["schedule_time"]
    # recipient = "zsenarchitect@gmail.com; szhang@ennead.com; paula.gronda@ennead.com"
    # recipient = "szhang@ennead.com; paula.gronda@ennead.com"
    # sender = "szhang@ennead.com"

    content = body

    try:
        # Connect to Outlook and send the email
        outlook = win32com.client.Dispatch("Outlook.Application")
        message = outlook.CreateItem(0)
        message.To = receiver_email_list
        message.Subject = subject
        message.HTMLBody = content

        if body_folder_link_list:
            # insert hyper link to folder in the body of the email
            # folder_link = r"I:\2135\1_Study\test print"

            for link in body_folder_link_list:
                message.HTMLBody += '<br><br><a href="{0}">Click here to access the folder: {0}</a>'.format(
                    link)

        if body_image_link_list:
            # insert image to thge body of the email,
            for link in body_image_link_list:
                message.HTMLBody += '<br><br><img src="{}"><br><br>'.format(
                    link)

        # insert image to thge body of the email, make this the EnneadTab logo
        logo_image_path = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EnneadTab_Logo.png"
        message.HTMLBody += '<br><br><img src="{}"><br><br>'.format(
            logo_image_path)

        if attachment_list:
            for file in attachment_list:
                message.Attachments.Add(file, 1)

        if schedule_time:
            import time
            while time.time() < schedule_time:
                time.sleep(60)

        message.Send()
        # print ("finish")
        EnneadTab.SPEAK.speak("enni-ed tab email is sent out. Subject line: {}".format(
            subject.lower().replace("ennead", "enni-ed ")))
        EnneadTab.FOLDER.remove_exisitng_file_in_folder(dump_folder, file_name)
    except:
        print(subject)
        print(receiver_email_list)
        print(body)
        print(body_folder_link_list)
        print(body_image_link_list)
        print(attachment_list)
        print(schedule_time)

        error = traceback.format_exc()
        if "file" in locals():
            error += "\n\n{}".format(file)
        error_file = "{}\error_log.txt".format(
            EnneadTab.FOLDER.get_user_folder())
        with open(error_file, "w") as f:
            f.write(error)
        EnneadTab.EXE.open_file_in_default_application(error_file)


#################
if __name__ == "__main__":
    import traceback
    try:
        send_email_main()
        print ("tool end")
    except Exception as e:
        error = traceback.format_exc()
        print (error)
       
        import os
        error_file = "{}\\Documents\\error_log.txt".format(os.environ["USERPROFILE"])
        with open(error_file, "w") as f:
            f.write(error)
            
        
        os.startfile(error_file)

