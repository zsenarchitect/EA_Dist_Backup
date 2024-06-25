import sys
import EnneadTab
from EnneadTab.ERROR_HANDLE import try_catch_error
import EnneadTab.ENVIRONMENT_CONSTANTS as ENVIRONMENT_CONSTANTS
import rhinoscriptsyntax as rs

GITHUB_FOLDER = ENVIRONMENT_CONSTANTS.GITHUB_FOLDER
WORKING_FOLDER_FOR_RHINO = r"{}\EnneadTab-for-Rhino".format(GITHUB_FOLDER)
sys.path.append(r'{}\Source Codes\lib'.format(WORKING_FOLDER_FOR_RHINO))

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():


    EnneadTab.VERSION_CONTROL.publish_ENNEAD_module()

    print("done")



if  __name__ == "__main__" :

    main()
