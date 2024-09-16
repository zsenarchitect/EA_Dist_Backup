#!/usr/bin/python
# -*- coding: utf-8 -*-


import os

import EXE
import ENVIRONMENT
import NOTIFICATION




def update_EA_dist():
    EXE.try_open_app("EnneadTab_OS_Installer", safe_open=True)
    EXE.try_open_app("RegisterAutoStartup", safe_open=True)




def show_last_success_update_time():
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) if file.endswith(".duck") and not "_ERROR" in file]
    if len(records) == 0:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    records.sort()
    record = records[-1]
    with open(os.path.join(ENVIRONMENT.ECO_SYS_FOLDER, record)) as f:
        commit_line = f.readlines()[-1].replace("\n","")
    NOTIFICATION.messenger("Most recent update at:{}\n{}".format(record.replace(".duck", ""),
                                                                 commit_line))    
        
    pass

def unit_test():
    update_EA_dist()



if __name__ == "__main__":
    unit_test()
    show_last_success_update_time()