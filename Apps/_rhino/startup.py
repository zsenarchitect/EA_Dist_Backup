__title__ = "EnneadTab_Startup"
__doc__ = "The friendly welcome wagon for EnneadTab in Rhino! This startup script springs into action with each new Rhino session, quietly setting up your environment with all the EnneadTab goodness. It registers aliases, checks for updates, sets up event hooks, and ensures all your favorite tools are ready to use - so you can focus on creating amazing designs."
import os
import sys

_app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_lib_path = os.path.join(_app_folder, "lib" )
sys.path.append(_lib_path)

# print ("\n".join(sys.path))
from EnneadTab import ERROR_HANDLE, NOTIFICATION, ENVIRONMENT
from EnneadTab import VERSION_CONTROL, USER, EXE, CONFIG, DOCUMENTATION, HOLIDAY
from EnneadTab.RHINO import RHINO_ALIAS


import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
rs.AddSearchPath(_lib_path)

sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\{}.menu\\get_latest.button".format(ENVIRONMENT.PLUGIN_NAME))
import get_latest_left # pyright: ignore


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():

    
    get_latest_left.get_latest(is_silient = True)
    RHINO_ALIAS.register_alias_set()
    add_hook()

    rs.Command("{}_Activate{}".format(ENVIRONMENT.PLUGIN_ABBR, ENVIRONMENT.PLUGIN_NAME))
    RHINO_ALIAS.register_shortcut("F12", "{}_SearchCommand".format(ENVIRONMENT.PLUGIN_ABBR))
    
    NOTIFICATION.messenger(main_text = "Startup Script Completed")

    DOCUMENTATION.tip_of_day()

    HOLIDAY.festival_greeting()



    
@ERROR_HANDLE.try_catch_error(is_silent=True, is_pass=True)
def add_hook(): 

        
    # then add hook for future file in this session
    Rhino.RhinoDoc.CloseDocument += event_func_timesheet
    Rhino.RhinoDoc.EndOpenDocumentInitialViewUpdate  += event_func_handle_auto_start_command
    Rhino.RhinoDoc.EndOpenDocumentInitialViewUpdate  += event_func_timesheet


    Rhino.RhinoDoc.BeginSaveDocument += event_func_update_dist_repo

    
    Rhino.RhinoApp.Closing += event_func_update_r8_rui
###################################################
def action_update_timesheet(doc):
    if doc.Path:
        try:
            from EnneadTab import TIMESHEET
            TIMESHEET.update_timesheet(doc.Path)
        except:
            print ("Error updating timesheet")
            if USER.IS_DEVELOPER:
                print (ERROR_HANDLE.get_alternative_traceback())


##################################################

def event_func_handle_auto_start_command(sender, e):
    file_name = e.FileName
    if not file_name:        
        return


    if "{}_Revit2Rhino".format(ENVIRONMENT.PLUGIN_ABBR) in rs.DocumentName():
        rs.Command("!Zoom Extents")
        rs.Command("!- _Select None")


        
def event_func_timesheet(sender, e):
    action_update_timesheet(e.Document)

def event_func_update_dist_repo(sender, e):
    if CONFIG.get_setting("is_update_dist_repo_enabled", True):
        VERSION_CONTROL.update_dist_repo()

def event_func_update_r8_rui():
    EXE.try_open_app("Rhino8RuiUpdater", safe_open=True)


if __name__ == "__main__":
    main()