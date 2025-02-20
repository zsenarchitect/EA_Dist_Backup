__title__ = "ActivateEnneadTab"
__doc__ = """Restore EnneadTab functionality.

Key Features:
- System path verification
- Component activation
- Path configuration
- Startup script setup
- Error recovery"""
__FONDATION__ = True

import os
import rhinoscriptsyntax as rs
import sys

try:
    import EnneadTab
    is_tab_loaded_originally = True
except:
    is_tab_loaded_originally = False


def add_search_path():
    _app_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    lib_path = os.path.join(_app_folder, "lib" )
    rs.AddSearchPath(lib_path)
    sys.path.append(lib_path)
    sys.path = list(set(sys.path))

if not is_tab_loaded_originally:
    add_search_path()

def activate_enneadtab():
    if not is_tab_loaded_originally:
        from EnneadTab import NOTIFICATION
        NOTIFICATION.messenger("EnneadTab Activated")
        from EnneadTab.RHINO import RHINO_RUI
        RHINO_RUI.add_startup_script()

    
if __name__ == "__main__":
    activate_enneadtab()
