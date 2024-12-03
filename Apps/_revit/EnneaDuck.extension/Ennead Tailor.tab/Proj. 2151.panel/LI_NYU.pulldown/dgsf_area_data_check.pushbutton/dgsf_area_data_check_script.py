#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "DGSF Area Data Check"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_AREA_SCHEME
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()
MARKER_NOTE = "_DO NOT FILL"

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dgsf_area_data_check(doc):
    pass


    t = DB.Transaction(doc, __title__)
    t.Start()
    all_areas = REVIT_AREA_SCHEME.get_area_by_scheme_name("DGSF Scheme", DOC, changable_only = True)
    for area in all_areas:

        if not area.LookupParameter("Name").HasValue:
            area.LookupParameter("Name").Set(MARKER_NOTE)
        if MARKER_NOTE not in area.LookupParameter("Name").AsValueString():
            name = area.LookupParameter("Name").AsValueString()
            area.LookupParameter("Name").Set(MARKER_NOTE + "_" + name)

    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    dgsf_area_data_check(DOC)







