#!/usr/bin/python
# -*- coding: utf-8 -*-
#import distutils

import os
import time
import shutil

import TIME
import FOLDER
import ENVIRONMENT_CONSTANTS
import NOTIFICATION
import SOUNDS
import ENVIRONMENT
import GIT
import EXE

def publish_ENNEAD_module():
    #working_root = ENVIRONMENT.get_EnneadTab_WORKING_root()
    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        _publish_ENNEAD_module_from_revit()
        return
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        _publish_ENNEAD_module_from_rhino()


def _publish_ENNEAD_module_from_revit():
    src = r"{}\ENNEAD.extension\lib\EnneadTab".format(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT)

    dst_rhino_working = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
    FOLDER.copy_dir(src, dst_rhino_working)

    #dst_revit_server = r"{}\ENNEAD.extension\lib\EnneadTab".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT)
    #FOLDER.copy_dir(src, dst_revit_server)

    #dst_rhino_server = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    #FOLDER.copy_dir(src, dst_rhino_server)

    print ("\n\nAll ennead Module updated from working Revit to Working Rhino")
    SOUNDS.play_sound("sound effect_mario fireball.wav")


def _push_core_module_from_rhino_repo_to_L_drive():
    src = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)

    dst_rhino_repo = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    FOLDER.copy_dir(src, dst_rhino_repo)
    
    print ("\n\nAll ennead Module updated from working Rhino to L Drive Rhino")
    SOUNDS.play_sound("sound effect_mario fireball.wav")

def _push_core_module_from_revit_repo_to_L_drive():
    src = ENVIRONMENT.CORE_MODULE_FOLDER_FOR_REVIT

    dst_revit_repo = ENVIRONMENT.CORE_MODULE_FOLDER_FOR_PUBLISHED_REVIT
    FOLDER.copy_dir(src, dst_revit_repo)
    dst_revit_repo = ENVIRONMENT.CORE_MODULE_FOLDER_FOR_PUBLISHED_BETA_REVIT
    FOLDER.copy_dir(src, dst_revit_repo)
    
    print ("\n\nAll ennead Module updated from working Revit to L Drive Revit")
    SOUNDS.play_sound("sound effect_mario fireball.wav")


def _publish_ENNEAD_module_from_rhino():
    src = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)

    dst_revit_working = r"{}\ENNEAD.extension\lib\EnneadTab".format(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT)
    FOLDER.copy_dir(src, dst_revit_working)

    #dst_revit_server = r"{}\ENNEAD.extension\lib\EnneadTab".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT)
    #FOLDER.copy_dir(src, dst_revit_server)

    #dst_rhino_server = r"{}\Source Codes\lib\EnneadTab".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    #FOLDER.copy_dir(src, dst_rhino_server)

    print ("\n\nAll ennead Module updated from working Rhino to WOrking Revit")
    SOUNDS.play_sound("sound effect_mario fireball.wav")


