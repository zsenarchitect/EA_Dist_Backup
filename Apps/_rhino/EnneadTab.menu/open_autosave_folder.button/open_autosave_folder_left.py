
__title__ = "OpenAutosaveFolder"
__doc__ = "Open the Rhino autosave folder lcoations."

import os
from EnneadTab import ERROR_HANDLE, LOG
import subprocess
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_autosave_folder():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "McNeel", "Rhinoceros", "temp")
       

    subprocess.Popen(r'explorer /select, {}'.format(path))

    
if __name__ == "__main__":
    open_autosave_folder()
