#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import USER_CONSTANTS
import ENVIRONMENT_CONSTANTS

from USER_CONSTANTS import USER_NAME, IS_FAKE_ACCOUNT_MODE
from USER_CONSTANTS import ENNEADTAB_DEVELOPERS
from USER_CONSTANTS import RHINO_RUI_EDITOR, IS_CURRENT_RHINO_RUI_EDITOR
from USER_CONSTANTS import OFFLINE_RHINO_USERS


import NOTIFICATION
import DATA_FILE
import SPEAK
import FOLDER
import UNIT_TEST



for name, data in ENNEADTAB_DEVELOPERS.items():
    if data["github_local"] is None:
        data["github_local"] = ["C:\\Users\\{}\\github".format(x) for x in data["system"]]





def get_dev_name_from_username(username):
    """Get the full name of EnneadTab developer given username or Autodesk ID.

    Args:
        developers_dict (dict): Dictionary of developers. Key is the name of the developer, value is a dictionary including at least two keys: "system" and "autodesk". The value of each subkey is a list of usernames.
        username (str): The username or Autodesk ID to check.

    Returns:
        str: The full name of the developer, if available. None if not available.
    """
    for developer, data in ENNEADTAB_DEVELOPERS.items():
        usernames = data["system"] + data["autodesk"]
        if username in usernames:
            return developer
    return None


def get_dev_value_from_username(username, key):
    """Get the value of a key of EnneadTab developer given username or Autodesk ID.

    Args:
        developers_dict (dict): Dictionary of developers. Key is the name of the developer, value is a dictionary including at least two keys: "system" and "autodesk". The value of each subkey is a list of usernames.
        username (str): The username or Autodesk ID to check.
        key (str): The key to get the value from.

    Returns:
        str: The value of the key, if available. None if not available.
    """
    for data in ENNEADTAB_DEVELOPERS.values():
        usernames = data["system"] + data["autodesk"]
        if username in usernames:
            return data[key]
    return None
    

def get_usernames_from_developers():
    """Get all usernames from a dictionary of developers.

    Args:
        username (str): The username or Autodesk ID to check.

    Returns:
        list: Any possible system usernames.
        list: Any possible autodesk usernames.
    """
    
    system_usernames = []
    autodesk_usernames = []
    for key in ENNEADTAB_DEVELOPERS:
        system_usernames += ENNEADTAB_DEVELOPERS[key]["system"]
        autodesk_usernames += ENNEADTAB_DEVELOPERS[key]["autodesk"]
    return system_usernames, autodesk_usernames

def is_terminal_developer():
    system_user_names, _ = get_usernames_from_developers()
    return USER_NAME in system_user_names
    
    
def is_rhino_developer():
    """Checks if the current user is a developer of EnneadTab for Rhino.

    Returns:
        bool: True if the current user is authorized, False if not.
    """
    if is_SZ():
        return True
    # if is_enneadtab_developer():
    #     return True

    if USER_NAME in ["colin.matthews", "OtherUserAutodeskId_2"]:
        return True
    return False


def is_revit_developer():
    """Checks if the current user is a developer of EnneadTab for Revit.

    Returns:
        bool: True if the current user is authorized, False if not.
    """
    if is_SZ():
        return True
    # if is_enneadtab_developer():
    #     return True

    if get_autodesk_user_name() in ["OtherUserAutodeskId_1", "OtherUserAutodeskId_2"]:
        return True
    return False


def is_enneadtab_developer(pop_toast=False, additional_tester_ID=[]):
    """Checks if the current user is a developer of EnneadTab.

    Args:
        pop_toast (bool, optional): If True, shows a notification in Revit when a developer is identified. Defaults to False.
        additional_tester_ID (list, optional): Additional system usernames for tester functionality.

    Returns:
        bool: True if the current user is a developer of EnneadTab, False if not.
    """
    # declare username variables
    current_user = USER_NAME
    system_usernames, autodesk_usernames = get_usernames_from_developers()

    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        if current_user in system_usernames:
            return True
        return False

    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        
        try:
            app = __revit__
            if hasattr (app, "Application"):
                app = __revit__.Application
        except:
           
            return current_user in autodesk_usernames
                
            

        if app.Username in autodesk_usernames:
            if pop_toast:
                developer_name = get_dev_name_from_username(app.Username)
                temp_note = "Welcome back, {}!".format(developer_name)
                NOTIFICATION.toast(sub_text="", main_text=temp_note)
                SPEAK.speak(temp_note)
                # print("#####EnneadTab is operated by Sen Zhang")
            return True

        if app.Username in additional_tester_ID:
            # print("additional test user found = {}".format(app.Username))
            return True

        return False

    # in all other terminal conditions:
    if current_user in system_usernames:
        return True
    return False

# IS_ENNEADTAB_DEVELOPER = is_enneadtab_developer()

def is_SZ(pop_toast=False, additional_tester_ID=[]):
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():

        return USER_NAME in ["szhang" , "sen.zhang"]
       

    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        try:
            app = __revit__.Application
        except:
            try:
                app = __revit__
            except:
                if os.environ["USERPROFILE"] == r"C:\Users\szhang":
                    return True
                return False

        if app.Username == "szhangXNLCX":
            if pop_toast:
                temp_note = "Welcome back! Sen Zhang"
                NOTIFICATION.toast(sub_text="", main_text=temp_note)
                SPEAK.speak(temp_note)
                # print "#####EnneadTab is operated by Sen Zhang"
            return True

        if app.Username in additional_tester_ID:
            # print "additional test user found = {}".format(app.Username)
            return True

        return False

    # in all other termnial condition
    return USER_NAME in ["szhang" , "sen.zhang"]


