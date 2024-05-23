import os

import sys

sys.path.append("..\lib")
import EnneadTab
import subprocess

@EnneadTab.ERROR_HANDLE.try_catch_error
def china_code_ref():
    folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\Codes"
    files = EnneadTab.FOLDER.get_filenames_in_folder(folder)
    special_folder = "#PDF in this directory are reference only"
    files.remove(special_folder)
    """
    for file in files:
        print(file)
    """
    keyword = "<Open Entire Code Folder...>"
    files.insert(0, keyword)
    #print dir(EnneadTab)
    #print dir(EnneadTab.RHINO)
    #print dir(EnneadTab.RHINO.RHINO_FORMS)
    selected_opt = EnneadTab.RHINO.RHINO_FORMS.select_from_list(files, multi_select = False, message = "WHAT THE CODE IS GOING ON?????")

    if not selected_opt:
        return


    if keyword == selected_opt:

        path = r"file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\DD Documentation Samples\#PDF in this directory are reference only"
        subprocess.Popen(r'explorer /select, {}'.format(path))
        return

    filepath = folder + "\\" + selected_opt
    EnneadTab.EXE.open_file_in_default_application(filepath)
###################################################################
if __name__ == "__main__":
    china_code_ref()
