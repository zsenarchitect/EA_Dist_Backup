#!/usr/bin/python
# -*- coding: utf-8 -*-


import EXE
import FOLDER
import DATA_FILE


def email_error(traceback, tool_name, error_from_user, subject_line="EnneadTab Auto Email Error Log"):

    import time
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    body = "{}\nError happens on {}'s machine when running {}.\n\nDetail below:\n{}'".format(
        t, error_from_user, tool_name, traceback)
    email(sender_email=None,
          receiver_email_list=["szhang@ennead.com"],
          subject=subject_line,
          body=body,
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None,
          schedule_time=None)
    # print ("Email sent.")


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

    exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\EA_EMAIL\\EA_EMAIL.exe"

    try:
        EXE.open_file_in_default_application(exe_location)
    except Exception as e:
        print(exe_location)
        print(str(e))


def send_email_main():

    import win32com.client
    import json
    import sys
    import traceback
    sys.path.append(
        r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\lib')
    sys.path.append(
        r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
    import EnneadTab

    file_name = "EA_EMAIL.json"
    dump_folder = EnneadTab.FOLDER.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    if not EnneadTab.FOLDER.is_file_exist_in_folder(file_name, dump_folder):
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
    send_email_main()
