
from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ENVIRONMENT, MODULE_HELPER, ERROR_HANDLE


@ERROR_HANDLE.try_catch_error(is_silent=True)
def proj_initiation():
    if ENVIRONMENT.is_RhinoInsideRevit_environment():
        return

    
    try:
        doc = EXEC_PARAMS.event_args.Document
    except:
        return


    if doc is None:
        return

    if doc.IsFamilyDocument:
        return
    
    
    folder = "Ennead.tab\\ACE.panel\\Project Starter.pushbutton\\project_starter_script.py"
    func_name = "project_starter"

    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    
    
    
if __name__ == "__main__":
    proj_initiation()