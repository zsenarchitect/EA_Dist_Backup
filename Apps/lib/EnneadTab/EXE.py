"""Run apps from the EnneadTab app library."""

import os
import time
import ENVIRONMENT
import USER
import NOTIFICATION
import COPY

def try_open_app(exe_name, legacy_name = None, safe_open = False):
    """Attempt to open an exe file from the app libary.
    
    Args:
        exe_name (str): The name of the exe file to open.
        legacy_name (str): The name of the legacy exe file to open (optional).
        safe_open (bool): Whether to open the exe file using safe mode.
    
    Note:
        When using safe open, a temporary copy of the exe file will be created in the dump folder.
        This is to address the issue that the exe file cannot be updated while it is being used.
        The temporary copy will be purged after a certain period of time.   
    """ 

    abs_name = exe_name.lower()
    if abs_name.endswith((".3dm", ".xlsx", ".xls", ".pdf", ".png", ".jpg")):
        os.startfile(exe_name)
        return True
    


    exe_name = exe_name.replace(".exe", "")
    exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{}.exe".format(exe_name)


    def get_ignore_age(file):
        if "OS_Installer" in file or "AutoStartup" in file:
            return 60*60*2
        return 60*60*24
    if safe_open:
        if not os.path.exists(exe):
            raise Exception("Only work for stanfle along exe, not for foldered exe.[{}] not exist".format(exe))
        temp_exe_name = "_temp_exe_{}_{}.exe".format(exe_name, int(time.time()))
        temp_exe = ENVIRONMENT.WINDOW_TEMP_FOLDER + "\\" + temp_exe_name
        # print (temp_exe)
        COPY.copyfile(exe, temp_exe)
        os.startfile(temp_exe)
        for file in os.listdir(ENVIRONMENT.WINDOW_TEMP_FOLDER):
            if file.startswith("_temp_exe_"):
                # ignore if this temp file is less than 1 day old, unless it is OS_installer or AutoStartup
                if time.time() - os.path.getmtime(os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, file)) < get_ignore_age(file):
                    continue
                try:
                    os.remove(os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, file))
                except:
                    pass
        return True
        
    
        
    if os.path.exists(exe):
        os.startfile(exe)
        return True
    foldered_exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{0}\\{0}.exe".format(exe_name)
    if os.path.exists(foldered_exe):
        os.startfile(foldered_exe)
        return True
    
    if legacy_name:
        if try_open_app(legacy_name):
            return True
        
    if USER.IS_DEVELOPER:
        print ("[Developer only log]No exe found in the location.")
        print (exe)
        print (foldered_exe)
        NOTIFICATION.messenger("No exe found!!!\n{}".format(exe_name))
    return False


