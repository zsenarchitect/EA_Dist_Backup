#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import ENVIRONMENT
import ERROR_HANDLE
import FOLDER
import DATA_FILE
import USER
import EXE


def OLD_is_hate_toast():
    dump_folder = FOLDER.get_EA_local_dump_folder()
    file_name = "EA_TOASTER_KILL.kill"
    return FOLDER.is_file_exist_in_folder(file_name, dump_folder)


def get_toaster_level_setting():
    """return in integer how sever the level is. rnage from 0, 1, 2.
    

    Returns:
        int: Default as 1.
        0 = lowest, all level can pass
        2 = highest, only most sever level can pass
    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        return 1

    setting_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = DATA_FILE.read_json_as_dict(setting_file)
    if data.get("radio_bt_popup_minimal", False):
        return 2  # allowing the highest level to pass
    if data.get("radio_bt_popup_standard", False):
        return 1
    if data.get("radio_bt_popup_full", False):
        return 0  # allow any level to pass, becasue any level is larger than 0

    return 1


def messager(main_text,
             force_toast=False,
             importance_level=1,
             width = 1200,
             height = 150,
             image = None,
             animation_stay_duration = 5,
             print_note = False):
    """pop simple messag from bm of screen and disappear later. This can replace the WIN versino becasue it is less annoying with sound.

    Args:
        main_text (str): the message to show. Better within 2 return lines. If too long, please use line return
        force_toast (bool, optional): ignore level, always pop. Defaults to False.
        importance_level (int, optional): dtermin when to show this pop. Defaults to 1.
        width (int, optional): how width is the message max width. Defaults to 1200.
        height (int, optional): how tall is the message max height. Defaults to 150.
    """
    if not force_toast:
        if get_toaster_level_setting() <= importance_level:
            pass
        else:
            return

    # from MESSAGER import MessageApp
    #app = MessageApp(main_text)
    #app.run()
    if print_note:
        print (main_text)
     
     
    import os
    if os.environ["USERPROFILE"].split("\\")[-1] in ["eshaw" , "szhang"]:   
        import random
        if random.random() < 0.02:
            duck_pop(main_text) 
            return
    
    data = {}
    data["main_text"] = main_text
    data["animation_in_duration"] = 0.5
    data["animation_stay_duration"] = animation_stay_duration
    data["animation_fade_duration"] = 2
    data["width"] = width
    data["height"] = height
    data["image"] = image
    DATA_FILE.save_dict_to_json_in_dump_folder(data, "MESSAGER.json")
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\MESSAGER_1.4\MESSAGER.exe"
    EXE.open_file_in_default_application(exe_location)


    try:
        import RHINO.RHINO_UI
        RHINO.RHINO_UI.is_enneadtab_registered(email_result=True)
    except:
        pass

def duck_pop(main_text = None):
    if not main_text:
        main_text = "Quack!"


    data = {"main_text":main_text,"image":None}
    
    DATA_FILE.save_dict_to_json_in_dump_folder(data, "DUCK_POP.json")
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\DUCK_POP_1.3\DUCK_POP.exe"
    EXE.open_file_in_default_application(exe_location)

def toast(sub_text="",
          main_text="",
          app_name=None,
          icon=None,
          click=None,
          actions=None,
          force_toast=False,
          importance_level=1):
    """Send toast notificaton.
    Args:
        click (str): click action (see `--activation-arg` cli option)
        actions (dict[str:str]):
            list of actions (see `--action` and `--action-arg` cli options)

        importance_level = [0,1,2]: 
            0: low
            1: med
            2: high

            if user setting == 0, it should allow level 0,1,2
            if user setting == 1, it should allow level 0,1 to pass, reject level 0   
            if user setting == 2, it should allow level 2 to pass, reject level 0 ,1  


    """

    """
    if not force_toast and is_hate_toast():
        return
    """
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    if get_toaster_level_setting() <= importance_level:
        pass
    else:
        return

    def get_toaster():
        """Return full file path of the toast binary utility."""
        return r"{}\Source Codes\lib\EnneadTab\EXE\Ennead_Toaster.exe".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)

    def get_app_name():
        if ENVIRONMENT.is_Rhino_environment():
            return "EnneadTab For Rhino"
        if ENVIRONMENT.is_Revit_environment():
            return "EnneadTab For Revit"
        return "EnneadTab Moniter"

    # set defaults
    if not icon:
        icon = r"{}\Source Codes\lib\EnneadTab\images\toaster_icon_{}.png".format(
            ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO, ENVIRONMENT.primary_app_name())
    if not actions:
        actions = {}
    if not app_name:
        app_name = get_app_name()

    # build the toast
    toast_args = r'"{}"'.format(get_toaster())
    toast_args += r' --app-id "{}"'.format(app_name)
    toast_args += r' --title "{}"'.format(main_text)
    toast_args += r' --message "{}"'.format(sub_text)
    toast_args += r' --icon "{}"'.format(icon)
    toast_args += r' --audio "default"'
    # toast_args += r' --duration "long"'
    if click:
        toast_args += r' --activation-arg "{}"'.format(click)
    for action, args in actions.items():
        toast_args += r' --action "{}" --action-arg "{}"'.format(action, args)

    # send the toast now
    subprocess.Popen(toast_args, shell=True)


def get_annoucement_file():
    return r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\beta_annoucement.json"


def checkout_annoucement_panel(topic):
    annoucement_file = get_annoucement_file()

    data = DATA_FILE.read_json_file_safely(annoucement_file)

    topic_name_list = data.get(topic, None)
    if topic_name_list:
        user = USER.get_user_name()
        # if user not in topic_name_list:
        #     return

        topic_name_list[user] = True
        DATA_FILE.save_dict_to_json(data, annoucement_file)
        return


def publish_new_topic(topic, beta_tester_only=True):
    annoucement_file = get_annoucement_file()
    data = DATA_FILE.read_json_file_safely(annoucement_file)
    if topic in data:
        print("This topic exist. Skip adding.")
        return

    temp = dict()
    if beta_tester_only:
        group = USER.get_all_revit_beta_testers()
    else:
        group = USER.get_all_revit_users()
    for user in group:
        temp[user] = False

    data[topic] = temp
    DATA_FILE.save_dict_to_json(data, annoucement_file)


def let_read_annoucement(topic, main_text, sub_text=None, images=None):

    # terminate early if the topic is already read for this user
    annoucement_file = get_annoucement_file()
    data = DATA_FILE.read_json_file_safely(annoucement_file)
    topic_name_list = data.get(topic, None)
    if topic_name_list:
        is_checked = topic_name_list.get(USER.get_user_name(), None)
        if is_checked:
            return

    from pyrevit import script
    import REVIT

    output = script.get_output()
    # output.print_md("**SH team please note that Autodesk will maintain cloud server on July 10, this might overlap with your working hour on Monday.**")
    if images:
        for image in images:
            output.print_image(image)

    ops = [["Got it!", "(Do not show this topic again)"], "Remind me later."]
    res = REVIT.REVIT_FORMS.dialogue(
        main_text=main_text, sub_text=sub_text, options=ops)
    if res == ops[0][0]:
        checkout_annoucement_panel(topic)
        return







def show_loading_screen_bar(display_text, time = 2):
    """show a loading bar animation that is indipdenent of the application framework. This should reduce the pschological stresss of waiting.

    Args:
        display_text (_type_): _description_
        time (int, optional): _description_. Defaults to 2.
    """
    text_source_file = "EA_LOADING_SCREEN_TEXT.json"
    file = "{}\{}".format(FOLDER.get_EA_local_dump_folder(), text_source_file)
    data = dict()
    data["text"] = display_text
    data["time"] = time# in seconds
    DATA_FILE.save_dict_to_json(data, file)
    loading_screen_exe = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EA_LOADING_SCREEN_EXE\make_loading_bar\make_loading_bar.exe"
    EXE.open_file_in_default_application(loading_screen_exe)









if __name__ == "__main__":
    # toast("123")
    duck_pop(main_text= "test")
