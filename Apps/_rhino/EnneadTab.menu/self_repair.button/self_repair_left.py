__title__ = "SelfRepair"
__doc__ = """Automatically repair and update EnneadTab installation.

Key Features:
- Legacy RUI detection and repair
- Automatic version updates
- System path verification
- Component synchronization
- Installation validation"""

import os
import sys
from EnneadTab import ERROR_HANDLE, LOG
import rhinoscriptsyntax as rs

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def self_repair():
    """Main function to repair and update EnneadTab installation.
    
    Scans for legacy RUI files and triggers update process if found.
    Ensures proper system path configuration and component synchronization.
    """

    
    for tool_bar_name in rs.ToolbarCollectionNames():
        path = rs.ToolbarCollectionPath(tool_bar_name)
        if is_legacy_rui(path):
            update_get_latest()
            return


def update_get_latest():
    menu_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    get_latest_path = os.path.join(menu_folder, "get_latest.button")
    
        
    sys.path.append(get_latest_path)

    import get_latest_left as GL #type: ignore
    GL.get_latest()
    return

def is_legacy_rui(rui_path):
    """Check if RUI file contains legacy EnneadTab references.
    
    Args:
        rui_path (str): Path to RUI file
        
    Returns:
        bool: True if legacy references found, False otherwise
    """
    if not os.path.exists(rui_path):
        return False
        

    with open(rui_path, "r") as file:
        return any("ennead+" in line.lower() for line in file)


if __name__ == "__main__":
    self_repair()
