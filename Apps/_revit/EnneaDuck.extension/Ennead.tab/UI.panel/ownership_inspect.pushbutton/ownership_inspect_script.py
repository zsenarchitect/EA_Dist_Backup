#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Element ownership detective that reveals who's controlling what in your model! This comprehensive scanner examines all categories of elements and reports which team members have ownership of various objects. Perfect for troubleshooting editing conflicts, identifying workset patterns, and understanding collaboration dynamics across your project."
__title__ = "Ownership\nInspect"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import forms, script


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def ownership_inspect(doc):

    output = script.get_output()
    all_elements = []
    
    # Get all BuiltInCategory enum values using System.Enum.GetValues
    import System # pyright: ignore 
    categories = list(System.Enum.GetValues(DB.BuiltInCategory))
    
    # Alternatively, you can select specific categories if needed
    # categories = [DB.BuiltInCategory.OST_Rooms, 
    #               DB.BuiltInCategory.OST_Areas, 
    #               DB.BuiltInCategory.OST_Walls, 
    #               DB.BuiltInCategory.OST_Columns, 
    #               DB.BuiltInCategory.OST_Floors, 
    #               DB.BuiltInCategory.OST_Roofs,
    #               DB.BuiltInCategory.OST_Views,
    #              ]
    
    for category in categories:
        try:
            all_elements.extend(list(DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()))
        except Exception as e:
            print ("Nothing found for category: {} with error: {}".format(category, e))

    for element in all_elements:
        owner = REVIT_SELECTION.get_owner(element)
        if owner == "":
            continue

        cate = element.Category.Name if hasattr(element, "Category") and element.Category else "Unknown Category"
        item_name = element.Name if hasattr(element, "Name") and element.Name else "Unknown Name"
        print ("[{}]{} is owned by {}".format(cate, output.linkify(element.Id, title=item_name), owner))











################## main code below #####################
if __name__ == "__main__":
    ownership_inspect(DOC)







