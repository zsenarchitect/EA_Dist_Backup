#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Area Scheme Data Transfer"

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
def area_scheme_data_transfer():


    t = DB.Transaction(DOC, __title__)
    t.Start()


    
    all_areas = REVIT_AREA_SCHEME.get_area_by_scheme_name("DGSF Scheme", DOC)
    for area in all_areas:

        name = area.LookupParameter("Name").AsValueString()
        program_type = area.LookupParameter("Area_$Department_Program Type").AsValueString()
        if name == MARKER_NOTE:
            continue

        if program_type == "" or program_type == name or not area.LookupParameter("Area_$Department_Program Type").HasValue:
            area.LookupParameter("Area_$Department_Program Type").Set(name)
            area.LookupParameter("Name").Set(MARKER_NOTE)

        # name = MARKER_NOTE + "_" + name
        # area.LookupParameter("Name").Set(name)

    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    area_scheme_data_transfer()







