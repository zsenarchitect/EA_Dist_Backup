import os
import sys
import time
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore




def add_search_path():
    # for path in rs.SearchPathList():
    #     if 'EnneadTab-OS' in path:
    #         rs.DeleteSearchPath(path)
    _app_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    lib_path = os.path.join(_app_folder, "lib" )
    rs.AddSearchPath(lib_path)
    sys.path.append(lib_path)
    sys.path = list(set(sys.path))
    
      
time_start = time.time()
add_search_path()
# print ("Get Latest use {:.2}s".format(time.time() - time_start))
print ("\n".join(sys.path))




__title__ = "GetLatest"
__doc__ = "Get the lastest version of EnneadTab"
__FONDATION__ = True
from EnneadTab import ERROR_HANDLE
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI, RHINO_ALIAS


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()
    RHINO_RUI.update_my_rui()
    RHINO_ALIAS.register_alias_set()
    RHINO_RUI.add_startup_script()


    if not is_silient:
        NOTIFICATION.messenger("Latest EnneadTab-For-Rhino Loaded")
    else:
        print ("Latest EnneadTab-For-Rhino Loaded")



 



if __name__ == "__main__":
    get_latest()