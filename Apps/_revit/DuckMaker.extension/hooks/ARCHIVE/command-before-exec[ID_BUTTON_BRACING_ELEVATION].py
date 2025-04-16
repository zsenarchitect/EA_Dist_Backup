from pyrevit import  EXEC_PARAMS
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from view_creation_util import mark_current_view_collection



if __name__ == "__main__":
    mark_current_view_collection(doc)





