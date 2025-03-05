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
    area_schemes = get_all_area_schemes(doc)
    return next((x for x in area_schemes if x.Name == scheme_name), None)


def get_all_area_schemes(doc=DOC):
    """Retrieves all area schemes in the document.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        list: Collection of AreaScheme elements in the document
    """
    return list(DB.FilteredElementCollector(doc)\
            .OfCategory(DB.BuiltInCategory.OST_AreaSchemes)\
            .WhereElementIsNotElementType()\
            .ToElements())

def pick_area_scheme(doc=DOC):
    """Picks an area scheme from the document.
    
    Args:
        doc (Document): The Revit document to query. Defaults to active document
        
    Returns:
        AreaScheme: The selected area scheme element, or None if no element is selected
    """
    from pyrevit import forms
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item.Name
    selected_element = forms.SelectFromList.show([MyOption(x) for x in get_all_area_schemes(doc)],
                                              multiselect=False,
                                              width=500,
                                              title="Pick Area Scheme",
                                              button_name='Select Area Scheme')
    return selected_element