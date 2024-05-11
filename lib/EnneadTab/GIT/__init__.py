#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import subprocess
import time
import datetime


import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import EXE
import ENVIRONMENT
import NOTIFICATION
import DATA_FILE
import FOLDER

# from GIT_UPDATER import GIT_HOLDING_KEY #>>> if use from import, will cause ironpython to load py3 style module which is fail
GIT_HOLDING_KEY = "EnneadTab_git_working_is_busy"
############################################################################################################################
def run_updater(show_progress=False):
    # giving up for now, see front note at GIT_UPDATER


    return False

    version = 0.3
    exe_location = "{}\\GIT_UPDATER_{}\\GIT_UPDATER.exe".format(ENVIRONMENT.EXE_FOLDER, version)
    EXE.open_file_in_default_application(exe_location)
    os.environ[GIT_HOLDING_KEY] = "True"
    DATA_FILE.save_dict_to_json_in_dump_folder({}, "{}.json".format(GIT_HOLDING_KEY))
    max_count = 60
    count = 0
    while True:
        if show_progress:
            print ("Time until repo update giveup: {}s".format(max_count - count))
        time.sleep(1)
        count += 1
        if os.environ[GIT_HOLDING_KEY] == "False":
            NOTIFICATION.messenger(main_text="EnneadTab Ecosystem Updated")
            return True
        
        if not FOLDER.is_file_exist_in_dump_folder("{}.json".format(GIT_HOLDING_KEY)):
            NOTIFICATION.messenger(main_text="EnneadTab Ecosystem Updated")
            return True
        
        
        if count> max_count:
            return False
    
    

def unit_test():
    assert run_updater(show_progress=True)

############################################################################################
def get_nth_commit_number():
    # Count the number of commits made today
    result = subprocess.Popen(["git", "log", "--since=midnight", "--oneline"], stdout=subprocess.PIPE)
    commits = result.stdout.readlines()
    return len(commits) + 1


def push_changes_to_main(repository_path):
    """this is importatnt and should keep. It push the change of Distrubuter Folder to git repo"""

    # Change to the Git repository directory
    os.chdir(repository_path)

    # Stage all changes
    subprocess.call(["git", "add", "."])

    commit_number = get_nth_commit_number()

    # Commit with today's date
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    commit_message = "Auto push changes committed on {}...{}".format(current_date, commit_number)
    subprocess.call(["git", "commit", "-m", commit_message])

    # Push to the main branch
    subprocess.call(["git", "push", "origin", "main"])




####################################
def is_current_version_outdated():
    # depend on environment, check the current fetch date of revit repo, if older than the most recent available one, update git
    pass

###############################################
if __name__ == '__main__':
    
    run_updater()
    