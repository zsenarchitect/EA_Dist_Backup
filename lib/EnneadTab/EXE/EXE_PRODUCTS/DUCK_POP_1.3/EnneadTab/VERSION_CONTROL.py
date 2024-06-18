#!/usr/bin/python
# -*- coding: utf-8 -*-
#import distutils

import os
import TIME
import FOLDER
import ENVIRONMENT
import NOTIFICATION
import ERROR_HANDLE
import SOUNDS

def publish_ENNEAD_module():
    #working_root = ENVIRONMENT.get_EnneadTab_WORKING_root()
    if ENVIRONMENT.is_Revit_environment():
        _publish_ENNEAD_module_from_revit()
        return
    if ENVIRONMENT.is_Rhino_environment():
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
    src = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension"
    #dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\test folder_ennead_extension"
    stable_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension"
    beta_tester_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension"


    year, month, day = TIME.get_date_as_tuple()
    archive_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\_Archive\{}{}{}_ENNEAD.extension".format(year, month, day)
    SH_version_dst = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_SH_VERSION\VERSION_{}_{}_{}\SH_ENNEAD.extension".format(year, month, day)
    #distutils.dir_util.copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, update=0, verbose=0, dry_run=0)


    #copytree(src, dst)
    if publish_stable_version:
        FOLDER.copy_dir(src, stable_dst, ignore_keywords = ["EnneadTab_Beta", "EnneadTab_Basic", "EnneadTab_Tailor", "EnneadTab_Advanced"])
        if not os.path.exists(SH_version_dst):
            FOLDER.copy_dir(src, SH_version_dst)
            print ("SH version created")
            SOUNDS.play_sound("sound effect_mario fireball.wav")
            
            update_yaml(SH_version_dst, disable_advanced=True, disable_SZ=True)
        update_yaml(stable_dst, disable_advanced=True, disable_SZ=True)

    if publish_beta_version:
        FOLDER.copy_dir(src, beta_tester_dst)
        SOUNDS.play_sound("sound effect_mario fireball.wav")
        update_yaml(beta_tester_dst, disable_advanced=False, disable_SZ=True)


    FOLDER.copy_dir(src, archive_dst)
    SOUNDS.play_sound("sound effect_mario fireball.wav")




    print ("\n\nTool finished")


def update_yaml(dst_repo, disable_advanced, disable_SZ):
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
            print ("file: {} has been updated to be advanced only".format(os.path.join(root, file)))




def publish_Rhino_python_file():
    if not ENVIRONMENT.is_Rhino_environment():
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
    if not ENVIRONMENT.is_Rhino_environment():
        print ("Should do this in Rhino enviornment")
        return

    print ("Beigning to copy folders...")
    FOLDER.copy_dir(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO, ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, show_progress = False, progress_bar_note = "github working>>>L drive")
    NOTIFICATION.toast(main_text = "Publish Done")
    SOUNDS.play_sound("sound effect_mario fireball.wav")
    if not deep_copy:
        return

    archive = "{}\{}_EnneadTab for Rhino Backup".format(ENVIRONMENT.ARCHIVE_FOLDER_FOR_RHINO, TIME.get_YYYYMMDD())
    FOLDER.copy_dir(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, archive, show_progress = False, progress_bar_note = "L drive>>> {}_backup".format(TIME.get_YYYYMMDD()))
    NOTIFICATION.toast(main_text = "Backup Done")
    print ("Copying over.")
    SOUNDS.play_sound("sound effect_mario fireball.wav")



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")