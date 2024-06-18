#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import NOTIFICATION
import USER

GITHUB_FOLDER = "C:\\Users\\szhang\\github"
if not os.path.exists(GITHUB_FOLDER):
    GITHUB_FOLDER = GITHUB_FOLDER.replace("szhang", "sen.zhang")
OFFLINE_RHINO_USERS = ["fsun"]
CURRENT_USER = os.environ["USERPROFILE"]
if os.path.exists("C:\\Users\\{}\\github".format(CURRENT_USER)):
    GITHUB_FOLDER = "C:\\Users\\{}\\github".format(CURRENT_USER)
    
    


WORKING_FOLDER_FOR_REVIT = "{}\\EnneadTab-for-Revit".format(GITHUB_FOLDER)
WORKING_FOLDER_FOR_RHINO = "{}\\EnneadTab-for-Rhino".format(GITHUB_FOLDER)

PUBLISH_FOLDER_FOR_REVIT = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published"
PUBLISH_BETA_FOLDER_FOR_REVIT = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published_Beta_Version"

PUBLISH_FOLDER_FOR_RHINO = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino"
DEPENDENCY_FOLDER = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Dependency Modules"

ARCHIVE_FOLDER_FOR_RHINO = "L:\\4b_Applied Computing\\03_Rhino\\xx_EnneadTab for Rhino_Archives"
EXE_FOLDER = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe"

IS_L_DRIVE_ACCESSIBLE = os.path.exists(PUBLISH_FOLDER_FOR_REVIT)

def is_offline_rhino_user():
    return CURRENT_USER  in OFFLINE_RHINO_USERS
  
    

def is_SZ_environment():
    if os.path.exists(GITHUB_FOLDER):
        return True
    return False


def is_SZ(pop_toast = False, additional_tester_ID = []):
    return USER.is_SZ(pop_toast, additional_tester_ID)


def get_EnneadTab_module_root():
    if is_Rhino_environment():
        return r"{}\Source Codes\lib\EnneadTab".format(get_EnneadTab_For_Rhino_root())
    if is_Revit_environment():
        return r"{}\ENNEAD.extension\lib\EnneadTab".format(get_EnneadTab_For_Revit_root())

def get_EnneadTab_For_Rhino_root():

    if is_SZ_environment() or is_offline_rhino_user():
        root = WORKING_FOLDER_FOR_RHINO
    else:
        root = PUBLISH_FOLDER_FOR_RHINO

    return root

def get_EnneadTab_For_Revit_root():

    if is_SZ_environment():
        root = WORKING_FOLDER_FOR_REVIT
    else:
        root = PUBLISH_FOLDER_FOR_REVIT

    return root

def is_Rhino_environment():
    try:
        import Rhino
        return True
    except:
        return False


def is_Revit_environment():
    try:
        from Autodesk.Revit import DB
        return True
    except:
        return False


def primary_app_name():
    if is_Rhino_environment():
        return "Rhino"



    if is_Revit_environment():

        return "Revit"

    return "EnneadTab"

def set_environment_variable_from_iron_python(key_name, value):
    """this is a ironpython method

    Args:
        key_name (_type_): _description_
        value (_type_): _description_
    """
    import System
    from System import Environment
    

    # Set the environment variable
    Environment.SetEnvironmentVariable(key_name, value, System.EnvironmentVariableTarget.User)

def set_environment_variable(key_name, value):
    """this is a python method

    Args:
        key_name (_type_): _description_
        value (_type_): _description_
    """
    os.environ[key_name] = value
    
def get_environment_variable(key_name):
    return os.environ[key_name]
    

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    # os.environ["key_name"] = "1234"
    