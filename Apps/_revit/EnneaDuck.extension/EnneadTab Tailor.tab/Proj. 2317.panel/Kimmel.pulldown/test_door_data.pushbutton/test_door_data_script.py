#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Door Data"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def test_door_data(doc):

    all_doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    for door in all_doors:
        is_good = False
        for para in door.GetParameters("Fire Rating"):
            if para.AsValueString() in ["uu", "ST"]:
                is_good = True
        if is_good:
            for para in door.GetParameters("Fire Rating"):
                print(para.Definition.Id)
                print(para.Id)
                print(para.AsValueString())
    # t = DB.Transaction(doc, __title__)
    # t.Start()
    # pass
    # t.Commit()



################## main code below #####################
if __name__ == "__main__":
    test_door_data(DOC)







