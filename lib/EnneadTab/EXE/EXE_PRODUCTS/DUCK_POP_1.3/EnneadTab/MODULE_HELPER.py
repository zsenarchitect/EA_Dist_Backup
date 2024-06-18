#!/usr/bin/python
# -*- coding: utf-8 -*-


import imp
import FOLDER
import ENVIRONMENT
import ERROR_HANDLE

#@ERROR_HANDLE.try_catch_error
def run_func_in_module(module_path, func_name):
    """run specific func in specific python file

    Args:
        module_path (str): path to the python file
        func_name (str): name of func to run
    """
    module_name = FOLDER.get_file_name_from_path(module_path).replace(".py", "")
    ref_module = imp.load_source(module_name, module_path)
    func = getattr(ref_module, func_name)
    func()


def run_Rhino_button(folder, file_name, func_name ):
    """run rhino button

    Args:
        folder (_type_): _description_
        file_name (_type_): _description_
        func_name (_type_): _description_
    """

    # do this from..import to remove any dependecy that first time run it from Rhino button
    # try:
    #     from ENVIRONMENT import get_EnneadTab_For_Rhino_root
    # except Exception as e:
    #     print e
    #     return

    root = ENVIRONMENT.get_EnneadTab_For_Rhino_root()
    module_path = "{}\Source Codes\{}\{}.py".format(root, folder, file_name)

    run_func_in_module(module_path, func_name)
