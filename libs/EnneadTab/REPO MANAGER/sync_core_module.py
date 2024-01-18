
import os
parent_folder = os.path.dirname(os.path.dirname(__file__))

import sys
sys.path.append(parent_folder)


import threading
import time
import ENVIRONMENT
import NOTIFICATION
import FOLDER
import TIME
import TEXT


def main():
    """try to set auto schedule run on the module compare
    to catch all the module"""
    
    CoreMoudleMonitorTimer().start()




class CoreMoudleMonitorTimer():
    def __init__(self):
        self.stop_flag = False
        self.starting_time = time.time()
    
    def start(self): 
        # using threading to run check_repo, run every 5seconds for 1mins or until canceled.
        self.timer = threading.Timer(5, self.func)
        self.timer.start()

    
    def func(self):
        
        if time.time() - self.starting_time > 60 * 0.3:
            self.stop_flag = True
            return
        check_repo()
        if not self.stop_flag:
            self.timer = threading.Timer(10, self.func)
            self.timer.start()
        else:
            self.timer.cancel()
        
            NOTIFICATION.messenger (main_text = "Monitor terminated.")
            print (TEXT.colored_text("\n\nMonitor terminated.", TEXT.TextColor.Red))


def check_repo():
    rhino_repo_folder = ENVIRONMENT.WORKING_FOLDER_FOR_RHINO
    revit_repo_folder = ENVIRONMENT.WORKING_FOLDER_FOR_REVIT


    # generate dict---> key = path, value = last modified date
    # compare two dicts, get the intersection of key that exsit on both dict, 
    # if a key exist in both, see which value is older. User newer version to override, old version.(not yet actualkly override, just use print to say going to override.)
    rhino_data = folder_map(rhino_repo_folder)
    revit_data = folder_map(revit_repo_folder)
    shared_keys = set(rhino_data.keys()).intersection(set(revit_data.keys()))
    shared_keys = [key for key in shared_keys if not content_same(rhino_data[key], revit_data[key])]
    unique_keys_rhino = set(rhino_data.keys()).difference(set(revit_data.keys())) 
    unique_keys_revit = set(revit_data.keys()).difference(set(rhino_data.keys())) 
    
    def handle_unique_keys(unique_keys, rhino_or_revit):
        if len(unique_keys) == 0:
            return
        note = "\n\ntime = {}\n{} unique files found in {} repo.".format(TIME.get_formatted_current_time(), len(unique_keys), rhino_or_revit)
        print (TEXT.colored_text(note, TEXT.TextColor.Blue))
        for i, key in enumerate(unique_keys):
            print ("\n")
            print ("----{}: {}".format(i, TEXT.colored_text(key, TEXT.TextColor.Red)))
            if rhino_or_revit == "rhino":
                # print ("{}".format(rhino_data[key]))
                rhino_file  = rhino_data[key]
                revit_file = "{}\{}".format(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_REVIT, key)
                # print ("{}".format(revit_file))
                FOLDER.copy_file(rhino_file, revit_file)
                NOTIFICATION.messenger (main_text = "Copying <{}>\nrhino repo--->revit repo".format(key))
            else:
                revit_file = revit_data[key]
                rhino_file = "{}\{}".format(ENVIRONMENT.CORE_MODULE_FOLDER_FOR_RHINO, key)
                FOLDER.copy_file(revit_file, rhino_file)
                NOTIFICATION.messenger (main_text = "Copying <{}>\nrevit repo--->rhino repo".format(key))
    
    if len(unique_keys_rhino) != 0:
        print ("\n\ntime = {}\n{} unique files found in rhino repo.".format(TIME.get_formatted_current_time(), len(unique_keys_rhino)))
        handle_unique_keys(unique_keys_rhino, "rhino")
        
    if len(unique_keys_revit) != 0:
        print ("\n\ntime = {}\n{} unique files found in revit repo.".format(TIME.get_formatted_current_time(), len(unique_keys_revit)))
        handle_unique_keys(unique_keys_revit, "revit")
    
    if len(shared_keys) == 0:
        print ("\n\ntime = {}\nEverything is good. All Core modules synced.".format(TIME.get_formatted_current_time()))
        NOTIFICATION.messenger (main_text = "Everything is good. All Core modules synced.")
        return
    
    note = "\n\ntime = {}\nSome files need to sync up.".format(TIME.get_formatted_current_time())
    print (TEXT.colored_text(note, TEXT.TextColor.Blue))
    for i, key in enumerate(shared_keys):
        print ("\n")
        print ("----{}: {}".format(i, TEXT.colored_text(key, TEXT.TextColor.Red)))
        rhino_file = rhino_data[key]
        revit_file = revit_data[key]
        if os.path.getmtime(rhino_file) > os.path.getmtime(revit_file):
            print(TEXT.colored_text("    Rhino version is newer", TEXT.TextColor.Magenta))
            FOLDER.copy_file(rhino_file, revit_file)
            NOTIFICATION.messenger (main_text = "Copying <{}>\nrhino repo--->revit repo".format(key))
        else:
            print(TEXT.colored_text("    Revit version is newer", TEXT.TextColor.Cyan))
            FOLDER.copy_file(revit_file, rhino_file)
            NOTIFICATION.messenger (main_text = "Copying <{}>\nrevit repo--->rhino repo".format(key))
            
    # NOTIFICATION.messenger (main_text = "Please check version comparision.")


def content_same(file1, file2):
    try:
        with open(file1, "r") as f1:
            with open(file2, "r") as f2:
                return f1.read() == f2.read()
    except:
        
        return True

def folder_map(folder):
    data = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".pyc"):
                continue
            
            path = os.path.join(root, file)
            # path = path.split("EnneadTab")[1]
            try:
                file_local = path.split("EnneadTab\\")[1]
                data[file_local] = path
            except:
                pass
                # print ("skip <{}>".format(path))
            


    return data

if __name__ == "__main__":
    main()