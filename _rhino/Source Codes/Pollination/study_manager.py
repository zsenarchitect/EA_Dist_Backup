import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


@EnneadTab.ERROR_HANDLE.try_catch_error
def study_manager():
    rs.EnableRedraw(False)
    if EnneadTab.USER.is_SZ():
        note = """
        input looper to get every combonation,
        let it explore overnight and save all the version"""
        EnneadTab.NOTIFICATION.messenger(main_text = "manage output of study so can return and serialize back. Lagend maker? Make a counter part in GH python part to save data, mesh....export with legend and same camera on many study" + note)
    


######################  main code below   #########
if __name__ == "__main__":

    study_manager()




