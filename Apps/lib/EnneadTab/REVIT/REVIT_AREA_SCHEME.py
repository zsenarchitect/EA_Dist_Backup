import ERROR_HANDLE
from Autodesk.Revit import DB # pyright:ignore
import REVIT_APPLICATION
UIDOC = REVIT_APPLICATION.get_uidoc() 
DOC = REVIT_APPLICATION.get_doc()

import REVIT_SELECTION

def get_area_by_scheme_name(scheme_name, doc=DOC, changable_only=False):
    """Retrieves areas belonging to a specific area scheme.
    
    Args:
        scheme_name (str): Name of the area scheme to filter by
        doc (Document): The Revit document to query. Defaults to active document
        changable_only (bool): If True, returns only editable areas. Defaults to False
        
    Returns:
        list: Collection of Area elements matching the specified scheme name
    """
    all_areas = DB.FilteredElementCollector(doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Areas)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
    if changable_only:
        all_areas = REVIT_SELECTION.filter_elements_changable(all_areas)
    return filter(lambda x: x.AreaScheme.Name == scheme_name, all_areas)



def get_area_scheme_by_name(scheme_name, doc=DOC):
    """Retrieves an area scheme by its name.
    
    Args:
        scheme_name (str): Name of the area scheme to find
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        AreaScheme: The matching area scheme element, or None if not found
    """
    area_schemes = DB.FilteredElementCollector(doc)\
            .OfCategory(DB.BuiltInCategory.OST_AreaSchemes)\
            .WhereElementIsNotElementType()\
            .ToElements()
    return next((x for x in area_schemes if x.Name == scheme_name), None)

