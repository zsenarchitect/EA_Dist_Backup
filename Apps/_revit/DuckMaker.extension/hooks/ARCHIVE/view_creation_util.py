
from pyrevit import  EXEC_PARAMS
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import DATA_FILE
from Autodesk.Revit import DB # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 


def mark_current_view_collection(doc):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    data = {
        "all_views": [x.Id.IntegerValue for x in all_views]
    }
    DATA_FILE.set_data(data, "all_current_views")