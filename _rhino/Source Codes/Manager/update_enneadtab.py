import traceback
import os
import json
import rhinoscriptsyntax as rs
import scriptcontext as sc
import shutil
import sys
sys.path.append("..\lib")
import EnneadTab


def get_latest_toolbar():

    # rs.CloseToolbarCollection("Enscape.Rhino7.Plugin", prompt = False)
    # reload(EA)
    if EnneadTab.USER.is_SZ():
        EnneadTab.NOTIFICATION.messenger(main_text="Skip RUI reassign for Sen Zhang")
        return
    folder_name = "EnneadTab for Rhino Local Copy"
    folder = EnneadTab.FOLDER.get_special_folder_in_EA_setting(folder_name)
    target = folder + "\EnneadTab.rui"
    rs.SaveToolbarCollectionAs("EnneadTab", target)

    rs.CloseToolbarCollection("EnneadTab", prompt=False)
    original = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Working\EnneadTab.rui"
    target = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino\EnneadTab.rui"

    user_name = os.environ["USERPROFILE"].split("\\")[-1]
    folder = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Users" + "\\" + user_name
    folder = EnneadTab.FOLDER.secure_folder(folder)
    target = folder + "\EnneadTab.rui"

    """
    folder_name = "EnneadTab for Rhino Local Copy"
    folder = EnneadTab.FOLDER.get_special_folder_in_EA_setting(folder_name)
    target = folder + "\EnneadTab.rui"
    """
    try:
        shutil.copyfile(original, target)
        rs.OpenToolbarCollection(target)
    except Exception as e:
        print(e)
        folder_name = "EnneadTab for Rhino Local Copy"
        folder = EnneadTab.FOLDER.get_special_folder_in_EA_setting(folder_name)
        target = folder + "\EnneadTab.rui"
        shutil.copyfile(original, target)
        rs.OpenToolbarCollection(target)


def notify_GH_repo_error(error_message):
    error_message = "When user [{}] attemp to update EA standard Grasshopper Repo, the following error has occured.\n\n{}".format(EnneadTab.USER.get_user_name(),
                                                                                                                                  error_message)
    EnneadTab.EMAIL.email(receiver_email_list=["Colin.Matthews@ennead.com"],
                          subject="GH repo update failed",
                          body=error_message)


def update_grasshopper_repo():
    def display_update_message():
        EnneadTab.NOTIFICATION.messenger(main_text="Updating Ennead Standard Grasshopper library, this might take a few minutes.")



    local_lib_folder = "C:\\Users\\{}\\AppData\\Roaming\\Grasshopper\\Libraries\\EnneadPlugins-gha".format(
        EnneadTab.USER.get_user_name())
    local_userobj_folder = "C:\\Users\\{}\\AppData\\Roaming\\Grasshopper\\UserObjects\\EnneadUserObjects-ghuser".format(
        EnneadTab.USER.get_user_name())

    # get the folder of L drive repo
    gh_repo_lib_folder = "L:\\4b_Applied Computing\\04_Grasshopper\\000_PLUGINS\\EA Standard Grasshopper Plugins\\EnneadPlugins-gha"
    gh_repo_user_folder = "L:\\4b_Applied Computing\\04_Grasshopper\\000_PLUGINS\\EA Standard Grasshopper User Objects\\EnneadUserObjects-ghuser"

    # check if the gh libraries are outdated
    is_main_lib_outdated = is_gh_repo_outdated(
        local_lib_folder, gh_repo_lib_folder)
    is_userobj_outdated = is_gh_repo_outdated(
        local_userobj_folder, gh_repo_user_folder)

    if not is_main_lib_outdated and not is_userobj_outdated:
        return

    display_update_message()

    if is_main_lib_outdated:
        # updating plugins only
        try:
            gh_repo_update_action(gh_repo_lib_folder, local_lib_folder)
        except Exception as e:
            print("Error occured: {}".format(e))
            notify_GH_repo_error(traceback.format_exc())

    if is_userobj_outdated:
        # updating user objects onlys
        try:
            gh_repo_update_action(gh_repo_user_folder, local_userobj_folder)
        except Exception as e:
            print("Error occured: {}".format(e))
            notify_GH_repo_error(traceback.format_exc())

