#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Duplicate\nArea Scheme"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_AREA_SCHEME
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import forms
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def duplicate_area_scheme(doc):

    t = DB.Transaction(doc, __title__)
    t.Start()
    pass

    #pick area scheme to duplicate
    original_area_scheme = REVIT_SELECTION.pick_area_scheme(doc)


    # get a new name for the new area scheme, cannot be same as other area schemes
    new_name = forms.ask_for_unique_string(title="New Area Scheme Name",
                                           reserved_values=[x.Name for x in REVIT_AREA_SCHEME.get_all_area_schemes(doc)],
                                           default=original_area_scheme.Name + "_copy")

    # copy this area scheme
    newElemIds = DB.ElementTransformUtils.CopyElement(doc, original_area_scheme.Id, DB.XYZ.Zero)
    new_area_scheme = doc.GetElement(newElemIds[0])
    new_area_scheme.Name = new_name

    # get all the views that use original area scheme, if genLevel is already used then ignore. we only need one view from each genLevel
    all_areas = REVIT_AREA_SCHEME.get_area_by_scheme_name(original_area_scheme.Name, doc)
    level_dict = {}
    for area in all_areas:
        if area.GenLevel not in level_dict:
            level_dict[area.GenLevel] = []
        level_dict[area.GenLevel].append(area)
    

    # for each view's genLevel, create a new view with the new area scheme, then transfer the boundarys and areas into the new view
    for genLevel, areas in level_dict.items():
        # create a new view with the new area scheme
        new_area_plan_view = DB.ViewPlan.CreateAreaPlan(doc, new_area_scheme.Id, genLevel.Id)


    
    
    

    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    duplicate_area_scheme(DOC)