def get_user_name():
    """Get the system username of the current user.

    Returns:
        str: System username of the current user.
    """
    return os.environ["USERPROFILE"].split("\\")[-1]
    return USER_NAME



def get_autodesk_user_name():
    """Get the Autodesk username of the current user.

    Returns:
        str: Autodesk username of the current user.
    """
    try:
        import REVIT
        return REVIT.REVIT_APPLICATION.get_application().Username
    except:
        try:
            if not ENVIRONMENT_CONSTANTS.IS_L_DRIVE_ACCESSIBLE:
                return "Not found becasue cannot access L drive"
        except:
            pass
        file = DATA_FILE.get_revit_user_file()
        if file is None:
            return "no Revit account for EnneadTab for Revit" 
        data = DATA_FILE.read_json_file_safely(file)
        key = "Autodesk_ID"
        return data[key]


def get_all_revit_users():
    """Get all system usernames of the users who have used EnneadTab for Revit.

    Returns:
        list of str: System usernames of the users who have used EnneadTab for Revit. 
    """
    folder = FOLDER.get_revit_user_folder()
    return [x.replace(".json", "") for x in FOLDER.get_filenames_in_folder(folder) if "Error_Log" not in x]


def get_all_revit_beta_testers(return_email=False, include_SZ=False):
    """Get all system usernames of the users who have used EnneadTab for Revit and are beta testers.

    Args:
        return_email (bool, optional): If True, returns a list of email addresses. If False, returns a list of system usernames. Defaults to False.
        include_SZ (bool, optional): 

    Returns:
        _type_: _description_
    """
    names = get_all_revit_users()
    names = filter(lambda x: is_revit_beta_tester(x, include_SZ), names)
    if return_email:
        return ["{}@ennead.com".format(x) for x in names]
    return names


def is_revit_beta_tester(name=None, include_SZ=False):

    if include_SZ:
        if USER_NAME == "szhang":
            return True

    if not name:
        name = USER_NAME

    file = DATA_FILE.get_revit_user_file(name)

    # for SH people they cannot get a valid setting file, so i will try everyone as Non tester
    if not os.path.exists(file):
        return False

    data = DATA_FILE.read_json_file_safely(file)
    if not data:
        return False
    key = "is_beta_tester"
    if not data.has_key(key):
        data[key] = False
        set_revit_beta_tester(is_tester=False)
        return False
    return data[key]


# rewritten to incorporate new developer authentication

# def is_revit_beta_tester(name = None, include_enneadtab_developers = False):
#     """Checks if the current user is a beta tester of EnneadTab for Revit.

#     Args:
#         name (str, optional): System username of the user to be checked. If None, the current user will be checked. Defaults to None.
#         include_enneadtab_developers (bool, optional): If True, the developers of EnneadTab will be considered as beta testers. Defaults to False.

#     Returns:
#         bool: True if the current user is a beta tester of EnneadTab for Revit, False if not.
#     """
#     system_usernames, autodesk_usernames = get_usernames_from_developers(enneadtab_developers)

#     if include_enneadtab_developers:
#         for user in system_usernames:
#             if USER_NAME == user:
#                 return True

#     if not name:
#         name = USER_NAME

#     file = DATA_FILE.get_revit_user_file(name)

#     # for SH people they cannot get a valid setting file, so i will try everyone as Non tester
#     if not os.path.exists(file):
#         return False

#     data = DATA_FILE.read_json_file_safely(file)
#     if not data:
#         return False
#     key = "is_beta_tester"
#     if not data.has_key(key):
#         data[key] = False
#         set_revit_beta_tester(is_tester = False)
#         return False
#     is_beta_tester = data[key].lower() == "true"
#     return is_beta_tester


def set_revit_beta_tester(is_tester):
    """Set the current user as a beta tester of EnneadTab for Revit.

    Args:
        is_tester (bool): True to set the current user as a beta tester, False to set the current user as a non-beta tester.
    """
    file = DATA_FILE.get_revit_user_file()
    data = DATA_FILE.read_json_file_safely(file)
    key = "is_beta_tester"
    data[key] = is_tester
    DATA_FILE.save_dict_to_json(data, file)

def get_rhino_developer_emails():
    out = []
    for developer_data in ENNEADTAB_DEVELOPERS.values():
        if len(developer_data["system"]) == 0:
            continue
        out += developer_data["email"]
    return out

def get_revit_developer_emails():
    out = []
    for developer_data in ENNEADTAB_DEVELOPERS.values():
        if len(developer_data["autodesk"]) == 0:
            continue
        out += developer_data["email"]
    return out
    
def unit_test():
    # if is_SZ():
    #     assert is_enneadtab_developer() == False
    # assert 1>2
    print ("current user [{}] is a developer? {}".format(USER_NAME,
                                                       UNIT_TEST.print_boolean_in_color(is_enneadtab_developer())))
    print ("current user is SZ? {} ". format (UNIT_TEST.print_boolean_in_color(is_SZ())))
    print ("my system name = {}".format(USER_NAME))
    print ("my autodesk name = {}".format(get_autodesk_user_name()))
    print ("I am a rhino developer? {}".format(UNIT_TEST.print_boolean_in_color(is_rhino_developer())))
    print ("I am a revit developer? {}".format(UNIT_TEST.print_boolean_in_color(is_revit_developer())))
    
    system_usernames, autodesk_usernames = get_usernames_from_developers()
    print ("all system_usernames = {}".format(system_usernames))
    print ("all autodesk_usernames = {}".format(autodesk_usernames))
    print ("all rhino developer emails = {}".format(get_rhino_developer_emails()))
    print ("all revit developer emails = {}".format(get_revit_developer_emails()))
#############
if __name__ == "__main__":

    unit_test()
    print(__file__ + "   -----OK!")

