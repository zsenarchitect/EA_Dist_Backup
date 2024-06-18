#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Just download latest version without reload. Great if there are no layout changes."
__title__ = "Soft Reload"
__context__ = "zero-doc"
# from pyrevit import forms #
from pyrevit import script

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, VERSION_CONTROL, WEB, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB  # pyright: ignore
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
import os
import shutil
import time
import traceback
import threading

"""until IT fix the firewall issue about baked exe, this is a temp solution."""

class RepositoryUpdater:
    def __init__(self, repo_url, extract_to):
        self.repo_url = repo_url
        self.extract_to = os.path.expanduser(extract_to)

        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
            
        self.final_folder_name = self.extract_repo_name(repo_url)
        self.final_dir = os.path.join(self.extract_to, self.final_folder_name)
    
    def extract_repo_name(self, url):
        if '/archive/' in url:
            parts = url.split('/')
            repo_index = parts.index('archive') - 1
            return parts[repo_index]
        return "Repository"
    
    def run_update(self):
        print("Starting run_update")
        self.download_zip()
        self.extract_zip()
        self.update_files()
        try:
            self.cleanup()
        except:
            pass
        print("Completed run_update")
    
    def download_zip(self):
        print("Starting download_zip")
        zip_path = WEB.download_file_by_name(self.repo_url, self.extract_to, "repo.zip")
        self.zip_path = zip_path
        print("Zip file downloaded successfully.")
    
    def extract_zip(self):
        print("Starting extract_zip")
        self.temp_dir = os.path.join(self.extract_to, "temp_extract")
        WEB.unzip_file(self.zip_path, self.temp_dir)
        self.source_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])
        print("Zip file extracted.")
    
    def update_files(self):
        print("Starting update_files")
        if not os.path.exists(self.final_dir):
            os.makedirs(self.final_dir)
        
        # Force copy everything over
        source_files = {os.path.join(dp, f): os.path.relpath(os.path.join(dp, f), self.source_dir) for dp, dn, filenames in os.walk(self.source_dir) for f in filenames}
        for src_path, rel_path in source_files.items():
            tgt_path = os.path.join(self.final_dir, rel_path)
            if not os.path.exists(os.path.dirname(tgt_path)):
                os.makedirs(os.path.dirname(tgt_path))
            shutil.copy2(src_path, tgt_path)

        # Delete files older than 3 days
        now = time.time()
        three_days_ago = now - 3 * 24 * 60 * 60
        for dp, dn, filenames in os.walk(self.final_dir):
            for f in filenames:
                file_path = os.path.join(dp, f)
                if os.stat(file_path).st_mtime < three_days_ago:
                    os.remove(file_path)
                    try:
                        os.rmdir(dp)  # Attempt to remove the directory if empty
                    except OSError:
                        pass
        print("Files have been updated.")
    
    def cleanup(self):
        print("Starting cleanup")
        shutil.rmtree(self.temp_dir)
        WEB.remove_zip_file(self.zip_path)
        print("Cleanup completed.")

def save_traceback_and_open(user, error_message):
    error_path = os.path.expanduser("~/Desktop/GIT_CLONE_error.txt")  

    with open(error_path, 'w') as f:
        f.write(error_message)
    if user in ["szhang", "Sen Zhang"]:
        os.startfile(error_path)

def main_thread():
    print("Starting main")
    repo_url = "https://github.com/zsenarchitect/EA_Dist/archive/refs/heads/master.zip"
    extract_to = r"~\Documents\EnneadTab Ecosystem"
    updater = RepositoryUpdater(repo_url, extract_to)
    updater.run_update()
    print("Completed main")




@ERROR_HANDLE.try_catch_error
def soft_reload():

    VERSION_CONTROL.update_EA_dist()

    start = time.time()
    main_thread()
    print("Finish everything in {}s".format(int(time.time() - start)))
    return

    print("Starting main_thread")
    thread = threading.Thread(target=main_thread)
    thread.start()
    thread.join(1)  # Wait for a second to ensure the thread starts
    print("main_thread is alive:", thread.is_alive())

################## main code below #####################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    soft_reload()
    ENNEAD_LOG.use_enneadtab(coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)
