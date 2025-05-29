#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Environment configuration and detection module for EnneadTab.

This module handles environment setup, path configurations, and runtime environment detection
for the EnneadTab ecosystem. It supports multiple applications including Revit, Rhino,
and terminal environments.

Key Features:
- Path configuration for development and production environments
- Application environment detection (Revit, Rhino, Grasshopper)
- System environment checks (AVD, Python version)
- Filesystem management for temp and dump folders
- Network drive availability monitoring

Note:
    Network drive connectivity is managed through GitHub distribution rather than 
    direct network mapping to optimize IT infrastructure costs.



Unfortunately IT department cannot make L drive and other drive to be connnected by default ever since the Azure dirve migration.
There are money to be saved to disconnect the drive, so we need to use github to push update to all users.

Dont tell me it is a security risk, it is NOT.



"""

import os
import sys
from datetime import datetime

PLUGIN_NAME = "EnneadTab"
PLUGIN_ABBR = "EA"
PLUGIN_EXTENSION = ".sexyDuck"

IS_PY3 = sys.version.startswith("3")
IS_PY2 = not IS_PY3
IS_IRONPYTHON = sys.platform == "cli"


# this is the repo folder if you are a developer, or EA_dist if you are a normal user
ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

USER_PROFILE_FOLDER = os.environ["USERPROFILE"]
USER_DOCUMENT_FOLDER = os.path.join(USER_PROFILE_FOLDER, "Documents")
USER_DOWNLOAD_FOLDER = os.path.join(USER_PROFILE_FOLDER, "downloads")

USER_DESKTOP_FOLDER = os.path.join(USER_PROFILE_FOLDER, "Desktop")
ONE_DRIVE_DESKTOP_FOLDER = os.path.join(USER_PROFILE_FOLDER, 
                                        "OneDrive - Ennead Architects", "Desktop")
ONE_DRIVE_DOCUMENTS_FOLDER = os.path.join(USER_PROFILE_FOLDER, 
                                          "OneDrive - Ennead Architects", "Documents")
if not os.path.exists(ONE_DRIVE_DESKTOP_FOLDER):
    ONE_DRIVE_DESKTOP_FOLDER = USER_DESKTOP_FOLDER
USER_APPDATA_FOLDER = os.path.join(USER_PROFILE_FOLDER, "AppData")
ECO_SYS_FOLDER_MODERN = os.path.join(USER_DOCUMENT_FOLDER, 
                                     "{}-Ecosystem".format(PLUGIN_NAME))
ECO_SYS_FOLDER_LEGACY = os.path.join(USER_DOCUMENT_FOLDER, 
                                     "{} Ecosystem".format(PLUGIN_NAME))
####################################
# TO_DO: make commit change to MODERN after May 1st
if datetime.now().date() > datetime(2026, 5, 1).date():
    ECO_SYS_FOLDER = ECO_SYS_FOLDER_MODERN
else:
    ECO_SYS_FOLDER = ECO_SYS_FOLDER_LEGACY
    try:
        if os.path.exists(ECO_SYS_FOLDER_LEGACY):
            import shutil
            for root, dirs, files in os.walk(ECO_SYS_FOLDER_LEGACY):
                for file in files:
                    if file.endswith(PLUGIN_EXTENSION):
                        rel_path = os.path.relpath(os.path.join(root, file), 
                                                ECO_SYS_FOLDER_LEGACY)
                        shutil.copy(os.path.join(ECO_SYS_FOLDER_LEGACY, rel_path), 
                                    os.path.join(ECO_SYS_FOLDER_MODERN, rel_path))
    except:
        pass

####################################
DUMP_FOLDER = os.path.join(ECO_SYS_FOLDER, "Dump")
INSTALLATION_FOLDER = os.path.join(ROOT, "Installation")

def _secure_folder(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except Exception as e:
            print("Cannot secure folder [{}] becasue {}".format(folder, e))

map(_secure_folder, [ECO_SYS_FOLDER, ECO_SYS_FOLDER_MODERN, DUMP_FOLDER])




APP_FOLDER = os.path.join(ROOT, "Apps")


LIB_FOLDER = os.path.join(APP_FOLDER, "lib")
CORE_FOLDER = os.path.join(LIB_FOLDER, PLUGIN_NAME)
IMAGE_FOLDER = os.path.join(CORE_FOLDER, "images")
AUDIO_FOLDER = os.path.join(CORE_FOLDER, "audios")
DOCUMENT_FOLDER = os.path.join(CORE_FOLDER, "documents")
SCRIPT_FOLDER = os.path.join(CORE_FOLDER, "scripts")


EXE_PRODUCT_FOLDER = os.path.join(LIB_FOLDER, "ExeProducts")
WINDOW_TEMP_FOLDER = os.path.join("C:\\", "temp", "{}_Dump".format(PLUGIN_NAME))
_secure_folder(WINDOW_TEMP_FOLDER)

DEPENDENCY_FOLDER = os.path.join(LIB_FOLDER, "dependency")
if IS_PY2:
    DEPENDENCY_FOLDER = os.path.join(DEPENDENCY_FOLDER, "py2")
else:
    DEPENDENCY_FOLDER = os.path.join(DEPENDENCY_FOLDER, "py3")
PY3_DEPENDENCY_FOLDER = os.path.join(LIB_FOLDER, "dependency", "py3")




REVIT_FOLDER_KEYNAME = "_revit"
REVIT_FOLDER = os.path.join(APP_FOLDER, REVIT_FOLDER_KEYNAME)

################# rhino extension ####################
RHINO_FOLDER_KEYNAME = "_rhino"
RHINO_FOLDER = os.path.join(APP_FOLDER, RHINO_FOLDER_KEYNAME)
DIST_RUI_CLASSIC = os.path.join(RHINO_FOLDER, "{}_For_Rhino_Classic.rui".format(PLUGIN_NAME))
DIST_RUI_MODERN = os.path.join(RHINO_FOLDER, "{}_For_Rhino_Modern.rui".format(PLUGIN_NAME))
ACTIVE_MODERN_RUI = os.path.join(DUMP_FOLDER, "{}_For_Rhino_Modern.rui".format(PLUGIN_NAME))
INSTALLATION_RUI = os.path.join(INSTALLATION_FOLDER, "{}_For_Rhino_Installer.rui".format(PLUGIN_NAME))
RHINO_INSTALLER_SETUP_FOLDER = os.path.join(LIB_FOLDER, PLUGIN_NAME, "RHINO")

################# indesign extension ####################
INDESIGN_FOLDER_KEYNAME = "_indesign"
INDESIGN_FOLDER = os.path.join(APP_FOLDER, INDESIGN_FOLDER_KEYNAME)

################### knowledge database ####################
KNOWLEDGE_RHINO_FILE = "{}\\knowledge_rhino_database{}".format(RHINO_FOLDER, PLUGIN_EXTENSION)
KNOWLEDGE_REVIT_FILE = "{}\\knowledge_revit_database{}".format(REVIT_FOLDER, PLUGIN_EXTENSION)
for _ in [KNOWLEDGE_RHINO_FILE, KNOWLEDGE_REVIT_FILE]:
    if not os.path.exists(_):
        import json
        try:
            with open(_, "w") as f:
                json.dump({}, f, indent=4)
        except Exception as e:
            print("Cannot create file [{}] becasue {}".format(_, e))

################### revit extension ####################
PRIMARY_EXTENSION_NAME = "EnneaDuck"
REVIT_PRIMARY_EXTENSION = os.path.join(
    REVIT_FOLDER, "{}.extension".format(PRIMARY_EXTENSION_NAME)
)
REVIT_PRIMARY_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "{}.tab".format(PLUGIN_NAME))
REVIT_LIBRARY_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "{} Library.tab".format(PLUGIN_NAME))
REVIT_TAILOR_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "{} Tailor.tab".format(PLUGIN_NAME))



#################### L drive folder ####################
L_DRIVE_HOST_FOLDER = os.path.join("L:\\", "4b_Design Technology")
if not os.path.exists(L_DRIVE_HOST_FOLDER):
    L_DRIVE_HOST_FOLDER = os.path.join("L:\\", "4b_Applied Computing")


DB_FOLDER = os.path.join(L_DRIVE_HOST_FOLDER, "EnneadTab-DB")
if not os.path.exists(DB_FOLDER):
    DB_FOLDER = os.path.join(L_DRIVE_HOST_FOLDER, "05_EnneadTab", "EnneadTab-DB")
SHARED_DUMP_FOLDER = os.path.join(DB_FOLDER, "Shared Data Dump")

STAND_ALONE_FOLDER = os.path.join(DB_FOLDER, "Stand Alone Tools")



############# engine ####################
ENGINE_FOLDER = os.path.join(APP_FOLDER, "_engine")
SITE_PACKAGES_FOLDER = os.path.join(ENGINE_FOLDER, "Lib")
map(_secure_folder, [ENGINE_FOLDER, SITE_PACKAGES_FOLDER])

IS_OFFLINE_MODE = not os.path.exists(SHARED_DUMP_FOLDER)
if IS_OFFLINE_MODE:
    SHARED_DUMP_FOLDER = DUMP_FOLDER


# this is to remove any transitional folder from IT transition, not intented to be ussed anywhere else
__legacy_one_drive_folder = [os.path.join(USER_PROFILE_FOLDER, "OneDrive - Ennead Architects", "Documents", "{} Ecosystem".format(PLUGIN_NAME)),
                            os.path.join(USER_PROFILE_FOLDER, "OneDrive - Ennead Architects", "Documents", "{}-Ecosystem".format(PLUGIN_NAME))]

for _folder in __legacy_one_drive_folder:
    if os.path.exists(_folder):
        print("legacy one drive folder found, this is not gooodddddddddddddddddddddddddddddddddddd: {}".format(_folder))
        import shutil
        try:
            shutil.rmtree(_folder)
        except:
            pass


def cleanup_dump_folder():
    """Clean up temporary files from the dump folder.

    Removes files older than 3 days from the DUMP_FOLDER, excluding protected file types:
    .json, PLUGIN_EXTENSION, .txt, .DuckLock, and .rui files.
    
    This function runs silently and handles file deletion errors gracefully.
    """
    import os
    import time

    cutoff_time = time.time() - (3 * 24 * 60 * 60)  # 3 days
    protected_extensions = {'.json', PLUGIN_EXTENSION, ".txt", ".lock", ".DuckLock", ".rui"}

    for filename in os.listdir(DUMP_FOLDER):
        file_path = os.path.join(DUMP_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue
            
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext in protected_extensions:
            continue
            
        if os.path.getmtime(file_path) < cutoff_time:
            try:
                os.remove(file_path)
            except:
                pass


def should_check_l_drive():
    """Determine if L drive should be checked based on time elapsed since last check.
    
    Ensures check happens at most once per hour.
    
    Returns:
        bool: True if an hour has passed since last check, False otherwise.
    """
    import time
    import os.path
    
    timestamp_file = os.path.join(DUMP_FOLDER, "l_drive_check.DuckLock")
    current_time = time.time()
    cutoff_time = current_time - (60 * 60)  # 1 hour
    
    # If lock file exists and is less than an hour old, don't check
    if os.path.exists(timestamp_file):
        if os.path.getmtime(timestamp_file) > cutoff_time:
            return False
    
    # Update timestamp by touching the file
    try:
        with open(timestamp_file, "w") as f:
            f.write("")
    except:
        pass
        
    return True

def should_cleanup_dump_folder():
    """Determine if dump folder should be cleaned up based on time elapsed since last cleanup.
    
    Ensures cleanup happens at most once per day.
    
    Returns:
        bool: True if a day has passed since last cleanup, False otherwise.
    """
    import time
    import os.path
    
    timestamp_file = os.path.join(DUMP_FOLDER, "dump_cleanup.DuckLock")
    current_time = time.time()
    cutoff_time = current_time - (24 * 60 * 60)  # 24 hours
    
    # If lock file exists and is less than a day old, don't cleanup
    if os.path.exists(timestamp_file):
        if os.path.getmtime(timestamp_file) > cutoff_time:
            return False
    
    # Update timestamp by touching the file
    try:
        with open(timestamp_file, "w") as f:
            f.write("")
    except:
        pass
        
    return True

def is_avd():
    """Detect if running in Azure Virtual Desktop environment.

    Returns:
        bool: True if running in AVD or GPU-PD environment, False otherwise
    """
    computer_name = get_computer_name()
  
    return "avd" in computer_name.lower() or "gpupd" in computer_name.lower()

def get_computer_name():
    """Get the computer name.

    Returns:
        str: Computer name

    """
    try:
        import clr  # pyright:ignore
        from System.Net import Dns  # pyright:ignore

        computer_name = Dns.GetHostName()
    except:
        import socket

        computer_name = socket.gethostname()

    return computer_name


def is_Rhino_8():
    """Check if current environment is Rhino 8.

    Returns:
        bool: True if running in Rhino 8, False otherwise
    """

    return str(get_rhino_version()) == "8"

def is_Rhino_7():
    """Check if current environment is Rhino 7.

    Returns:
        bool: True if running in Rhino 7, False otherwise
    """

    return str(get_rhino_version()) == "7"

def get_rhino_version(main_version_only=True):
    """Retrieve the current Rhino version.

    Args:
        main_version_only (bool, optional): If True, returns only the major version number.
            Defaults to True.

    Returns:
        str or None: Rhino version number if in Rhino environment, None otherwise
    """
    if not IS_RHINO_ENVIRONMENT:
        return None
    import Rhino  # pyright: ignore

    return Rhino.RhinoApp.ExeVersion  if main_version_only else Rhino.RhinoApp.Version

def is_Rhino_environment():
    """Check if the current environment is Rhino.

    Returns:
        bool: True if running in Rhino environment, False otherwise
    """
    try:
        import rhinoscriptsyntax  # pyright: ignore

        return True
    except:
        return False


def is_Grasshopper_environment():
    """Check if current environment is Grasshopper.

    Returns:
        bool: True if running in Grasshopper environment, False otherwise
    """
    try:
        import Grasshopper  # pyright: ignore

        return True
    except:
        return False


def is_Revit_environment():
    """Check if the current environment is Revit.

    Returns:
        bool: True if current environment is Revit.
    """
    try:
        from Autodesk.Revit import DB  # pyright: ignore

        return True
    except:
        return False


def is_RhinoInsideRevit_environment():
    """Check if the current environment is RhinoInsideRevit.

    Returns:
        bool: True if current environment is RhinoInsideRevit
    """
    try:
        import clr  # pyright: ignore

        clr.AddReference("RhinoCommon")
        clr.AddReference("RhinoInside.Revit")
        return True
    except:
        return False


def is_terminal_environment():
    """Check if the current environment is within the terminal.

    Returns:
        bool: True if current environment is a terminal.
    """
    return not is_Rhino_environment() and not is_Revit_environment()


def unit_test():
    import inspect
    # get all the global varibales in the current script

    for i, x in enumerate(sorted(globals())):
        content = globals()[x]

        if inspect.ismodule(content):
            continue

        if not x.startswith("_") and not callable(content):
            print(x, " = ", content)

            if isinstance(content, bool):
                continue

            if not isinstance(content, list):
                content = [content]

            for item in content:
                if "\\" in item:
                    is_ok = os.path.exists(item) or os.path.isdir(item)

                    if not is_ok:
                        print("!!!!!!!!!!!!! not ok: " + item)
                    # assert is_ok


IS_AVD = is_avd()
IS_RHINO_ENVIRONMENT = is_Rhino_environment()
IS_RHINO_7 = is_Rhino_7()
IS_RHINO_8 = is_Rhino_8()
IS_GRASSHOPPER_ENVIRONMENT = is_Grasshopper_environment()
IS_REVIT_ENVIRONMENT = is_Revit_environment()
IS_RHINOINSIDEREVIT_ENVIRONMENT = is_RhinoInsideRevit_environment()

def get_app_name():
    """Determine the current application environment.

    Returns:
        str: Application identifier - 'revit', 'rhino', or 'terminal'.
    """
    app_name = "terminal"
    if IS_REVIT_ENVIRONMENT:
        app_name = "revit"
    elif IS_RHINO_ENVIRONMENT:
        app_name = "rhino"
    return app_name

def alert_l_drive_not_available(play_sound = False):
    """Check L drive availability and notify user if unavailable.

    Args:
        play_sound (bool): If True, plays an error sound when L drive is unavailable.

    Returns:
        bool: True if L drive is available, False otherwise.
    """
    if  os.path.exists(L_DRIVE_HOST_FOLDER):
        return True

    note = "Friendly reminder! \n\nL drive is not available, please check your network connection or activate L drive manually.\nEnneadTab will still work, just without some public asset, such as AI related features."
    print(note)
    if play_sound:
        try:
            import SOUND
            SOUND.play_error_sound()
        except:
            pass        

    return False

# Run maintenance operations
if should_cleanup_dump_folder():
    cleanup_dump_folder()

if should_check_l_drive():
    alert_l_drive_not_available()
###############
if __name__ == "__main__":
    unit_test()

