#!/usr/bin/python
# -*- coding: utf-8 -*-
import ENVIRONMENT
import EXE
import DATA_FILE
import FOLDER
import NOTIFICATION
import os


UNICODE_VARIABLE_KEY = "UNICODE_STR"
UNICODE_READY_KEY = UNICODE_VARIABLE_KEY + "_READY"
UNICODE_DATA_FILE = "UNICODE_DATA.json"

def convert_unicode_to_string(unicode_string):
    data = {}
    data["input_text"] = unicode_string
    data["is_ready"] = False
    DATA_FILE.save_dict_to_json_in_dump_folder(data, UNICODE_DATA_FILE, use_encode=True)
    run_exe()
    from time import sleep
    max_attemp = 100
    attempt = 0
    source = FOLDER.get_EA_dump_folder_file(UNICODE_DATA_FILE)
    while True:
        if attempt > max_attemp:
            NOTIFICATION.messager(main_text="Cannot convert unicode to string----C!!!")
            return unicode_string
        data = DATA_FILE.read_json_file_safely(source,use_encode=True)
        if not data.get("is_ready", False):
            attempt += 1
            sleep(0.1)
            continue
        NOTIFICATION.messager(main_text="Convertion done!!!!")
        return  data.get("output_text", None)
     
    
    return
    
    
    
    ENVIRONMENT.set_environment_variable_from_iron_python(UNICODE_VARIABLE_KEY, unicode_string)
    ENVIRONMENT.set_environment_variable_from_iron_python(UNICODE_READY_KEY, False)
    run_exe()
    from time import sleep
    max_attemp = 100
    attempt = 0
    while True:
        if attempt > max_attemp:
            return unicode_string
        if not ENVIRONMENT.get_environment_variable(UNICODE_READY_KEY):
            attempt += 1
            sleep(0.1)
            continue
        print (999999999999999999)
        return  ENVIRONMENT.get_environment_variable(UNICODE_VARIABLE_KEY) 
     
    

    
def run_exe():
    exe_name = "UNICODE"
    exe_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe"
    exe_path = exe_folder + "\\" + exe_name +"\\" + exe_name + ".exe"

    
    os.startfile(exe_path)


def action_converter():
    """this MUST run as PY3
    """
    from time import sleep
    max_attemp = 100
    attempt = 0
    while True:
        if attempt > max_attemp:
            NOTIFICATION.messager(main_text="Convertion data saved done--A!!!!")
            return
        data = DATA_FILE.read_json_as_dict_in_dump_folder(UNICODE_DATA_FILE,use_encode=True)
        if not data:
            attempt += 1
            sleep(0.15)
            continue
        break
    converted = data.get("input_text", None)
    if  converted:
        converted = converted.encode('utf-8')
    data["is_ready"] = True
    data["output_text"] = converted
    NOTIFICATION.messager(main_text="Convertion data saved done---B!!!!")
    DATA_FILE.save_dict_to_json_in_dump_folder(data, UNICODE_DATA_FILE, use_encode=True)
    
    
    
    return
    try:
        unicode_string = ENVIRONMENT.get_environment_variable(UNICODE_VARIABLE_KEY)
    except KeyError:
        print("UNICODE_STR is not set!")
        return
    converted = unicode_string.encode('utf-8')
    print (converted)
    ENVIRONMENT.set_environment_variable(UNICODE_VARIABLE_KEY, converted)
    ENVIRONMENT.set_environment_variable(UNICODE_READY_KEY, True)
    


if __name__ == "__main__":
    print(__file__ + "   -----OK!")
    #unicode_string = u'\u8fd0\u8425\u6b66\u6c49\u4e1a\u52a1\u4e2d\u5fc3'
    # print (unicode_string)
    # print (unicode_string.encode('utf-8'))
    #convert_unicode_to_string(unicode_string)
    # action_converter()