
import os
import shutil


import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import USER
import ENVIRONMENT_CONSTANTS
import ENVIRONMENT
import FOLDER
import ERROR_HANDLE
import EMAIL
import random
try:
    import rhinoscriptsyntax as rs
    if random.random() < 0.001:
        import OUTPUT
        output = OUTPUT.get_output()
        output.write("EnneadTab in hibernation mode.", OUTPUT.Style.Title) 
        output.write("Due to staffing plan change, Sen Zhang is no longer maintaining EnneadTab.")
        output.write("Bug-fix and feature-build are suspended.")
        output.write("{}\\hibernation_large.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        """https://www.fontspace.com/cobemat-cartoon-font-f104361
        this is the font webpage"""
        output.plot()
except:
    pass

if USER.is_enneadtab_developer():
    EDITOR_VERSION_OLD = "{}\\Working\\EnneadTab.rui".format(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
    EDITOR_VERSION = "{}\\Working\\Ennead-For-Rhino.rui".format(ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
else:
    EDITOR_VERSION_OLD = "{}\\EnneadTab for Rhino\\EnneadTab.rui".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    EDITOR_VERSION = "{}\\EnneadTab for Rhino\\Ennead-For-Rhino.rui".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)



# TO-DO: depreciate this, use USER_CONSTSNATS func "is_SH_account()"
SH_USER_NAMES = ["qian.yu",
                 "Shu.Shang",
                 "xsun",
                 "xxu"]

@ERROR_HANDLE.try_catch_error_silently
def is_enneadtab_registered(email_result = False):
    if not ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        return None
    

    if USER.is_enneadtab_developer():
        return None

    try:
        import rhinoscriptsyntax as rs
    except:
        return None
    current_rui = rs.ToolbarCollectionPath("EnneadTab")
    if not current_rui:

        current_rui = "not using main rui. If you are only accessing from grasshopper, it is safe but still recommended to load the main rui first per EI instruction, so you can enjoy the main Rhino plugin functionalities. Then, do the following:" 
    is_enneadtab_registered =  current_rui.startswith("{}\\Users".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO))
    is_using_local_dump_rui = "Rhino Local Copy" in current_rui # for SH people this is allowed to use Local copy folder.-- also allowing developer who is NOT the main driver to use that folder
    if not is_enneadtab_registered and email_result and not is_using_local_dump_rui:
        user_name = USER.get_user_name()
        user_name = user_name.replace(".EA","")
        # TO-DO: depreciate this, use USER_CONSTSNATS func "get_email()"
        if user_name not in SH_USER_NAMES:
            instructions = "Step 1: Have only ONE rhino left open.\nStep 2: Click register from the menu.\nStep 3: Restart Rhino to confirm the setting."
            instructions += "\n\n\nYou might receive multiple emails about the same instruction until above step is finished."
            EMAIL.email(sender_email=None,
                        receiver_email_list=["{}@ennead.com".format(user_name)],
                        subject="EnneadTab Rhino Find Unregistered User.",
                        body="This user is not registered in EnneadTab for Rhino. Current rui is: {}.\n\n{}".format(current_rui, instructions),
                        body_folder_link_list=None,
                        body_image_link_list=None,
                        attachment_list=None,
                        schedule_time=None)
        

            
    return is_enneadtab_registered


def is_current_enneadtab_on_main_rui():

    current_rui = rs.ToolbarCollectionPath("EnneadTab")
    main_rui = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\EnneadTab for Rhino\\EnneadTab.rui"
    return current_rui == main_rui




def publish_rui():

    if not USER.is_enneadtab_developer():
        return
    publish_rui_to_server()
    publish_rui_to_users()



def update_my_rui():
    if USER.IS_CURRENT_RHINO_RUI_EDITOR:
        return

    
    rs.CloseToolbarCollection("EnneadTab", prompt=False)

    


    folder_name = "EnneadTab for Rhino Local Copy"
    folder = FOLDER.get_special_folder_in_EA_setting(folder_name)
    my_local_version = folder + "\\EnneadTab.rui"


    folder = "{}\\Users\\{}".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, USER.get_user_name()) 
    folder = FOLDER.secure_folder(folder)
    my_user_folder_version = folder + "\\EnneadTab.rui"

    try:
        shutil.copyfile(EDITOR_VERSION_OLD, my_user_folder_version)
        if not USER.is_enneadtab_developer():
            rs.OpenToolbarCollection(my_user_folder_version)
        else:
            rs.OpenToolbarCollection(my_local_version)
        return
    except:
        shutil.copyfile(EDITOR_VERSION_OLD, my_local_version)
        rs.OpenToolbarCollection(my_local_version)
    

def publish_rui_to_server():

    # copy over
    tartget_version = "{}\\EnneadTab for Rhino\\EnneadTab.rui".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    shutil.copyfile(EDITOR_VERSION_OLD, tartget_version)
    # tartget_version = "{}\\EnneadTab for Rhino\\Ennead-For-Rhino.rui".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    # shutil.copyfile(EDITOR_VERSION, tartget_version)

    # clean up all rui_bak file in folder and nesting folder
    folder = "{}\\EnneadTab for Rhino".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    for file in os.listdir(folder):
        if not file.endswith(".rui"):
            os.remove(os.path.join(folder, file))

    
def publish_rui_to_users():

    folder = "{}\\Users".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    
    for user_folder in os.listdir(folder):

        # clean folder now
        for f in os.listdir(folder + "\\" + user_folder):
            if not f.endswith(".rui"):
                try:
                    os.remove(folder + "\\" + user_folder + "\\" + f)
                except:
                    pass
        
        target_old = "{}\\{}\\EnneadTab.rui".format(folder, user_folder)
        target = "{}\\{}\\Ennead-For-Rhino.rui".format(folder, user_folder)
        
        try:
            shutil.copyfile(EDITOR_VERSION_OLD, target_old)
            # shutil.copyfile(EDITOR_VERSION, target)
        except:
            pass

def unit_test():
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        print ("Current user is registered: {}".format(is_enneadtab_registered()))


    
if __name__ == "__main__":
    print (EDITOR_VERSION_OLD)
    tartget_version = "{}\\EnneadTab for Rhino\\EnneadTab.rui".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    print (tartget_version)
    update_my_rui()