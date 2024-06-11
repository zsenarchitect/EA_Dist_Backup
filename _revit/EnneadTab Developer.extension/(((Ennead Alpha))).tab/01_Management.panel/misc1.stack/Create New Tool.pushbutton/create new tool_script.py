#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make a new button in EnneadTab. What would I do without you."
__title__ = "Create New\nTool Button"
__context__ = "zero-doc"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import sys
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
from pyrevit.loader import sessionmgr

def create_new_button():
    # get new button name
    func_name = forms.ask_for_string(default = "New_Button_Name", prompt = "Type in the name for new script, seperated by '_'")

    # pick folder location
    #file_address = forms.save_file(file_ext = '.py', files_filter = '', init_dir = '', default_name = '', restore_dir = True, unc_paths = False, title = None)
    folder = forms.pick_folder(title = "New script location of container pushbutton", owner = None)#not sure what is owner

    #print folder
    target_folder = "{}\{}.pushbutton".format(folder, func_name)
    new_location = "{}\{}_script.py".format(target_folder, func_name)
    #print new_location

    # copy from template to address
    # secure folder first
    EA_UTILITY.secure_folder(target_folder)

    source_folder = r"C:\Users\szhang\github\EnneadTab-for-Revit\EnneadTab Developer.extension\(((Ennead Alpha))).tab\00_Template.panel\###New Tool Template.pushbutton"
    files_in_source = EA_UTILITY.get_filenames_in_folder(source_folder)
    for file in files_in_source:
        print(file)
        EA_UTILITY.copy_file_to_folder("{}\{}".format(source_folder, file), target_folder)
        if "_script" in file:
            search_file = file
            new_file_name = file.replace("template", func_name)
            EA_UTILITY.rename_file_in_folder(search_file, new_file_name, target_folder)


    # edit main func name
    with open(new_location) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:

        line = line.replace('__title__ = "Template Button"', '__title__ = "{}"'.format(func_name))
        line = line.replace('run()', '{}()'.format(func_name))
        new_lines.append(line)

    with open(new_location, "w") as f:
        f.write("".join(new_lines))

    #open lib on the side
    utility_file = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib\EA_UTILITY.py"
    EA_UTILITY.open_file_in_default_application(utility_file)
    EA_UTILITY.open_file_in_default_application(new_location)

    sessionmgr.reload_pyrevit()

    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    create_new_button()
