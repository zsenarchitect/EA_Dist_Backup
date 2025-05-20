#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
VERSION_CONTROL
--------------
Manages EnneadTab update operations and tracking.
Maintains compatibility with both IronPython 2.7 and CPython 3.
"""

import os
import sys
import io
import time
import EXE
import ENVIRONMENT
import NOTIFICATION
import DATA_FILE
import USER


def update_dist_repo():
    """Updates the distribution repository if sufficient time has passed since last update"""
    if not is_update_too_soon():
        if USER.IS_DEVELOPER:
            print ("DEV ONLY: Using new EnneadTab_OS_Installer untill all is fine for future release")
            EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)
        else:
            EXE.try_open_app("EnneadTab_OS_Installer_Backup", safe_open=True)
        DATA_FILE.set_data({"last_update_time":time.time()}, "last_update_time")
        



def is_update_too_soon():
    """
    Checks if the last update was too recent (within 21 minutes)
    
    Returns:
        bool: True if last update was within 21 minutes
    """
    data = DATA_FILE.get_data("last_update_time")
    recent_update_time = data.get("last_update_time", None)
    if not recent_update_time:
        return False
    return (time.time() - recent_update_time) < 1260.0


def get_last_update_time(return_file=False):
    """
    Retrieves the timestamp of the most recent successful update
    
    Args:
        return_file (bool): When True, returns filename instead of timestamp
        
    Returns:
        str or None: Update timestamp or filename, None if no records found
    """
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) 
              if file.endswith(".duck") and "_ERROR" not in file]
    if not records:
        return None
    records.sort()
    record_file = records[-1]
    if return_file:
        return record_file
    return record_file.replace(".duck", "")


def show_last_success_update_time():
    """Displays a notification with information about the most recent successful update"""
    record_file = get_last_update_time(return_file=True)
    if not record_file:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    
    try:
        file_path = os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record_file)
        if sys.platform == "cli":  # IronPython
            from System.IO import File
            all_lines = File.ReadAllLines(file_path)
            commit_line = all_lines[-1].replace("\n", "")
        else:  # CPython
            with io.open(file_path, "r", encoding="utf-8") as f:
                commit_line = f.readlines()[-1].replace("\n", "")
                
        update_time = record_file.replace(".duck", "")
        message = "Most recent update at: {}\n{}".format(update_time, commit_line)
        NOTIFICATION.messenger(message)
    except Exception as e:
        print("Error reading update record: {}".format(str(e)))
        NOTIFICATION.messenger("Error reading update record.")


def unit_test():
    """Run simple unit test of the module"""
    update_dist_repo()


if __name__ == "__main__":
    update_dist_repo()
