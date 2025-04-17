#!/usr/bin/python
# -*- coding: utf-8 -*-

"""User management and authentication module for EnneadTab.

This module handles user identification, permissions, and developer status across
different environments (Revit, Rhino, Terminal). It provides a unified interface
for user management across the EnneadTab ecosystem.

Key Features:
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


import time
import ENVIRONMENT

try:
    import UNIT_TEST 
except:
    pass




USER_NAME = os.environ["USERPROFILE"].split("\\")[-1]


# note: why has seperate system key and autodesk keys? becasue some 
# developer might only be handling one software, not both.
def user_get_dev_dict():
    """Retrieve the developer configuration dictionary.

    Accesses the secure developer configuration containing system and Autodesk
    usernames for authorized developers.

    Returns:
        dict: Developer configuration mapping or empty list if access fails
    """
    import SECRET
    return SECRET.get_dev_dict()
try:
    PLUGIN_DEVELOPERS = user_get_dev_dict() or []
except Exception as e:
    PLUGIN_DEVELOPERS = []


def get_EA_email_address(user_name=USER_NAME):
    """Convert system username to Ennead email address.

    Args:
        user_name (str, optional): System username to convert. 
            Defaults to current user.

    Returns:
        str: Ennead email address in format 'username@ennead.com'
    """
    return "{}@ennead.com".format(user_name.replace("." + ENVIRONMENT.PLUGIN_ABBR,""))



def get_usernames_from_developers():
    """Extract all developer usernames from developer dictionary.

    Processes the PLUGIN_DEVELOPERS dictionary to separate system and
    Autodesk usernames for different environment authentications.

    Returns:
        tuple: Contains (system_usernames, autodesk_usernames)
            system_usernames (list): List of system usernames
            autodesk_usernames (list): List of Autodesk usernames
    """
    system_usernames = []
    autodesk_usernames = []
    for key in PLUGIN_DEVELOPERS:
        system_usernames += PLUGIN_DEVELOPERS[key]["system_id"]
        autodesk_usernames += PLUGIN_DEVELOPERS[key]["autodesk_id"]
    return system_usernames, autodesk_usernames


def _is_EnneadTab_developer():
    """Verify if current user has developer status.

    Checks against appropriate username list based on current environment:
    - Rhino: Checks system username
    - Revit: Checks Autodesk username
    - Other: Defaults to system username check

    Returns:
        bool: True if user is a developer, False otherwise
    """
    if os.path.exists("{}\\dev_egg{}".format(ENVIRONMENT.DUMP_FOLDER, ENVIRONMENT.PLUGIN_EXTENSION)):
        return True
    # declare username variables
    system_usernames, autodesk_usernames = get_usernames_from_developers()

    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        return USER_NAME in system_usernames

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return get_autodesk_user_name() in autodesk_usernames


    # in all other terminal conditions:
    if USER_NAME in system_usernames:
        with open("{}\\dev_egg{}".format(ENVIRONMENT.DUMP_FOLDER, ENVIRONMENT.PLUGIN_EXTENSION), "w") as f:
            f.write("Harry, you are a wizard!")
    return USER_NAME in system_usernames



def get_autodesk_user_name():
    """Retrieve current user's Autodesk username.

    Only functional in Revit environment. Handles potential errors
    when accessing Revit API.

    Returns:
        str or None: Autodesk username if in Revit, None otherwise
    """
    if not ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return None
    try:
        from REVIT import REVIT_APPLICATION
        return REVIT_APPLICATION.get_app().Username
    except Exception as e:
        # to-do: add try because Rhino 8 traceback is not working peoperly. This should be recheck in future Rhino 8.
        try:
            import ERROR_HANDLE
            print ("Cannot get Autodesk username becasue {}".format(ERROR_HANDLE.get_alternative_traceback()))
        except:
            print (e)
        return None
    
        

IS_DEVELOPER = _is_EnneadTab_developer()



def update_user_log():
    """Record user activity timestamp in shared log file.

    Creates or updates a user-specific log file with current timestamp.
    File is stored in shared location for usage tracking.
    """
    import DATA_FILE
    with DATA_FILE.update_data("USER_LOG_{}".format(USER_NAME), is_local=False) as data:
        if "log" not in data.keys():
            data["log"] = []
        data["log"].append(time.time())

try:
    update_user_log()
except Exception as e:
    pass

def get_rhino_developer_emails():
    """Get email addresses for all Rhino developers.

    Filters developer list to include only those with system access
    permissions.

    Returns:
        list: Email addresses of developers with system access
    """
    out = []
    for developer_data in PLUGIN_DEVELOPERS.values():
        if len(developer_data["system_id"]) == 0:
            continue
        out += developer_data["email"]
    return out

def get_revit_developer_emails():
    """Get email addresses for all Revit developers.

    Filters developer list to include only those with Autodesk access
    permissions.

    Returns:
        list: Email addresses of developers with Autodesk access
    """
    out = []
    for developer_data in PLUGIN_DEVELOPERS.values():
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
    
    Prints results to console for verification.
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
                                                       UNIT_TEST.print_boolean_in_color(IS_DEVELOPER)))
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

