#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
TO-DO
consider preparing for cpyhthon func in rhino 8.
pyrevit also support cpyhthon but might not be as new as rhino8

this allow direct run of openai, pygame , matploylib,panda, and other modern py3 lib
""" 


import os

for module in os.listdir(os.path.dirname(__file__)):

    if module == '__init__.py':
        continue
    

    if module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as e:
        # print (e)
        # print ("Cannot import {}".format(module))
        pass
del module# delete this varible becaue it is refering to last item on the for loop#!/usr/bin/python

# parent_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# print (parent_folder)
# sys.path.append(parent_folder)
# import USER
# this is abadoned becasue a circular reference


def open_exe(exe_name, use_shortcut = False):
    """direct run exe from L drive

    Args:
        exe_name (str): name of the exe file
        use_shortcut (bool, optional): append shortcut to run to get the shortcut version. Defaults to True.
    """
    exe_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe"
    exe_path = exe_folder + "\\" + exe_name +"\\" + exe_name + ".exe"
    if use_shortcut:
        exe_path += " - Shortcut"
        if not os.path.exists(exe_path):
            print ("Not short-cut found")
            exe_path = exe_path.split(" - Shortcut")[0]

    os.startfile(exe_path)

def open_file_in_default_application(filepath):
    """direct  run path file

    Args:
        filepath (str): path of the application or file
    """

    #subprocess.call('C:\Program Files\Rhino 7\System\Rhino.exe')

    
    if not os.path.exists(filepath):
        if os.environ["USERPROFILE"].split("\\")[-1] == "szhang":
            print ("[SZ only log]File not found: {}".format(filepath))
        return
    os.startfile(filepath)



def call_py_machine(script_path, func_name, version = 2):
    #import os, sys

    #root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #sys.path.append(root_folder)

    from EnneadTab import FOLDER, DATA_FILE

    file_name = "PY{}_MACHINE_DATA.json".format(version)
    data_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = dict()
    data["module_path"] = script_path
    data["func_name"] = func_name
    DATA_FILE.save_dict_to_json(data, data_file)


    exe_location = get_py_machine_location(version)
    #print (exe_location)
    open_file_in_default_application(exe_location)


def get_py_machine_location(version):
    exe_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe"
    return "{0}\PY{1}_MACHINE\PY{1}_MACHINE.exe - Shortcut".format(exe_folder, version)






###################
if __name__ == "__main__":
    print ("{} is ok".format(__file__))