__tooltip__ = "See other code related pdf."
__context__ = "zero-doc"
__title__ = "Building Codes"
import os


from pyrevit import forms
import EA_UTILITY
import EnneadTab
import subprocess

def open_code():
    folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\Codes"
    files = EA_UTILITY.get_filenames_in_folder(folder)
    special_folder = "#PDF in this directory are reference only"
    files.remove(special_folder)
    """
    for file in files:
        print file
    """
    keyword = "<Open Entire Code Folder...>"
    files.insert(0, keyword)
    selected_opt = forms.SelectFromList.show(files, multiselect = False, title = "WHAT THE CODE IS GOING ON?????")
    if not selected_opt:
        return


    if keyword == selected_opt:

        path = r"file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Library Docs\DD Documentation Samples\#PDF in this directory are reference only"
        subprocess.Popen(r'explorer /select, {}'.format(path))
        return

    filepath = folder + "\\" + selected_opt
    EA_UTILITY.open_file_in_default_application(filepath)
###################################################################

open_code()
