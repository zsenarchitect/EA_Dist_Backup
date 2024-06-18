#!/usr/bin/python
# -*- coding: utf-8 -*-
import FOLDER
import DATA_FILE
import USER
import EXE
import ENVIRONMENT
import NOTIFICATION


def random_speak(lines, chance=1.0):
    import random
    if random.random() <= chance:
        random.shuffle(lines)
        speak(lines[0])


def is_hate_talkie():
    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        return False


    setting_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = DATA_FILE.read_json_as_dict(setting_file)
    return not data.get("toggle_bt_is_talkie", True)
    """
    return not DATA_FILE.get_revit_ui_setting_data(("toggle_bt_is_talkie", True))


def speak(text, language='en', accent='com', force_talk = False):
    # print "speaker start: " + text
    """
    #language = 'zh-CN'
    #language = 'zh-TW'
    #language = 'en'

    #accent = 'co.uk'
    #accent = 'co.in'
    #accent = 'com'
    """
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return
    
    
    if not force_talk:
        if is_hate_talkie():
            # print "won't talk becasue you hate talkie"
            return

        if NOTIFICATION.get_toaster_level_setting() > 0:
            # print "won't talk becasue my toaster level is {}".format(NOTIFICATION.get_toaster_level_setting())
            return

    if text:
        data = dict()
        data["text"] = text
        data["language"] = language
        data["accent"] = accent
        file_name = "EA_Text2Speech.json"
        # dump_folder = FOLDER.get_EA_local_dump_folder()
        # file_path = "{}\{}".format(dump_folder, file_name)
        file_path = FOLDER.get_EA_dump_folder_file(file_name)
        # print file_path
        DATA_FILE.save_dict_to_json(data, file_path)
        # print "talkie data saved"

    run_exe()

    # print 123
    # try:
    #     import imp
    #     full_file_path = r'{}\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\text2speech.pushbutton\TTS_script.py'.format(ENVIRONMENT.get_EnneadTab_For_Revit_root())

    #     ref_module = imp.load_source("TTS_script", full_file_path)

    #     ref_module.run_exe()

    # except:
    #     print 456
    #     exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\EA_TEXT2SPEECH_2.0\EA_TEXT2SPEECH.exe - Shortcut"

    #     try:
    #         EXE.open_file_in_default_application(exe_location)
    #     except Exception as e:
    #         print exe_location
    #         print str(e)


def run_exe():

    if is_hate_talkie():
        # print "won't talk becasue you hate talkie"
        return

    
    version = 2.3
    exe_location = "{}\\EA_TEXT2SPEECH_{}\\EA_TEXT2SPEECH.exe - Shortcut".format(ENVIRONMENT.EXE_FOLDER, version)
    EXE.open_file_in_default_application(exe_location)



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")