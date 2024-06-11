#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "TO BE CONTINUED, setting up tester branch and nromal user branch."
__title__ = "Proj. Tab Setting\nJoin Beta Group"
__context__ = "zero-doc"
# from pyrevit import forms #
from pyrevit import script #

import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
from pyrevit.userconfig import user_config
from pyrevit.loader.sessionmgr import execute_command #pylint: disable=import-outside-toplevel

try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass

def run():
    EnneadTab.USER.set_revit_beta_tester(is_tester = True)
    import imp
    ref_module = imp.load_source("EnneadTab_Setting_UI_script", r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\EnneadTab_Basic.tab\Resource.panel\EnneadTab_Setting_UI.pushbutton\EnneadTab_Setting_UI_script.py")




    print("\n\nWelcome to the new EnneadTab for Revit.")
    try:
        og_pdf = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\bin\beta_tester_welcome.pdf"
        new_pdf = EnneadTab.FOLDER.copy_file_to_local_dump_folder(og_pdf)
        print(new_pdf)
        EnneadTab.EXE.open_file_in_default_application(new_pdf)
    except Exception as e:
        print (e)
        EnneadTab.EXE.open_file_in_default_application(og_pdf)



        
    ref_module.change_extension_folder(is_force_tester = True)
    return








    
    """Reads the user extension folders and updates the list"""
    current_external_folders = user_config.get_thirdparty_ext_root_dirs(include_default=False)
    print(current_external_folders)
    #﻿ ['C:\\Users\\szhang\\github\\EnneadTab-for-Revit']


    beta_version_extension_folder = filter(lambda x: "Published_Beta_Version"  in x, current_external_folders)
    stable_version_extension_folder = filter(lambda x: x not in beta_version_extension_folder, current_external_folders)
    print(beta_version_extension_folder)
    print(stable_version_extension_folder)

    return

    enneadtab_stable_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published"
    enneadtab_beta_tester_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version"

    if not is_beta_tester:
        return

    if is_beta_tester:
        if enneadtab_beta_tester_version_folder not in current_external_folders:
            current_external_folders.append(enneadtab_beta_tester_version_folder)
        if enneadtab_stable_version_folder in current_external_folders:
            current_external_folders.remove(enneadtab_beta_tester_version_folder)
    else:
        if enneadtab_beta_tester_version_folder  in current_external_folders:
            current_external_folders.remove(enneadtab_beta_tester_version_folder)
        if enneadtab_stable_version_folder not in current_external_folders:
            current_external_folders.append(enneadtab_beta_tester_version_folder)








    user_config.set_thirdparty_ext_root_dirs(current_external_folders)
    execute_command(pyrevitcore_globals.PYREVIT_CORE_RELOAD_COMMAND_NAME)


    return




    """ need to have consideration for other folder, this tool should only add/remove EA_Proj extension."""
    if isinstance(self.extfolders_lb.ItemsSource, list):
        user_config.set_thirdparty_ext_root_dirs(
            coreutils.filter_null_items(self.extfolders_lb.ItemsSource)
        )
    else:
        user_config.set_thirdparty_ext_root_dirs([])
    execute_command(pyrevitcore_globals.PYREVIT_CORE_RELOAD_COMMAND_NAME)


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    run()
