#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Automates the tedious task of joining columns and floors throughout your model. This time-saving utility identifies all column and floor elements and applies join geometry operations between them, providing a detailed completion report of successful and failed joins."
__title__ = "Join All Column/Floor"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def join_all_coln_floor(doc):
    


    t = DB.Transaction(doc, __title__)
    t.Start()

    all_columns = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
    all_floors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()

    join_count = 0
    fail_count = 0
    for column in all_columns:
        for floor in all_floors:
            try:
                DB.JoinGeometryUtils.JoinGeometry(doc, column, floor)
                join_count += 1
            except Exception as e:
                fail_count += 1
                
    NOTIFICATION.messenger("Joined {} column/floor pairs, failed {}\nTotal: {}".format(join_count, 
                                                                                       fail_count, 
                                                                                       join_count + fail_count))
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    join_all_coln_floor(DOC)







