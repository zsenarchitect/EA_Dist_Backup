
__title__ = "ActivateEnneadTab"
__doc__ = "When things do not load, activate me."
__FONDATION__ = True

import os
import rhinoscriptsyntax as rs
import sys

def add_search_path():
    _app_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    lib_path = os.path.join(_app_folder, "lib" )
    rs.AddSearchPath(lib_path)
    sys.path.append(lib_path)
    sys.path = list(set(sys.path))

add_search_path()


from EnneadTab import NOTIFICATION


def activate_enneadtab():
    NOTIFICATION.messenger("EnneadTab Activated")

    
if __name__ == "__main__":
    activate_enneadtab()
