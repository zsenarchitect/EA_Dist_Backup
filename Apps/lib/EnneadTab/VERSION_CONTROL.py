#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
import io
import time
import EXE
import ENVIRONMENT
import NOTIFICATION
import DATA_FILE

import random

def update_EA_dist():
    if not is_update_too_soon():
        EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)
        DATA_FILE.set_data({"last_update_time":time.time()}, "last_update_time.sexyDuck")



    if random.random() < 0.05:
        EXE.try_open_app("AccAutoRestarter", safe_open=True)

    if random.random() < 0.5:
        EXE.try_open_app("RegisterAutoStartup", safe_open=True)

def is_update_too_soon():
    """sample time 2025-01-22_09-59-59,convert to timestamp, if it is within 3mins, return True"""
    data = DATA_FILE.get_data("last_update_time.sexyDuck")
    recent_update_time = data.get("last_update_time", None)
    if not recent_update_time:
        return False
    if time.time() - recent_update_time < 60.0:
        return True
    return False

def get_last_update_time(return_file=False):
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) if file.endswith(".duck") and not "_ERROR" in file]
    if len(records) == 0:
        return None
    records.sort()
    record_file = records[-1]
    if return_file:
        return record_file
    return record_file.replace(".duck", "")

def show_last_success_update_time():
    record_file = get_last_update_time(return_file= True)
    if not record_file:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    
    try:
        if sys.platform == "cli":  # IronPython
            from System.IO import File
            # Read all lines and get the last one
            all_lines = File.ReadAllLines(os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record_file))
            commit_line = all_lines[-1].replace("\n", "")
        else:  # CPython
            with io.open(os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record_file), "r", encoding="utf-8") as f:
                commit_line = f.readlines()[-1].replace("\n","")
                
        NOTIFICATION.messenger("Most recent update at:{}\n{}".format(record_file.replace(".duck", ""),
                                                                    commit_line))
    except Exception as e:
        print("Error reading update record: {}".format(str(e)))
        NOTIFICATION.messenger("Error reading update record.")



def unit_test():
    update_EA_dist()



if __name__ == "__main__":
    update_EA_dist()
