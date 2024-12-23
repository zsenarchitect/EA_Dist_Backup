import ERROR_HANDLE
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



def get_area_scheme_by_name(scheme_name, doc = DOC):
    area_schemes = DB.FilteredElementCollector(doc)\
            .OfCategory(DB.BuiltInCategory.OST_AreaSchemes)\
            .WhereElementIsNotElementType()\
            .ToElements()
    return next((x for x in area_schemes if x.Name == scheme_name), None)

