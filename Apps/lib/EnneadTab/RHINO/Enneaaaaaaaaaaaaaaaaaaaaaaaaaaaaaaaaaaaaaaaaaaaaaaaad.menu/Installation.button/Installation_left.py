


__title__ = "Install EnneadTab"
__doc__ = "Install EnneadTab"
__FONDATION__ = True

import sys
import os

# this is needed becasue the first ever search need to be robust.
def find_main_repo():
    print ("Looking for EnneadTab OS...")
    user_profile_folder = os.environ['USERPROFILE']
    common_locations = [
        "github",
        "duck-repo",
        "design-repo"
        ]
    for location in common_locations:
        if os.path.exists(os.path.join(user_profile_folder, location)):
            return os.path.join(user_profile_folder, location, 'EnneadTab-OS')

    esosys_folder = "{}\\Documents\\EnneadTab Ecosystem".format(os.environ["USERPROFILE"])
    return os.path.join(esosys_folder, 'EA_Dist')

_repo = find_main_repo()
print ("EnneadTab OS at {}".format(_repo))
_lib = os.path.join(_repo,"Apps","lib")
sys.path.append(_lib)

from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT
try:
    import rhinoscriptsyntax as rs
    rs.AddSearchPath(_lib)
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
