#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Utility module for last sync record."
__title__ = "set_sync_time_record"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #


from EnneadTab.REVIT import REVIT_FORMS
from EnneadTab import EXE, DATA_FILE, NOTIFICATION, SPEAK, ERROR_HANDLE, FOLDER
import ENNEAD_LOG
import time
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore

FILE_NAME = "EA_Last_Sync_Record.json"
def get_record_file_path():
    dump_folder = FOLDER.get_EA_local_dump_folder()
    file_name = FILE_NAME
    file_path = "{}\{}".format(dump_folder, file_name)
    return file_path

def get_data_from_record_file():
    file_path = get_record_file_path()
    file_name = FILE_NAME
    if FOLDER.is_file_exist_in_folder(file_name, FOLDER.get_EA_local_dump_folder()):
        data = DATA_FILE.read_json_as_dict(file_path)
    else:
        data = dict()
    return data

@ERROR_HANDLE.try_catch_error
def kill_record():
    from pyrevit import forms
    data = get_data_from_record_file()
    if not data:
        NOTIFICATION.messenger(main_text = "No Active Record Found!!!")

        
        return

    """
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{} :Last Record {}".format(self.item)

    ops = [MyOption(key, value) for key, value in data]
    """
    keys = forms.SelectFromList.show(data.keys(),
                                    multiselect = True,
                                    title = "Want to kill curtain record from last sync monitor?",
                                    button_name = 'Kill Selected Record(s)')
    if not keys:
        return

    for key in keys:
        del data[key]

    DATA_FILE.save_dict_to_json(data, get_record_file_path())


@ERROR_HANDLE.try_catch_error
def update_last_sync_data_file(doc):
    if "detach" in doc.Title.lower():
        return

    data = get_data_from_record_file()
    if  data:
        for key, value in data.items():
            if time.time() - value  > 60*60*24:#record older than 24 hour should be removed
                del data[key]

    try:
        if doc.IsModified:
            punish_long_gap_time(data)
    except Exception as e:
        print (e)


    try:
        doc.Title
    except:
        return
    if not data:
        data = dict()
    data[doc.Title] = time.time()
    DATA_FILE.save_dict_to_json(data, get_record_file_path())

def remove_last_sync_data_file(doc):

    data = get_data_from_record_file()
    if not data:
        return

    if doc.Title not in data.keys():
        return
    del data[doc.Title]
    DATA_FILE.save_dict_to_json(data, get_record_file_path())


@ERROR_HANDLE.try_catch_error
def punish_long_gap_time(data):

    now = time.time()
    min_max = 90
    for key, value in data.items():
        if now - value  > 60 * min_max:
            #print int( (now - value - 60 * min_max) / 60)
            try:
                ENNEAD_LOG.sync_gap_too_long(mins_exceeded = int( (now - value - 60 * min_max) / 60), doc_name = key )
            except:
                ENNEAD_LOG.sync_gap_too_long(mins_exceeded = int( (now - value - 60 * min_max) / 60) )





@ERROR_HANDLE.try_catch_error
def is_doc_opened(doc):
    data = get_data_from_record_file()
    if not data:
        return False

    if doc.Title in data.keys():
        NOTIFICATION.toast(main_text = "Wait a minutes...", sub_text = "This document seems to be opened already.")
        SPEAK.speak("Unless you recently crashed Revit, this document seems to be opened already. You should prevent opening same file on same machine, because this will confuse central model which local version to allow sync.")
        REVIT_FORMS.notification(main_text = "This document seems to be opened already in other session.\nOr maybe recently crashed.\nAnyway, I have detected the record already existing.",
                                        sub_text = "Double check if this double opening is intentional.\nThere is another possibility that your last session crashed and the exit is not logged. In that case, please ignore this message box.",
                                        self_destruct = 20)
        return True
    return False

@ERROR_HANDLE.try_catch_error
def is_hate_sync_monitor():
    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        return False


    setting_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = DATA_FILE.read_json_as_dict(setting_file)
    return data.get("radio_bt_sync_monitor_never", False)
    """
    return DATA_FILE.get_revit_ui_setting_data(("radio_bt_sync_monitor_never", False))

@ERROR_HANDLE.try_catch_error
def run_exe():

    if is_hate_sync_monitor():
        return

    exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\LAST_SYNC_MONITOR_2.4\\LAST_SYNC_MONITOR.exe"



    try:
        EXE.open_file_in_default_application(exe_location)
        return
    except Exception as e:
        pass
        #print (e)

    try:
        EXE.open_file_in_default_application(exe_location.replace(" - Shortcut", ""))
        return
    except Exception as e:
        pass
        #print (e)
################## main code below #####################
if __name__== "__main__":
    output = script.get_output()
    output.close_others()
    


