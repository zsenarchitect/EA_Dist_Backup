#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys

import EXE
import ENVIRONMENT
import NOTIFICATION

import random


def update_EA_dist():
    EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)



    if random.random() < 0.05:
        EXE.try_open_app("RegisterAutoStartup", safe_open=True)
        EXE.try_open_app("AccAutoRestarter", safe_open=True)




def show_last_success_update_time():
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) if file.endswith(".duck") and not "_ERROR" in file]
    if len(records) == 0:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    records.sort()
    record = records[-1]
    
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