#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Pick your pill, then assign name from a list. Request by Gayatri"
__title__ = "Pick Name"

from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, NOTIFICATION, TEXT
from EnneadTab.REVIT import REVIT_SELECTION

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            
COLOR_SCHEME_NAME = "[Areas]: Department Category_Primary"      
            
@ERROR_HANDLE.try_catch_error()
def pick_name():
    selection_ids = uidoc.Selection.GetElementIds ()
    if len (selection_ids) == 0:
        NOTIFICATION.messenger(main_text = "Select one and only one pill shape")

        return 
    
    if len (selection_ids) != 1:
        NOTIFICATION.messenger(main_text = "Select one and only one pill shape")
        return
    
    element = doc.GetElement(selection_ids[0])
    if not REVIT_SELECTION.is_changable(element):
        NOTIFICATION.messenger(main_text = "You do not have permission to edit it.")
        return
    
    
    if not hasattr(element, "Symbol") or not element.Symbol.FamilyName.lower().startswith( "DTL_Healthcare_Planning_Section Bubble".lower()):
        NOTIFICATION.messenger(main_text = "This tool only work with the pill shape")
        return
    
    
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    def scheme_name(x):
        cate_name = DB.Category.GetCategory(doc, x.CategoryId).Name
        return "[{}]: {}".format(cate_name, x.Name)
    
    color_schemes = filter(lambda x: scheme_name(x) == COLOR_SCHEME_NAME, color_schemes)
    if len( color_schemes)== 0:
        NOTIFICATION.messenger(main_text = "Cannot find the color scheme [{}].\nMaybe you renamed your color scheme recently? Talk to SZ for update.".format(COLOR_SCHEME_NAME))
        return
    color_scheme = color_schemes[0]

    names = [entry.GetStringValue()  for entry in color_scheme.GetEntries()]
         
    name = forms.SelectFromList.show(sorted(names),
                                    multiselect=False)
    if not name:
        return
    # NOTIFICATION.messenger(main_text = name)
    name = TEXT.wrapped_text(name, max_len=20)
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    element.LookupParameter("bubble_diagram_label").Set(name)
    
    t.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    pick_name()
    










