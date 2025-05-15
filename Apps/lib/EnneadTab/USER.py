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

# Initialize as None to enable lazy loading
PLUGIN_DEVELOPERS = None

def _get_plugin_developers():
    """Lazy load the developer dictionary.
    
    Returns:
        dict: Developer configuration mapping or empty list if access fails
    """
    global PLUGIN_DEVELOPERS
    if PLUGIN_DEVELOPERS is None:
        try:
            PLUGIN_DEVELOPERS = user_get_dev_dict() or []
        except Exception as e:
            PLUGIN_DEVELOPERS = []
    return PLUGIN_DEVELOPERS

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
    for key in _get_plugin_developers():
        system_usernames += _get_plugin_developers()[key]["system_id"]
        autodesk_usernames += _get_plugin_developers()[key]["autodesk_id"]
    return system_usernames, autodesk_usernames


def _is_EnneadTab_developer():
    """Verify if current user has developer status.

    Uses a two-step verification:
    1. Fast local cache check using egg files
    2. Fallback to developer dictionary if cache miss

    Returns:
        bool: True if user is a developer, False otherwise
    """
    dev_egg_path = "{}\\dev_egg{}".format(ENVIRONMENT.DUMP_FOLDER, ENVIRONMENT.PLUGIN_EXTENSION)
    non_dev_egg_path = "{}\\non_dev_egg{}".format(ENVIRONMENT.DUMP_FOLDER, ENVIRONMENT.PLUGIN_EXTENSION)
    
    # Check cache first
    if os.path.exists(dev_egg_path):
        return True
    if os.path.exists(non_dev_egg_path):
        return False
        
    # Cache miss - check developer dictionary
    try:
        system_usernames, autodesk_usernames = get_usernames_from_developers()
        is_dev = False
        
        if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
            is_dev = USER_NAME in system_usernames
        elif ENVIRONMENT.IS_REVIT_ENVIRONMENT:
            is_dev = get_autodesk_user_name() in autodesk_usernames
        else:
            is_dev = USER_NAME in system_usernames
            
        # Update cache with Harry Potter themed message
        cache_path = dev_egg_path if is_dev else non_dev_egg_path
        with open(cache_path, "w") as f:
            f.write("Harry, you are{} a wizard!".format("" if is_dev else " not"))
            
        return is_dev
    except Exception as e:
        print("Error checking developer status: {}".format(e))
        return False



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
    try:
        out = []
        developers = _get_plugin_developers()
        if not developers or not isinstance(developers, dict):
            return ["szhang@ennead.com"]  # Default fallback
            
        for developer_data in developers.values():
            if not isinstance(developer_data, dict):
                continue
                
            if "system_id" not in developer_data or "email" not in developer_data:
                continue
                
            if len(developer_data["system_id"]) == 0:
                continue
                
            # Make sure we're dealing with a list
            if isinstance(developer_data["email"], list):
                out.extend(developer_data["email"])
            else:
                # Handle single email as string case
                out.append(developer_data["email"])
        
        # Always return at least one developer email
        if not out:
            return ["szhang@ennead.com"]
            
        return out
    except Exception as e:
        print("Error getting Rhino developer emails: {}".format(e))
        return ["szhang@ennead.com"]  # Fallback to default

def get_revit_developer_emails():
    """Get email addresses for all Revit developers.

    Filters developer list to include only those with Autodesk access
    permissions.

    Returns:
        list: Email addresses of developers with Autodesk access
    """
    try:
        out = []
        developers = _get_plugin_developers()
        if not developers or not isinstance(developers, dict):
            return ["szhang@ennead.com"]  # Default fallback
            
        for developer_data in developers.values():
            if not isinstance(developer_data, dict):
                continue
                
            if "autodesk_id" not in developer_data or "email" not in developer_data:
                continue
                
            if len(developer_data["autodesk_id"]) == 0:
                continue
                
            # Make sure we're dealing with a list
            if isinstance(developer_data["email"], list):
                out.extend(developer_data["email"])
            else:
                # Handle single email as string case
                out.append(developer_data["email"])
        
        # Always return at least one developer email
        if not out:
            return ["szhang@ennead.com"]
            
        return out
    except Exception as e:
        print("Error getting Revit developer emails: {}".format(e))
        return ["szhang@ennead.com"]  # Fallback to default



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

