import os

parent_folder = os.path.dirname(os.path.dirname(__file__))

import sys
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


def publishing_GH_python():
    GH_python_folder = "{}\\Source Codes\\Grasshopper\\GH_python".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
    target_folder = "{}\\Source Codes\\Grasshopper\\GH_python".format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    EnneadTab.FOLDER.copy_dir(GH_python_folder, target_folder)

    EnneadTab.NOTIFICATION.messenger(main_text = "GH python published.")

########################
if __name__ == "__main__":
    publishing_GH_python()
