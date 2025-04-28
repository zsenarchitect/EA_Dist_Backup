#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Update Dr Style Name"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_dr_style_name(doc):
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # Get all door instances using FamilyInstance with category filter
    door_collector = DB.FilteredElementCollector(doc)
    door_collector.OfCategory(DB.BuiltInCategory.OST_Doors)
    door_collector.WhereElementIsNotElementType()
    all_doors = door_collector.ToElements()
    
    for door in all_doors:
        current_door_style = door.LookupParameter("Door Style").AsValueString()
        if current_door_style:
            print(current_door_style)
            door.LookupParameter("_internal_note").Set(current_door_style)
    
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    update_dr_style_name(DOC)







