"""Run apps from the EnneadTab app library.

This module provides functionality to safely execute applications from the EnneadTab library,
with support for legacy versions and temporary file handling.
"""

import os
import time
import ENVIRONMENT
import USER
import NOTIFICATION
import COPY

def try_open_app(exe_name, legacy_name = None, safe_open = False):
    """Attempt to open an executable file from the app library.
    
    Args:
        exe_name (str): Name of the executable file to open. Can include full path.
        legacy_name (str, optional): Name of legacy executable as fallback.
        safe_open (bool, optional): When True, creates a temporary copy before execution
            to allow for updates while the app is running.
    
    Returns:
        bool: True if application was successfully opened, False otherwise.
    
    Note:
        Safe mode creates temporary copies in the system temp folder with automatic cleanup:
        - OS_Installer/AutoStartup files: cleaned up after 12 hours
        - Other executables: cleaned up after 24 hours
    """

    # Handle non-executable files directly
    abs_name = exe_name.lower()
    if abs_name.endswith((".3dm", ".xlsx", ".xls", ".pdf", ".png", ".jpg")):
        try:
            os.startfile(exe_name)
            return True
        except OSError:
            if USER.IS_DEVELOPER:
                NOTIFICATION.messenger("Failed to open file: {}".format(exe_name))
            return False
    


    exe_name = exe_name.replace(".exe", "")
    exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{}.exe".format(exe_name)



    if safe_open:
        # if not os.path.exists(exe):
        #     raise Exception("Only work for standalone exe, not for foldered exe.[{}] not exist".format(exe))
        temp_exe_name = "_temp_exe_{}_{}.exe".format(exe_name, int(time.time()))
        temp_exe = ENVIRONMENT.WINDOW_TEMP_FOLDER + "\\" + temp_exe_name
        # print (temp_exe)
        COPY.copyfile(exe, temp_exe)
        if os.path.exists(temp_exe):
            os.startfile(temp_exe)
        else:
            print ("temp exe not found, maybe failed to copy due to permission issue.")
        clean_temporary_executables()
        return True
        
    
        
    if os.path.exists(exe):
        os.startfile(exe)
        return True
    foldered_exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{0}\\{0}.exe".format(exe_name)
    if os.path.exists(foldered_exe):
        os.startfile(foldered_exe)
        return True
    
    if legacy_name:
        if try_open_app(legacy_name):
            return True
        
    if USER.IS_DEVELOPER:
        print ("[Developer only log]No exe found in the location.")
        print (exe)
        print (foldered_exe)
        NOTIFICATION.messenger("No exe found!!!\n{}\n Will try to open legacy app.".format(exe_name))

    if try_open_legacy_app(exe_name):
        return True
    NOTIFICATION.messenger("No legacy app found!!!\n{}".format(exe_name))
    return False

def try_open_legacy_app(exe_name):
    head = os.path.join(ENVIRONMENT.L_DRIVE_HOST_FOLDER, "01_Revit", "04_Tools", "08_EA Extensions", "Project Settings", "Exe")
    if os.path.exists(os.path.join(head, exe_name + ".exe")):
        os.startfile(os.path.join(head, exe_name + ".exe"))
        return True
    if os.path.exists(os.path.join(head, exe_name, exe_name + ".exe")):
        os.startfile(os.path.join(head, exe_name, exe_name + ".exe"))
        return True
    return False


def clean_temporary_executables():
    def get_ignore_age(file):
        if "OS_Installer" in file or "AutoStartup" in file:
            return 60*60*12
        return 60*60*24
    for file in os.listdir(ENVIRONMENT.WINDOW_TEMP_FOLDER):
        if file.startswith("_temp_exe_"):
            # ignore if this temp file is less than 1 day old, unless it is OS_installer or AutoStartup
            if time.time() - os.path.getmtime(os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, file)) < get_ignore_age(file):
                continue
            try:
                os.remove(os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, file))
            except:
                pass