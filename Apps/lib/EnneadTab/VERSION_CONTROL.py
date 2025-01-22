#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys

import EXE
import ENVIRONMENT
import NOTIFICATION

import random
from datetime import datetime

def update_EA_dist():
    if not is_update_too_soon():
        EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)



    if random.random() < 0.05:
        EXE.try_open_app("RegisterAutoStartup", safe_open=True)
        EXE.try_open_app("AccAutoRestarter", safe_open=True)


def is_update_too_soon():
    """sample time 2025-01-22_09-59-59,convert to timestamp, if it is within 3mins, return True"""
    recent_update_time = get_last_update_time()
    if not recent_update_time:
        return False
    recent_update_time = datetime.strptime(recent_update_time, "%Y-%m-%d_%H-%M-%S")
    if (datetime.now() - recent_update_time).total_seconds() < 3 * 60:
        return True
    return False

def get_last_update_time():
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) if file.endswith(".duck") and not "_ERROR" in file]
    if len(records) == 0:
        return None
    records.sort()
    record = records[-1]
    return record

def show_last_success_update_time():
    record = get_last_update_time()
    if not record:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    
    try:
        if sys.platform == "cli":  # IronPython
            from System.IO import File
            # Read all lines and get the last one
            all_lines = File.ReadAllLines(os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record))
            commit_line = all_lines[-1].replace("\n", "")
        else:  # CPython
            with open(os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record)) as f:
                commit_line = f.readlines()[-1].replace("\n","")
                
        NOTIFICATION.messenger("Most recent update at:{}\n{}".format(record.replace(".duck", ""),
                                                                    commit_line))
    except Exception as e:
        print("Error reading update record: {}".format(str(e)))
        NOTIFICATION.messenger("Error reading update record.")



def unit_test():
    update_EA_dist()



if __name__ == "__main__":
    update_EA_dist()

    show_last_success_update_time()