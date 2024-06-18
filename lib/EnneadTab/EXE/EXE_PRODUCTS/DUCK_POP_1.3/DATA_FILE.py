#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import json
except:
    pass
import io
import FOLDER

import USER

def read_json_file_safely(filepath, use_encode = False):
    """dup json file then read it to avoid holding the file open status

    Args:
        filepath (_type_): _description_

    Returns:
        dict | None: the content of the json file
    """
    local_path = FOLDER.get_EA_dump_folder_file("temp.json")
    import shutil
    shutil.copyfile(filepath, local_path)
    #print "###"
    #print local_path
    content = read_json_as_dict(local_path, use_encode)
    return content


def read_json_as_dict(filepath, use_encode = False):
    """get the data saved in json as dict

    Args:
        filepath (_type_): _description_
        use_encode (bool, optional): for Chinese char file it might need encoding. Defaults to False.

    Returns:
        dict | None: _description_
    """
    try:
        if use_encode:
            with io.open(filepath, encoding='utf8') as f:
                data = json.load(f)
            return data

        else:
            with open(filepath,"r") as f:
                data = json.load(f)
            return data
    except Exception as e:
        print (e)
        return None

def read_json_as_dict_in_dump_folder(file_name, use_encode = False): 
    """direct access the json file from dump folder

    Args:
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return read_json_as_dict(filepath, use_encode=use_encode)

def save_dict_to_json(dict, filepath, use_encode = False):
    """store the python dict to json at path

    Args:
        dict (_type_): _description_
        filepath (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    try:
        if use_encode:
            with io.open(filepath, 'w', encoding='utf-8') as f:
                # Serialize the data and write it to the file
                json.dump(dict, f, ensure_ascii=False)
            return True

        else:
            with open(filepath,"w") as f:
                json.dump(dict, f)
            return True
    except:
        return False

def save_dict_to_json_in_dump_folder(dict, file_name, use_encode = False): 
    """direct store dict to a file in dump folder

    Args:
        dict (_type_): _description_
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return save_dict_to_json(dict, filepath, use_encode=use_encode)


def pretty_print_dict(dict):
    """format print the content of dict or json

    Args:
        dict (_type_): _description_
    """
    string = json.dumps(dict,indent=4)
    print (string)



def read_txt_file_safely(filepath):
    extention = FOLDER.get_file_extension_from_path(filepath)
    local_path = FOLDER.get_EA_dump_folder_file("temp{}".format(extention))
    #print (filepath)
    #print (local_path)
    import shutil
    shutil.copyfile(filepath, local_path)
    #print "###"
    content = read_txt_as_list(local_path)
    return content

def read_txt_as_list(filepath = "path", use_encode = False):
    if use_encode:

        with io.open(filepath, encoding = "utf8") as f:
            lines = f.readlines()
    else:
        with open(filepath) as f: #encoding = "utf8"
            lines = f.readlines()
    return map(lambda x: x.replace("\n",""), lines)


def save_list_to_txt(list, filepath, end_with_new_line = False, use_encode = False):
    if use_encode:

        with io.open(filepath, "w", encoding = "utf8") as f:
            f.write('\n'.join(list))
            if end_with_new_line:
                f.write("\n")
    else:
        with open(filepath, 'w') as f:
            # f.writelines(list)
            f.write('\n'.join(list))
            if end_with_new_line:
                f.write("\n")



def get_sticky_longterm(sticky_name, default_value_if_no_sticky = None):
    """get longterm sticky information

    Args:
        sticky_name (str): name of the sticky
        default_value_if_no_sticky (_type_, optional): _description_. Defaults to None.

    Returns:
        any : get the value of the longterm sticky
    """
    file = get_longterm_sticky_file()
    data = read_json_file_safely(file)
    if sticky_name not in data.keys():
        set_sticky_longterm(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    return data[sticky_name]

def set_sticky_longterm(sticky_name, value_to_write):
    """set a long term sticky. The long term sticky will not be cleared after the application is closed.

    Args:
        sticky_name (str): _description_
        value_to_write (any): value to write
    """
    file = get_longterm_sticky_file()
    data = read_json_file_safely(file)
    data[sticky_name] = value_to_write
    save_dict_to_json(data, file)


def get_longterm_sticky_file():
    file_name = "longterm_sticky.STICKY"
    file = FOLDER.get_EA_dump_folder_file(file_name)
    if not FOLDER.is_file_exist_in_folder(file_name, FOLDER.get_EA_local_dump_folder()):
        save_dict_to_json(dict(), file)
        
        # add a sleeping time to avoid writing file  and read file to quickly
        import time
        time.sleep(1)
    return file



def get_revit_user_file(name = None):
    """get the revit user data file stored.

    Args:
        name (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if not name:
        name = USER.get_user_name()

    folder = FOLDER.get_revit_user_folder()
    #folder = FOLDER.secure_folder(folder)

    return "{}\{}.json".format(folder, name)



def get_revit_ui_setting_file():
    """this is the ui setting file for EnneadTab Revit stored in each user local computer

    Returns:
        _type_: _description_
    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        setting_file = FOLDER.get_EA_dump_folder_file(file_name)
        save_dict_to_json(dict(), setting_file) 


    return FOLDER.get_EA_dump_folder_file(file_name)


def get_revit_ui_setting_data(key_defaule_value = None):
    """if no key provided, will return the whole dict
        otherwise, return the value of this key, default value 
        
        key_defaule_value: (key, default value), a tuple of default result, this is used to get the key of value looking for. If do not provide this tuple, then return the raw while data"""
    setting_file = get_revit_ui_setting_file()
    data = read_json_as_dict(setting_file)


    if not key_defaule_value:
        return data
    key, defaule_value = key_defaule_value
    return data.get(key, defaule_value)

def set_revit_ui_setting_data(key, value):
    """set the key and value to the revit ui setting

    Args:
        key (_type_): _description_
        value (_type_): _description_
    """
    setting_file = get_revit_ui_setting_file()
    data = read_json_as_dict(setting_file)
    data[key] = value
    save_dict_to_json(data, setting_file)
    
    

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")