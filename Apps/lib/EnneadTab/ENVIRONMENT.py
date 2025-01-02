#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utility functions for checking the current application environment.
Sets environment variables and paths for EnneadTab."""

import os
import sys


IS_PY3 = sys.version.startswith("3")
IS_PY2 = not IS_PY3


# this is the repo folder if you are a developer, or EA_dist if you are a normal user
ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


INSTALLATION_FOLDER = os.path.join(ROOT, "Installation")


APP_FOLDER = os.path.join(ROOT, "Apps")
REVIT_FOLDER = os.path.join(APP_FOLDER, "_revit")
RHINO_FOLDER = os.path.join(APP_FOLDER, "_rhino")
PRIMARY_EXTENSION_NAME = "EnneaDuck"
REVIT_PRIMARY_EXTENSION = os.path.join(
    REVIT_FOLDER, "{}.extension".format(PRIMARY_EXTENSION_NAME)
)
REVIT_PRIMARY_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "Ennead.tab")
REVIT_LIBRARY_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "Ennead Library.tab")
REVIT_TAILOR_TAB = os.path.join(REVIT_PRIMARY_EXTENSION, "Ennead Tailor.tab")

L_DRIVE_HOST_FOLDER = "L:\\4b_Applied Computing"
DB_FOLDER = "{}\\EnneadTab-DB".format(L_DRIVE_HOST_FOLDER)
SHARED_DUMP_FOLDER = DB_FOLDER + "\\Shared Data Dump"


LIB_FOLDER = os.path.join(APP_FOLDER, "lib")
CORE_FOLDER = os.path.join(LIB_FOLDER, "EnneadTab")
IMAGE_FOLDER = os.path.join(CORE_FOLDER, "images")
AUDIO_FOLDER = os.path.join(CORE_FOLDER, "audios")
DOCUMENT_FOLDER = os.path.join(CORE_FOLDER, "documents")


EXE_PRODUCT_FOLDER = os.path.join(LIB_FOLDER, "ExeProducts")
WINDOW_TEMP_FOLDER = "C:\\temp\\EnneadTab Dump"
if not os.path.exists(WINDOW_TEMP_FOLDER):
    try:
        os.makedirs(WINDOW_TEMP_FOLDER)
    except Exception as e:
        print("Cannot secure folder [{}] becasue {}".format(WINDOW_TEMP_FOLDER, e))

DEPENDENCY_FOLDER = os.path.join(LIB_FOLDER, "dependency")
if IS_PY2:
    DEPENDENCY_FOLDER += "\\py2"
else:
    DEPENDENCY_FOLDER += "\\py3"
PY3_DEPENDENCY_FOLDER =  os.path.join(LIB_FOLDER, "dependency", "py3")


USER_PROFILE_FOLDER = os.environ["USERPROFILE"]
USER_DOCUMENT_FOLDER = "{}\\Documents".format(USER_PROFILE_FOLDER)
USER_DOWNLOAD_FOLDER = "{}\\downloads".format(USER_PROFILE_FOLDER)
# # desktop folder is tricky, reason unknown, maybe related to the One drive desktop sync?
USER_DESKTOP_FOLDER = "{}\\Desktop".format(USER_PROFILE_FOLDER)
ONE_DRIVE_DESKTOP_FOLDER = "{}\\OneDrive - Ennead Architects\\Desktop".format(USER_PROFILE_FOLDER)
if not os.path.exists(ONE_DRIVE_DESKTOP_FOLDER):
    ONE_DRIVE_DESKTOP_FOLDER = USER_DESKTOP_FOLDER
USER_APPDATA_FOLDER = "{}\\AppData".format(USER_PROFILE_FOLDER)
ECO_SYS_FOLDER = "{}\\EnneadTab Ecosystem".format(USER_DOCUMENT_FOLDER)
DUMP_FOLDER = ECO_SYS_FOLDER + "\\Dump"

for _folder in [ECO_SYS_FOLDER, DUMP_FOLDER]:
    if not os.path.exists(_folder):
        try:
            os.makedirs(_folder)
        except Exception as e:
            print("Cannot secure folder [{}] becasue {}".format(_folder, e))

IS_OFFLINE_MODE = not os.path.exists(SHARED_DUMP_FOLDER)
if IS_OFFLINE_MODE:
    SHARED_DUMP_FOLDER = DUMP_FOLDER

ONE_DRIVE_ECOSYS_FOLDER = "{}\\OneDrive - Ennead Architects\\Documents\\EnneadTab Ecosystem".format(USER_PROFILE_FOLDER)
if os.path.exists(ONE_DRIVE_ECOSYS_FOLDER):
    import shutil
    try:
        shutil.rmtree(ONE_DRIVE_ECOSYS_FOLDER)
    except:
        pass


def cleanup_dump_folder():
    """Silently clean up files in DUMP_FOLDER older than 3 days, excluding .json and .sexyDuck files"""
    import os
    import time

    cutoff_time = time.time() - (3 * 24 * 60 * 60)  # 3 days
    protected_extensions = {'.json', '.sexyDuck', ".txt", ".lock", ".rui"}

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


cleanup_dump_folder()

def is_avd():
    """Check if current environment is an Azure Virtual Desktop.

    Returns:
        bool: True if current environment is AVD.
    """
    try:
        import clr  # pyright:ignore

        clr.AddReference("System")
        from System.Net import Dns  # pyright:ignore

        computer_name = Dns.GetHostName()
    except:
        import socket

        computer_name = socket.gethostname()
  
    return "avd" in computer_name.lower() or "gpupd" in computer_name.lower()


def is_Rhino_8():
    """Check if current environment is Rhino 8.

    Returns:
        bool: True if current environment is Rhino 8.
    """

    return str(get_rhino_version()) == "8"

def is_Rhino_7():
    """Check if current environment is Rhino 7.

    Returns:
        bool: True if current environment is Rhino 7.
    """

    return str(get_rhino_version()) == "7"

def get_rhino_version(main_version_only=True):
    """Get Rhino version.

    Returns:
        str: Rhino version.
    """
    if not IS_RHINO_ENVIRONMENT:
        return None
    import Rhino  # pyright: ignore

    return Rhino.RhinoApp.ExeVersion  if main_version_only else Rhino.RhinoApp.Version

def is_Rhino_environment():
    """Check if the current environment is Rhino.

    Returns:
        bool: True if current environment is Rhino.
    """
    try:
        import rhinoscriptsyntax  # pyright: ignore

        return True
    except:
        return False


def is_Grasshopper_environment():
    """Check if current environment is Grasshopper.

    Returns:
        bool: True if current environment is Grasshopper.
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
    """Get the current application name.

    Returns:
        str: The current application name.
    """
    app_name = "terminal"
    if IS_REVIT_ENVIRONMENT:
        app_name = "revit"
    elif IS_RHINO_ENVIRONMENT:
        app_name = "rhino"
    return app_name


if not os.path.exists(L_DRIVE_HOST_FOLDER):
    print ("L drive is not available, please check your network connection")
    try:
        import NOTIFICATION
        NOTIFICATION.messenger(main_text = "L drive is not available, please check your network connection")
    except:
        pass

###############
if __name__ == "__main__":
    unit_test()
