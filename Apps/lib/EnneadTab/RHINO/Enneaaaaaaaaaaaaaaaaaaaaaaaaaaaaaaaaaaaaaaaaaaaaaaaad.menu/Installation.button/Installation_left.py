
__title__ = "Install EnneadTab"
__doc__ = "Install EnneadTab"
__FONDATION__ = True

import os
import sys

# this is needed becasue the first ever search need to be robust.
def find_main_repo():
    print ("Looking for EnneadTab OS...")
    for root, dirs, files in os.walk(os.environ['USERPROFILE']):
        if 'EnneadTab-OS' in dirs:
            return os.path.join(root, 'EnneadTab-OS')
    ESOSYSTEM_FOLDER = "{}\\Documents\\EnneadTab Ecosystem".format(os.environ["USERPROFILE"])
    return os.path.join(ESOSYSTEM_FOLDER, 'EA_Dist')

repo = find_main_repo()
sys.path.append(repo)

from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT
try:
    import rhinoscriptsyntax as rs
except ModuleNotFoundError:
    pass

import sys
sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left # pyright:ignore

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def Installation():
    get_latest_left.get_latest(is_silient = False)


    rs.MessageBox("Please remember to restart your Rhino now.")