def _publish_Revit_source_code(publish_stable_version, publish_beta_version):
    allow_print_log = False
    src = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension"
    #dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\test folder_ennead_extension"
    stable_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension"
    beta_tester_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension"


    year, month, day = TIME.get_date_as_tuple()
    archive_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\_Archive\{}{}{}_ENNEAD.extension".format(year, month, day)
    SH_version_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_SH_VERSION\VERSION_{}_{}_{}\SH_ENNEAD.extension".format(year, month, day)
    #distutils.dir_util.copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, update=0, verbose=0, dry_run=0)


    
    if publish_beta_version:
    
        time_start = time.time()
        
        print ("Publishing beta version...")
        FOLDER.copy_dir(src, 
                        beta_tester_dst,
                        allow_print_log=allow_print_log)
        SOUNDS.play_sound("sound effect_mario fireball.wav")
        update_yaml(beta_tester_dst, disable_advanced=False, disable_SZ=True)
        used_time = time.time() - time_start
        used_time = TIME.get_readable_time(used_time)
        NOTIFICATION.duck_pop(main_text = "beta version created in {}".format(used_time))


        
        
        
        
    if publish_stable_version:
        time_start = time.time()
        print ("Publishing stable version...")
        FOLDER.copy_dir(src, 
                        stable_dst, 
                        ignore_keywords = ["EnneadTab_Beta", "EnneadTab_Basic", "EnneadTab_Tailor", "EnneadTab_Advanced"],
                        allow_print_log=allow_print_log)
        update_yaml(stable_dst, disable_advanced=True, disable_SZ=True)
        used_time = time.time() - time_start
        used_time = TIME.get_readable_time(used_time)
        NOTIFICATION.duck_pop(main_text = "basic version created in {}".format(used_time))
        
        
        if not os.path.exists(SH_version_dst):
            time_start = time.time()
            print ("Publishing SH version...")
            FOLDER.copy_dir(src, 
                            SH_version_dst,
                            allow_print_log=allow_print_log)
            print ("SH version created")
            SOUNDS.play_sound("sound effect_mario fireball.wav")
            
            update_yaml(SH_version_dst, disable_advanced=True, disable_SZ=True)
            used_time = time.time() - time_start
            used_time = TIME.get_readable_time(used_time)

            NOTIFICATION.duck_pop(main_text = "SH version created in {}".format(used_time))

    update_icon()

    
    time_start = time.time()
    print ("Publishing archive version...")
    FOLDER.copy_dir(src, 
                    archive_dst,
                    allow_print_log=allow_print_log)
    used_time = time.time() - time_start
    used_time = TIME.get_readable_time(used_time)
    SOUNDS.play_sound("sound effect_mario fireball.wav")
    NOTIFICATION.duck_pop(main_text = "archive version created in {}".format(used_time))


    #allow copy to distribution folder. This is not to be confised with the _revit which is used
    #  for local run. The below are distubuted for pyRevit direct hook extension from Github. Only still doing this to 
    # keep a few users using this method happy.
    if not os.path.exists(ENVIRONMENT.DISTIBUTION_FOLDER):
        return
    time_start = time.time()
    print ("Publishing dist version...")
    dist_dst = ENVIRONMENT.DISTIBUTION_FOLDER
    for folder_or_file in os.listdir(dist_dst):
        if folder_or_file.endswith(".tab") \
            or folder_or_file in ["hooks", "lib", "bin"] \
            or folder_or_file.endswith(".py") \
            or folder_or_file.endswith(".xaml") \
            or folder_or_file.endswith(".yaml"):
            try:
                shutil.rmtree(os.path.join(dist_dst, folder_or_file))
            except:
                os.remove(os.path.join(dist_dst, folder_or_file))
    FOLDER.copy_dir(src,
                    dist_dst,
                    allow_print_log=allow_print_log)
    used_time = time.time() - time_start
    used_time = TIME.get_readable_time(used_time)
    NOTIFICATION.duck_pop(main_text = "dist version created in {}".format(used_time))




    print ("\n\nTool finished")


def update_yaml(dst_repo, disable_advanced, disable_SZ):
    allow_print_log = False
    for root, dirs, files in os.walk(dst_repo):
        for file in files:
            if not file.endswith(".yaml"):
                continue
            with open(os.path.join(root, file), "r") as f:
                # get each line, if the line contain "advanced_only" then replace first "-" with "#-"
                lines = f.readlines()
                for i in range(len(lines)):
                    if "advanced_only" in lines[i] and disable_advanced:
                        lines[i] = lines[i].replace("-", "#-")
                    if "SZ_only" in lines[i] and disable_SZ:
                        lines[i] = lines[i].replace("-", "#-")
                        

            with open(os.path.join(root, file), "w") as f:
                # write the new lines back to file
                f.writelines(lines)
            if allow_print_log:
                print ("file: {} has been updated to be advanced only".format(os.path.join(root, file)))

def update_icon():
    icon_source = "{}\\ENNEAD.extension\\Ennead.tab\\Resource.panel\\EnneadTab_Setting_UI.pushbutton\\icons\\basic_icon.png".format(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT)
    icon_target = "{}\\ENNEAD.extension\\Ennead.tab\\Resource.panel\\EnneadTab_Setting_UI.pushbutton\\Icon.png".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT)
    FOLDER.copy_file(icon_source, icon_target)
    icon_source = "{}\\ENNEAD.extension\\Ennead.tab\\Resource.panel\\EnneadTab_Setting_UI.pushbutton\\icons\\advanced_icon.png".format(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT)
    icon_target = "{}\\ENNEAD.extension\\Ennead.tab\\Resource.panel\\EnneadTab_Setting_UI.pushbutton\\icon.png".format(ENVIRONMENT.PUBLISH_BETA_FOLDER_FOR_REVIT)
    FOLDER.copy_file(icon_source, icon_target)
    


