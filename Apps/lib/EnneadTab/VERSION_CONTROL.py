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
import datetime
import EXE
import ENVIRONMENT
import NOTIFICATION
import DATA_FILE
import USER


def timestamp_string_to_unix(timestamp_str):
    """
    Converts timestamp string format "YYYY-MM-DD_HH-MM-SS" to Unix timestamp
    
    Args:
        timestamp_str (str): Timestamp in format "2025-06-09_13-10-14"
        
    Returns:
        float: Unix timestamp
    """
    try:
        # Parse the timestamp string format "YYYY-MM-DD_HH-MM-SS"
        dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        return time.mktime(dt.timetuple())
    except (ValueError, TypeError):
        return None


def update_dist_repo():
    """Updates the distribution repository if sufficient time has passed since last update"""
    if not is_update_too_soon():
        EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)

        DATA_FILE.set_data({"last_update_time":time.time()}, "last_update_time")

        alert_user_to_update()
        



def is_update_too_soon():
    """
    Checks if the last update was too recent (within 60 minutes)
    
    Returns:
        bool: True if last update was within 60 minutes
    """
    data = DATA_FILE.get_data("last_update_time")
    recent_update_time = data.get("last_update_time", None)
    if not recent_update_time:
        return False
    return (time.time() - recent_update_time) < 3600


def alert_user_to_update():
    last_update_timestamp_str = get_last_update_time()
    if last_update_timestamp_str is None:
        return
    
    last_update_unix = timestamp_string_to_unix(last_update_timestamp_str)
    if last_update_unix is None:
        return
        
    time_since_last_update = time.time() - last_update_unix
    if time_since_last_update > 2592000.0:  # 30 days in seconds (30 * 24 * 60 * 60)
        NOTIFICATION.messenger("You have not updated EnneadTab for a long time. Please update it. Duck eggs have been hatched")
        return


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
