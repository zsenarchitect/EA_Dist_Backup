import os
import imp

import sys
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("{}\Source Codes\lib".format(parent_folder))
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)


def run_func_in_module(module_path, func_name, *args):
    """Run a specified function in a specified python file.

    Args:
        module_path (str): Path to the python file.
        func_name (str): Name of function to run.
        *args: Positional arguments to pass to the function.
    """
        
    module_name = EnneadTab.FOLDER.get_file_name_from_path(module_path).replace(".py", "")
    ref_module = imp.load_source(module_name, module_path)

    
    func = getattr(ref_module, func_name, None)
    if func is None:
        for surfix in ["_left", "_right"]:
            func = getattr(ref_module, func_name.replace(surfix, ""), None)
            if func is not None:
                break
        else:
            EnneadTab.NOTIFICATION.messenger(main_text="Oooops, cannot find the func <{}> in source code.\nContact SZ and let him know. Thx!".format(func_name))
            return

    @EnneadTab.ERROR_HANDLE.try_catch_error
    @EnneadTab.LOG.log(module_path, func_name)
    def runner(*args):
        func(*args)

    runner()



def run_Rhino_button(locator, *args):
    """Run a specified function in a specified file, for use with Rhino buttons.

    Args:
        folder (str): The folder name for the button script, in EnneadTab sources codes folder.
        file_name (str): The file name for the button script, without the .py extension.
        func_name (str): The function name to run in the button script. To run entire script, use "file_name".
        *args: Positional arguments to pass to the function.
    """

    # do this from..import to remove any dependecy that first time run it from Rhino button
    # try:
    #     from ENVIRONMENT import get_EnneadTab_For_Rhino_root
    # except Exception as e:
    #     print e
    #     return

    root = EnneadTab.ENVIRONMENT.get_EnneadTab_For_Rhino_root()
    module_path = "{}\\Toolbar\\{}".format(root, locator)
    
    # add the folder of the module to the system path for referencing additional modules
    module_folder = os.path.dirname(module_path)
    if module_folder not in sys.path:
        sys.path.append(module_folder)

    head, tail = os.path.split(module_path)
    func_name = tail.replace(".py", "")
    run_func_in_module(module_path, func_name, *args)