def publish_Rhino_python_file():
    if not ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        print ("Should do this in Rhino enviornment")
        return

    import rhinoscriptsyntax as rs

    source_files = rs.OpenFileNames(title = "Pick for Rhino script file and its icon to publish", filter = "Python and PNG File(*.py or *.png)|*.py;*.png|Python File(*.py)|*.py|Icon png(*.png)|*.png||")
    for file in source_files:
        tartget = file.replace(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO,
                                ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO )
        FOLDER.copy_file(file, tartget)
    SOUNDS.play_sound("sound effect_mario fireball.wav")


def publish_Rhino_source_code(deep_copy = False):
    # if not ENVIRONMENT_CONSTANTS.is_Rhino_environment():
    #     print ("Should do this in Rhino enviornment")
    #     return

    show_progress = False
    allow_print_log = False
    print ("Beigning to copy folders...")
    FOLDER.copy_dir(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO, 
                    ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, 
                    show_progress = show_progress, 
                    progress_bar_note = "github working>>>L drive",
                    allow_print_log=allow_print_log)
    NOTIFICATION.toast(main_text = "Publish Done")
    SOUNDS.play_sound("sound effect_mario fireball.wav")
    NOTIFICATION.duck_pop("Main Copy Finish!")
    if not deep_copy:
        return

    archive = "{}\{}_EnneadTab for Rhino Backup".format(ENVIRONMENT.ARCHIVE_FOLDER_FOR_RHINO, TIME.get_YYYYMMDD())
    FOLDER.copy_dir(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, 
                    archive, 
                    show_progress = show_progress, 
                    progress_bar_note = "L drive>>> {}_backup".format(TIME.get_YYYYMMDD()),
                    allow_print_log=allow_print_log)
    NOTIFICATION.toast(main_text = "Backup Done")
    print ("Copying over.")
    SOUNDS.play_sound("sound effect_mario fireball.wav")
    
    
    NOTIFICATION.duck_pop("Deep Copy Finish!")




def publish_dist_folder():

    softwares = [  "_revit","_rhino"]
    if not os.path.exists(ENVIRONMENT.DISTIBUTION_FOLDER):
        return
    time_start = time.time()
    print ("Publishing dist version...")
    dist_dst = ENVIRONMENT.DISTIBUTION_FOLDER
    for folder_or_file in os.listdir(dist_dst):
        if folder_or_file in softwares:
            try:
                shutil.rmtree(os.path.join(dist_dst, folder_or_file))
            except:
                os.remove(os.path.join(dist_dst, folder_or_file))

    for software in softwares:
        target = "{}\\{}".format(dist_dst, software)
        if not os.path.exists(target):
            os.makedirs(target)
        source_folder = getattr(ENVIRONMENT, "WORKING_FOLDER_FOR_{}".format(software.upper().replace("_", "")))
        FOLDER.copy_dir(source_folder,
                        target,
                        allow_print_log=False,
                        ignore_keywords=["EnneadTab Developer.extension"])
    used_time = time.time() - time_start
    used_time = TIME.get_readable_time(used_time)
    NOTIFICATION.duck_pop(main_text = "dist version created in {}".format(used_time))

    GIT.push_changes_to_main(dist_dst)

def install_EA_dist():

    exes = [ENVIRONMENT_CONSTANTS.EXE_FOLDER + "\\EnneadTab Installer.exe",
            ENVIRONMENT_CONSTANTS.PUBLIC_L_EXE_FOLDER + "\\EnneadTab Installer.exe"]
    for exe in exes:
        if os.path.exists(exe):
            break
       
    
    EXE.open_file_in_default_application(exe)

def update_EA_dist():
    install_EA_dist()
#############
if __name__ == "__main__":
    # publish_Rhino_source_code(deep_copy = False)
    print(__file__ + "   -----OK!")
    publish_dist_folder()
    install_EA_dist()