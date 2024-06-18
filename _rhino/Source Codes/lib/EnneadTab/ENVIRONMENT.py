#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import traceback

from ENVIRONMENT_CONSTANTS import HOSTER_FOLDER, IS_L_DRIVE_ACCESSIBLE
from ENVIRONMENT_CONSTANTS import GITHUB_FOLDER
from ENVIRONMENT_CONSTANTS import ECOSYSTEM_FOLDER
from ENVIRONMENT_CONSTANTS import ARCHIVE_FOLDER_FOR_RHINO
from ENVIRONMENT_CONSTANTS import EXE_FOLDER
from ENVIRONMENT_CONSTANTS import MISC_FOLDER
from ENVIRONMENT_CONSTANTS import SHARED_DATA_DUMP_FOLDER


from ENVIRONMENT_CONSTANTS import RHINO_USER_LOG_FOLDER
from ENVIRONMENT_CONSTANTS import REVIT_USER_LOG_FOLDER

from ENVIRONMENT_CONSTANTS import PUBLISH_FOLDER_FOR_REVIT
from ENVIRONMENT_CONSTANTS import PUBLISH_BETA_FOLDER_FOR_REVIT
from ENVIRONMENT_CONSTANTS import CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT
from ENVIRONMENT_CONSTANTS import CORE_MODULE_FOLDER_FOR_PUBLISHED_BETA_REVIT

from ENVIRONMENT_CONSTANTS import PUBLISH_FOLDER_FOR_RHINO
from ENVIRONMENT_CONSTANTS import CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO

from ENVIRONMENT_CONSTANTS import DEPENDENCY_FOLDER_LEGACY


import ENVIRONMENT_CONSTANTS

import USER_CONSTANTS

import USER
import UNIT_TEST




IS_DEV_ENVIRONMENT = False






if USER_CONSTANTS.is_enneadtab_developer():
    IS_DEV_ENVIRONMENT = True
    # rhino and revit dev check will be deprecated upon implementation of is_enneadtab_developer() when that is bug free.
    
    dev_username = USER_CONSTANTS.USER_NAME
    dev_name = USER_CONSTANTS.get_dev_name_from_username(dev_username)
    local_github_location_list = USER_CONSTANTS.ENNEADTAB_DEVELOPERS[dev_name]["github_local"] or GITHUB_FOLDER
    if isinstance(local_github_location_list, list):
        
        for location in local_github_location_list:
            if os.path.exists(location):
                GITHUB_FOLDER = location
                break
    else:
        # if is None, this will use the default github location, which is szhang github folder
        pass


DISTIBUTION_FOLDER = "{}\\EA_Dist".format(GITHUB_FOLDER)

WORKING_FOLDER_FOR_REVIT = "{}\\EnneadTab-for-Revit".format(GITHUB_FOLDER)
WORKING_FOLDER_FOR_RHINO = "{}\\EnneadTab-for-Rhino".format(GITHUB_FOLDER)


if os.path.exists(WORKING_FOLDER_FOR_REVIT):
    ENNEADTAB_FOR_REVIT = WORKING_FOLDER_FOR_REVIT
else:
    ENNEADTAB_FOR_REVIT = PUBLISH_FOLDER_FOR_REVIT

CORE_MODULE_FOLDER_FOR_REVIT = "{}\\ENNEAD.extension\\lib\\EnneadTab".format(WORKING_FOLDER_FOR_REVIT)
CORE_MODULE_FOLDER_FOR_RHINO = "{}\\Source Codes\\lib\\EnneadTab".format(WORKING_FOLDER_FOR_RHINO)

CORE_RESOURCES_FOLDER = "{}\\sources".format(os.path.dirname(__file__))
CORE_IMAGES_FOLDER = "{}\\images".format(os.path.dirname(__file__))





IS_ECOSYS_FOLDER_SETUP = os.path.isdir(ECOSYSTEM_FOLDER)

def is_offline_rhino_user():
    """Checks if current user is an offline Rhino user.

    Returns:
        bool: True if current user is an offline Rhino user.
    """
    return USER_CONSTANTS.USER_NAME in USER.OFFLINE_RHINO_USERS


def get_EnneadTab_module_root():
    """Get the module folder for EnneadTab, depending on the user environment.

    Returns:
        str: The root folder path for EnneadTab.
    """
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        return r"{}\Source Codes\lib\EnneadTab".format(get_EnneadTab_For_Rhino_root())
    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        return r"{}\ENNEAD.extension\lib\EnneadTab".format(get_EnneadTab_For_Revit_root())


