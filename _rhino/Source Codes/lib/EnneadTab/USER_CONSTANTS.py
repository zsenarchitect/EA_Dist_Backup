"""important: there should be ZERO depedency other than other CONSTANTS in this module becasue it is the base of many other module"""


import os
import ENVIRONMENT_CONSTANTS
USER_NAME = os.environ["USERPROFILE"].split("\\")[-1]


# since CBI cannot give us fake account, I need to pretend to be someone else sometime to test if things are runing nicely for office user.
# this is yet to be implemented.
IS_FAKE_ACCOUNT_MODE = False


# note: why has seperate system key and autodesk keys? becasue some 
# developer might only be handling one software, not both.
ENNEADTAB_DEVELOPERS = {
    "Sen Zhang": {
        "initials": "SZ",
        "system": ["szhang", "sen.zhang", "senzhang"],
        "autodesk": ["szhangXNLCX"],
        "github_local": None,
        "github_remote": ["zsenarchitect"],
        "email": ["szhang@ennead.com"]
    },
    "Colin Matthews": {
        "initials": "CM",
        "system": ["cmatthews", "colin.matthews"],
        "autodesk": [],
        "github_local": ["C:\\Users\\colin.matthews\\github"],
        "github_remote": ["colinlsmatthews"],
        "email": ["Colin.Matthews@ennead.com"]
    }
}

RHINO_RUI_EDITOR = "Colin Matthews" # this is the name of the developer who owns the RHINO RUI edit right..there should be only one name at any time.
IS_CURRENT_RHINO_RUI_EDITOR = USER_NAME in ENNEADTAB_DEVELOPERS[RHINO_RUI_EDITOR]["system"]




# this refer to the people who want to use it on their personal computer without L drive access. 
#this idea is abandoned for now...
OFFLINE_RHINO_USERS = ["fsun"]


def is_SH_account():
    SH_names = ["DChang",
                "XSun",
                "qian.yu",
                "Shu.Shang",
                "xxu",
                "zhuang"]
    return USER_NAME.lower() in  [x.lower() for x in SH_names]

def get_email(user_name = USER_NAME):
    return "{}@ennead.com".format(user_name.replace(".EA",""))

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


def get_local_github_folder():
    username = USER_NAME
    possible_local_github_folders = get_dev_value_from_username(username, "github_local")
    for folder in possible_local_github_folders:
        if os.path.exists(folder):
            return folder
    return None
    

def get_dev_name_from_username(username=USER_NAME):
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


    

def is_enneadtab_developer(additional_tester_ID=[]):
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
            return True

        if app.Username in additional_tester_ID:
            # print("additional test user found = {}".format(app.Username))
            return True

        return False

    # in all other terminal conditions:
    if current_user in system_usernames:
        return True
    return False



def unit_test():
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


###############
if __name__ == "__main__":
    unit_test()
