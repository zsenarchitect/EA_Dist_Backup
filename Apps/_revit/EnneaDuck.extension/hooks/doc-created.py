
from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars
from pyrevit import script

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ENVIRONMENT, MODULE_HELPER, ERROR_HANDLE


@ERROR_HANDLE.try_catch_error(is_silent=True)
def proj_initiation():
    output = script.get_output()
    if ENVIRONMENT.is_RhinoInsideRevit_environment():
        output.close()
        return

    
    try:
        doc = EXEC_PARAMS.event_args.Document
    except:
        output.close()
        return


    if doc is None:
        output.close()
        return

    if doc.IsFamilyDocument:
        output.close()
        return
    
    
    folder = "Ennead.tab\\ACE.panel\\Project Starter.pushbutton\\project_starter_script.py"
    func_name = "project_starter"

    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    
    
    
if __name__ == "__main__":
    proj_initiation()