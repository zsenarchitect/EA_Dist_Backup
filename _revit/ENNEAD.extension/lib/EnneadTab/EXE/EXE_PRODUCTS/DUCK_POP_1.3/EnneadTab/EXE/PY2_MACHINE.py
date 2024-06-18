# -*- coding: utf-8 -*-



import os

PY_VERSION = 2

def secure_folder(path):


    if os.path.exists(path):
        return path
    os.makedirs(path)
    return path


def get_user_folder():

    return "{}\Documents".format(os.environ["USERPROFILE"])


def get_special_folder_in_EA_setting(folder_name):
    folder = get_EA_setting_folder() + "\{}".format(folder_name)
    return secure_folder(folder)


def get_EA_setting_folder():
    folder = get_user_folder() + "\EnneadTab Settings"
    return secure_folder(folder)

def get_EA_local_dump_folder():
    return get_special_folder_in_EA_setting("Local Copy Dump")

def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\{}".format(get_EA_local_dump_folder(), file_name)

def is_file_exist_in_dump_folder(file_name):
    return is_file_exist_in_folder(file_name, get_EA_local_dump_folder())


def is_file_exist_in_folder(check_file_name, folder):


    for file_name in os.listdir(folder):
        #ERROR_HANDLE.print_note(file_name)
        if check_file_name == file_name:
            return True
    return False

def read_json_as_dict(filepath, use_encode = False):
    import json
    import io
    if use_encode:
        with io.open(filepath, encoding='utf8') as f:
            data = json.load(f)
        return data

    else:
        with open(filepath,"r") as f:
            data = json.load(f)
        return data


def get_file_name_from_path(file_path):

    head, tail = os.path.split(file_path)
    return tail

def run_func_in_module(module_path, func_name):
    import imp
    module_name = get_file_name_from_path(module_path).replace(".py", "")
    ref_module = imp.load_source(module_name, module_path)
    func = getattr(ref_module, func_name)
    func()










def main(py_version):
    file_name = "PY{}_MACHINE_DATA.json".format(py_version)
    if not is_file_exist_in_dump_folder(file_name):
        return
    data_file = get_EA_dump_folder_file(file_name)
    data = read_json_as_dict(data_file)
    module_path = data["module_path"]
    func_name = data["func_name"]

    run_func_in_module(module_path, func_name)


#####################################################
if __name__ == "__main__":
    import traceback
    try:
        main(PY_VERSION)
    except:
        
        error = traceback.format_exc()

        error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
        error_file = "{}\error_log.txt".format(get_EA_local_dump_folder())
        with open(error_file, "w") as f:
            f.write(error)
        
        os.startfile(error_file)
    finally:
        print "Done"


    
