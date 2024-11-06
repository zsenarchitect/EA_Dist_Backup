
from Autodesk.Revit import DB # pyright:ignore
import REVIT_APPLICATION
UIDOC = REVIT_APPLICATION.get_uidoc() 
DOC = REVIT_APPLICATION.get_doc()

import REVIT_SELECTION

def get_area_by_scheme_name(scheme_name, doc = DOC,changable_only = False):
        all_areas = DB.FilteredElementCollector(doc)\
                        .OfCategory(DB.BuiltInCategory.OST_Areas)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
        if changable_only:
            all_areas = REVIT_SELECTION.filter_elements_changable(all_areas)
        return filter(lambda x: x.AreaScheme.Name == scheme_name, all_areas)

