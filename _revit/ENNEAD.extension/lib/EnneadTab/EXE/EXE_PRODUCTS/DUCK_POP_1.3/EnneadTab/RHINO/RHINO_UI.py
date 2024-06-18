#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import rhinoscriptsyntax as rs
except:
    pass


import EMAIL
import ERROR_HANDLE
import ENVIRONMENT
import USER
@ERROR_HANDLE.try_catch_error_silently
def is_enneadtab_registered(email_result = False):
    if not ENVIRONMENT.is_Rhino_environment():
        return
    if USER.is_SZ():
        return
    
    current_rui = rs.ToolbarCollectionPath("EnneadTab")
    is_enneadtab_registered =  current_rui.startswith(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Users")
    if not is_enneadtab_registered and email_result:
        EMAIL.email(sender_email=None,
                    receiver_email_list=["szhang@ennead.com"],
                    subject="EnneadTab Rhino Find Unregistered User.",
                    body="This user is not registered in EnneadTab for Rhino. Current rui is: {}.".format(current_rui),
                    body_folder_link_list=None,
                    body_image_link_list=None,
                    attachment_list=None,
                    schedule_time=None)
    return is_enneadtab_registered


def is_current_enneadtab_on_main_rui():

    current_rui = rs.ToolbarCollectionPath("EnneadTab")
    main_rui = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino\EnneadTab.rui"
    return current_rui == main_rui