def is_gh_repo_outdated(local_folder, gh_repo_folder):
    def get_last_updated_date(file_path):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path) as json_file:
                data = json.load(json_file)
                return data["last_updated"]
        except Exception as e:
            print("Error occured: {}".format(e))
            notify_GH_repo_error(traceback.format_exc())
            return None

    local_folder_json = "00_" + local_folder.split("\\")[-1] + ".json"
    gh_repo_folder_json = "00_" + gh_repo_folder.split("\\")[-1] + ".json"

    local_last_updated = get_last_updated_date("{}\\{}".format(local_folder, local_folder_json))
    remote_last_updated = get_last_updated_date("{}\\{}".format(gh_repo_folder, gh_repo_folder_json))

    return local_last_updated != remote_last_updated and local_last_updated is not None


def gh_repo_update_action(source_folder, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # purge the  local folder, if Ennead plugins exist
    EnneadTab.FOLDER.purge_folder(target_folder)

    # copy from L drive repo to user local grasshopper folder
    EnneadTab.FOLDER.copy_dir(source_folder, target_folder)


def reload_all_modules():
    # also reload python engine for EA module
    import sys
    sys.path.append("..\lib")
    # import EA_UTILITY as EA
    import EnneadTab

    import reload_python
    try:
        reload_python.main()
    except:
        pass


def add_alias_set():
    # add alias for this
    try:
        import alias_manager
        alias_manager.add_alias_set()
    except:
        pass
    


def assist_add_startup():
    return
    rs.ClipboardText(
        text='! _-RunPythonScript "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\lib\EA_STARTUP.py"')
    return
    import sys
    sys.path.append("..\lib")
    import EA_UTILITY

    filepath = r"L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Manager\instruction_add startup.pdf"
    EA_UTILITY.open_file_in_default_application(filepath)
    filepath = r"L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Manager\instruction_add startup.txt"
    EA_UTILITY.open_file_in_default_application(filepath)


def add_rs_path():
    """make sure developer are pointing to designer folder, and user are pointing to publish folder"""
    good_lib = EnneadTab.ENVIRONMENT.CORE_MODULE_FOLDER_FOR_PUBLISHED_RHINO
    bad_lib = EnneadTab.ENVIRONMENT.CORE_MODULE_FOLDER_FOR_RHINO
    if EnneadTab.USER.is_enneadtab_developer():
        good_lib, bad_lib = bad_lib, good_lib
    
    if bad_lib in rs.SearchPathList():
        rs.DeleteSearchPath(bad_lib)
    rs.AddSearchPath(good_lib)

def prompt_to_add_startup_script():
    if EnneadTab.USER.get_user_name() in []:
        return
    
    
    image = "{}\\Source Codes\\Manager\\how_to_starter.png".format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    EnneadTab.EMAIL.email_to_self(subject="EnneadTab Auto Email: Please add starter command",
                                body="Hello!\nIf you want to have EnneadTab loaded faster, you can initialize EnneadTab during rhino startup by adding 'EnneadTab_Starter' at below location at setting.\n\nPlease ONLY HAVE ONE RHINO OPEN when adding this command, and restart Rhino to make it effective.\n\nTo stop receiving email about this topic, msg Sen Zhang.",
                                body_image_link_list=[image])

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def update_enneadtab():
    add_rs_path()
    update_grasshopper_repo()
    try:
        EnneadTab.RHINO.RHINO_RUI.update_my_rui()
    except:
        if EnneadTab.USER.is_SZ():
            EnneadTab.NOTIFICATION.duck_pop("new updater failed")
        get_latest_toolbar()
    assist_add_startup()
    reload_all_modules()
    add_alias_set()
    
    prompt_to_add_startup_script()
    EnneadTab.NOTIFICATION.messenger(main_text="Latest EnneadTab Loaded.\nPreviously docked EnneadTab can be removed from your UI.")
##########################################################################


if (__name__ == "__main__"):
    update_enneadtab()
