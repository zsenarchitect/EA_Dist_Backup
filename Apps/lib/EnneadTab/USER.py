#!/usr/bin/python
# -*- coding: utf-8 -*-

"""User management and authentication module for EnneadTab.

This module handles user identification, permissions, and developer status across
different environments (Revit, Rhino, Terminal). Key features include:
- User identification and email resolution
- Developer status verification
- Environment-specific username handling
- Usage logging and tracking
- Developer contact management

Note:
    Developer permissions are managed through separate system and Autodesk keys
    to support environment-specific access control.
"""

import os

import traceback

import time
import ENVIRONMENT
import SECRET
import UNIT_TEST 




USER_NAME = os.environ["USERPROFILE"].split("\\")[-1]


# note: why has seperate system key and autodesk keys? becasue some 
# developer might only be handling one software, not both.
EnneadTab_DEVELOPERS = SECRET.get_dev_dict() or []


def get_EA_email_address(user_name=USER_NAME):
    """Convert system username to Ennead email address.

    Args:
        user_name (str): System username, defaults to current user

    Returns:
        str: Ennead email address in format 'username@ennead.com'
    """
    return "{}@ennead.com".format(user_name.replace(".EA",""))



def get_usernames_from_developers():
    """Extract all developer usernames from developer dictionary.

    Processes the EnneadTab_DEVELOPERS dictionary to separate system and
    Autodesk usernames for different environment authentications.

    Returns:
        tuple: (list of system usernames, list of Autodesk usernames)
    """
    
    system_usernames = []
    autodesk_usernames = []
    for key in EnneadTab_DEVELOPERS:
        system_usernames += EnneadTab_DEVELOPERS[key]["system_id"]
        autodesk_usernames += EnneadTab_DEVELOPERS[key]["autodesk_id"]
    return system_usernames, autodesk_usernames


def is_EnneadTab_developer():
    """Verify if current user has developer status.

    Checks against appropriate username list based on current environment:
    - Rhino: Checks system username
    - Revit: Checks Autodesk username
    - Other: Defaults to system username check

    Returns:
        bool: True if user is a developer, False otherwise
    """
    # declare username variables
    system_usernames, autodesk_usernames = get_usernames_from_developers()

    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        return USER_NAME in system_usernames

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return get_autodesk_user_name() in autodesk_usernames


    # in all other terminal conditions:
    return USER_NAME in system_usernames



def get_autodesk_user_name():
    """Retrieve current user's Autodesk username.

    Only functional in Revit environment. Handles potential errors
    when accessing Revit API.

    Returns:
        str: Autodesk username if in Revit, None otherwise or on error
    """
    if not ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return None
    try:
        from REVIT import REVIT_APPLICATION
        return REVIT_APPLICATION.get_app().Username
    except Exception as e:
        # to-do: add try because Rhino 8 traceback is not working peoperly. This should be recheck in future Rhino 8.
        try:
            print ("Cannot get Autodesk username becasue {}".format(traceback.format_exc()))
        except:
            print (e)
        return None
    
        

IS_DEVELOPER = is_EnneadTab_developer()



def update_user_log():
    """Record user activity timestamp in shared log file.

    Creates or updates a user-specific log file with current timestamp.
    File is stored in shared location for usage tracking.
    """
    import DATA_FILE
    with DATA_FILE.update_data("USER_LOG_{}.sexyDuck".format(USER_NAME), is_local=False) as data:
        if "log" not in data.keys():
            data["log"] = []
        data["log"].append(time.time())

try:
    update_user_log()
except Exception as e:
    pass

def get_rhino_developer_emails():
    """Get email addresses for all Rhino developers.

    Returns:
        list: Email addresses of developers with system access
    """
    out = []
    for developer_data in EnneadTab_DEVELOPERS.values():
        if len(developer_data["system_id"]) == 0:
            continue
        out += developer_data["email"]
    return out

def get_revit_developer_emails():
    """Get email addresses for all Revit developers.

    Returns:
        list: Email addresses of developers with Autodesk access
    """
    out = []
    for developer_data in EnneadTab_DEVELOPERS.values():
        if len(developer_data["autodesk_id"]) == 0:
            continue
        out += developer_data["email"]
    return out



def unit_test():
    """Run diagnostic tests on user management functions.

    Tests include:
    - Current user identification
    - Developer status verification
    - Username resolution
    - Developer email list generation
    """
    import inspect
    import pprint
    # get all the global varibales in the current script
    for i, x in enumerate(sorted(globals())):
        content = globals()[x]
        
        if inspect.ismodule(content):
            
            continue
        if not x.startswith("_") and not callable(content):
            if isinstance(content,dict):
                print(x, " = ")
                pprint.pprint(content)
            else:
                print(x, " = ", content)

    print ("current user [{}] is a developer? {}".format(USER_NAME,
                                                       UNIT_TEST.print_boolean_in_color(is_EnneadTab_developer())))
    print ("my system name = {}".format(USER_NAME))
    print ("my autodesk name = {}".format(get_autodesk_user_name()))
    print ("Am I a developer? {}".format(UNIT_TEST.print_boolean_in_color(IS_DEVELOPER)))
    
    
    system_usernames, autodesk_usernames = get_usernames_from_developers()
    print ("all system_usernames = {}".format(system_usernames))
    print ("all autodesk_usernames = {}".format(autodesk_usernames))
    print ("all rhino developer emails = {}".format(get_rhino_developer_emails()))
    print ("all revit developer emails = {}".format(get_revit_developer_emails()))
###############
if __name__ == "__main__":
    unit_test()

