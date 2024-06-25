"""Please note that, for developer, the python script will come from your local repo folder, 
this is to help you debug features without constantly uploading to L drive and potnetially
disturb other people's working file.

Only need to publish when you are ready.
"""

import os
import imp
import sys
import traceback
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))

sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


if os.path.exists(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO):
    repo_folder = EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO
else:
    repo_folder = EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO
ScriptPath = "{}\\Source Codes\\Grasshopper\\GH_python\\Lenox\\{}".format(repo_folder,
                                                                          ScriptName)
parent_folder = os.path.dirname(ScriptPath)



# Add the directory containing your script to the Python path
sys.path.append(parent_folder)


# script file name
file_module_name = os.path.basename(ScriptPath).split(".py")[0]




try:
    module = imp.load_source(file_module_name, ScriptPath)


    HelpDoc = module.__doc__
    ExceptionDoc = "<{}> has no error when loading.".format(file_module_name)
except Exception as e:
    ExceptionDoc = traceback.format_exc()
    HelpDoc = "Help Document is suspended until the main warning is fixed."

# print HelpDoc
if "IsEnabled" not in globals():
    globals()["IsEnabled"] = True
    
if IsEnabled:
    EnneadTab.NOTIFICATION.messenger(main_text = "Script <{}> is loaded".format(file_module_name))
else:
    EnneadTab.NOTIFICATION.messenger(main_text = "Script <{}> is loaded but NOT enabled".format(file_module_name))
    ScriptPath = None
    ExceptionDoc += "\n\nIt is currently DISABLED!"
    