def get_EnneadTab_For_Rhino_root():
    """Get the root folder for EnneadTab for Rhino, depending on the user type.

    Returns:
        str: The root folder path for EnneadTab for Rhino.
    """
    if IS_DEV_ENVIRONMENT:# or is_offline_rhino_user() stop using offline user because it is not ready
        root = WORKING_FOLDER_FOR_RHINO
    else:
        root = PUBLISH_FOLDER_FOR_RHINO

    if not os.path.isdir(root):
        root = PUBLISH_FOLDER_FOR_RHINO
    return root


def get_EnneadTab_For_Revit_root():
    """Get the root folder for EnneadTab for Revit, depending on the user type.

    Returns:
        str: The root folder path for EnneadTab for Revit.
    """
    if IS_DEV_ENVIRONMENT:
        root = WORKING_FOLDER_FOR_REVIT
    else:
        root = PUBLISH_FOLDER_FOR_REVIT
    if not os.path.isdir(root):
        root = PUBLISH_FOLDER_FOR_REVIT
    return root


def is_Grasshopper_environment():
    """Check if current environment is Grasshopper.

    Returns:
        bool: True if current environment is Grasshopper.
    """
    try:
        import Grasshopper # pyright: ignore
        return True
    except:
        return False


def is_exclusive_Rhino_environment():
    """Check if current environment is Rhino and not Grasshopper.

    Returns:
        bool: True if current environment is Rhino and not Grasshopper.
    """
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment() and not ENVIRONMENT_CONSTANTS.is_Grasshopper_environment():
        return True
    return False


def primary_app_name():
    """Get the primary app name, depending on the app in use.

    Returns:
        str: The primary app name.
    """
    if ENVIRONMENT_CONSTANTS.is_Grasshopper_environment():
        return "Grasshopper"

    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        return "Rhino"

    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        return "Revit"

    return "EnneadTab"


def set_environment_variable_from_iron_python(key_name, value):
    """Set an environment variable in IronPython.

    Args:
        key_name (str): The environment variable name.
        value (str): The environment variable value.
    """
    import System # pyright: ignore
    from System import Environment # pyright: ignore

    # Set the environment variable
    Environment.SetEnvironmentVariable(key_name, value, System.EnvironmentVariableTarget.User)


def set_environment_variable(key_name, value):
    """Set an environment variable in CPython.

    Args:
        key_name (str): The environment variable name.
        value (str): The environment variable value.
    """
    os.environ[key_name] = value


def get_environment_variable(key_name, default_value = None):
    """Get an environment variable.

    Args:
        key_name (str): The environment variable name.

    Returns:
        str: The environment variable value.
    """

    return os.environ.get(key_name, default_value)


if is_exclusive_Rhino_environment():
    import Rhino # pyright: ignore
    import scriptcontext as sc
    sc.doc = Rhino.RhinoDoc.ActiveDoc


def unit_test():
    
    print("Is currently in developer environemnt? {}".format(UNIT_TEST.print_boolean_in_color(IS_DEV_ENVIRONMENT)))
    print ("Current environment is Revit? {}".format(UNIT_TEST.print_boolean_in_color(ENVIRONMENT_CONSTANTS.is_Revit_environment())))
    print ("Current environment is Rhino? {}".format(UNIT_TEST.print_boolean_in_color(ENVIRONMENT_CONSTANTS.is_Rhino_environment())))
    print ("Current environment is terminal? {}".format(UNIT_TEST.print_boolean_in_color(ENVIRONMENT_CONSTANTS.is_terminal_environment())))
    print ("\n")
    print ("current github folder = {}".format (GITHUB_FOLDER))
    print ("L drive is accessible? {}".format(UNIT_TEST.print_boolean_in_color(IS_L_DRIVE_ACCESSIBLE)))
    print ("core module for rhino local = {}".format(CORE_MODULE_FOLDER_FOR_RHINO))
    print ("core module for revit local = {}".format(CORE_MODULE_FOLDER_FOR_REVIT))
    print ("core module for published rhino = {}".format(CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO))
    print ("core module for published revit = {}".format(CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT))
    
    if not USER.is_enneadtab_developer():
        assert True == IS_L_DRIVE_ACCESSIBLE
#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    # os.environ["key_name"] = "1234"
    unit_test()
