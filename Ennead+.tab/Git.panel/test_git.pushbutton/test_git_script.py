#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "test_git"

import os
# from pyrevit import forms #
from pyrevit import script #
import traceback
from pyrevit.coreutils import git 
import ENNEAD_LOG
import EnneadTab
# from Autodesk.Revit import DB # fastest DB
# # from Autodesk.Revit import UI
# doc = __revit__.ActiveUIDocument.Document

USERNAME = "zsenarchitect"
PASSWORD = "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"
REPO_URL = "https://github.com/Ennead-Architects-LLP/EnneadTab-for-Revit.git"
# REPO_URL = "https://github.com/zsenarchitect/MyWorkOutTrainer.git"
REPO_DIR = "{}\\EnneadTab-for-Revit".format(EnneadTab.ENVIRONMENT.ECOSYSTEM_FOLDER)
# REPO_DIR = "{}\\MyWorkOutTrainer".format(EnneadTab.ENVIRONMENT.ECOSYSTEM_FOLDER)
# print (REPO_DIR)
# print (type(REPO_DIR))
# from LibGit2Sharp import FilePath

# REPO_DIR = FilePath(REPO_DIR)
# print (REPO_DIR)
# print (type(REPO_DIR))

def clone():
    git.git_clone(REPO_URL, REPO_DIR, username=USERNAME, password=PASSWORD)
    return
    try:
        git.git_clone(REPO_URL, REPO_DIR, username=USERNAME, password=PASSWORD)
    except git.PyRevitGitAuthenticationError:
        print (traceback.format_exc())
        return
    
@EnneadTab.ERROR_HANDLE.try_catch_error
def test_git():
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)
        clone()
    
    # if the folder is empty
    if not os.listdir(REPO_DIR):
        print ("folder is empty")
        
        clone()
        
    # if the folder is empty
    if not os.listdir(REPO_DIR):
        print ("folder is still empty, give up")
        return
        
        
        
    try:
        current_local_repo = git.get_repo(REPO_DIR)
        # print type(current_local_repo)
        # for i,x in enumerate(dir(current_local_repo)):
        #     print ("--{}\n{}: {}".format(i,x, getattr(current_local_repo, x)))
        current_local_repo.password = PASSWORD
        current_local_repo.username = USERNAME
        git.git_fetch(current_local_repo)
        diff = git.compare_branch_heads(current_local_repo)
        # print ("Your branch is behind by {} commits.".format(diff.BehindBy))
        # print ("Your branch is ahead by {} commits.".format(diff.AheadBy))
        # print ("getting all commits:{}".format(git.get_all_new_commits(current_local_repo)))
    except:
        
        print (traceback.format_exc())
        return
    
    if diff.BehindBy > 0:
        print ("pulling...")
        git.git_pull(current_local_repo)
        
    print ("done")
    
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    test_git()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)




