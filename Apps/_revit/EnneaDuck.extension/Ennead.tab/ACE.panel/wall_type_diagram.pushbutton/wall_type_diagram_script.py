#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Wall Type\nDiagram"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import traceback
from pyrevit import forms
from EnneadTab import DATA_CONVERSION, ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
import random

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def add_wall_type_box_and_text(doc, legend_view, walltypes_selected):
    cursor_x = 0
    cursor_y = 0
    color_dict = {}
    walltypes_selected.sort(key = lambda x: x.LookupParameter("Keynote").AsString(), reverse = True)
    for walltype in walltypes_selected:
        edge = 3
        wall_type_name = walltype.LookupParameter("Type Name").AsString()
        region_type_name = "EnneadTab_WallType_{}".format(wall_type_name)
        filled_region_type = REVIT_SELECTION.get_filledregion_type(doc, region_type_name, color_if_not_exist = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        pt0 = DB.XYZ(cursor_x, cursor_y, 0)
        pt1 = DB.XYZ(cursor_x + edge, cursor_y, 0)   
        pt2 = DB.XYZ(cursor_x + edge, cursor_y + edge, 0)
        pt3 = DB.XYZ(cursor_x, cursor_y + edge, 0)
        curveloop = DB.CurveLoop()
        curveloop.Append(DB.Line.CreateBound(pt0, pt1))
        curveloop.Append(DB.Line.CreateBound(pt1, pt2))
        curveloop.Append(DB.Line.CreateBound(pt2, pt3))
        curveloop.Append(DB.Line.CreateBound(pt3, pt0))
        curveloop = DATA_CONVERSION.list_to_system_list([curveloop], type = "CurveLoop")
        DB.FilledRegion.Create(doc, 
                            filled_region_type.Id,
                            legend_view.Id,
                            curveloop)
        color_dict[wall_type_name] = filled_region_type.ForegroundPatternColor



        key_note = walltype.LookupParameter("Keynote").AsString()
        text_note_type_id = doc.GetDefaultElementTypeId(DB.ElementTypeGroup.TextNoteType)
        DB.TextNote.Create(doc,
                       legend_view.Id,
                       DB.XYZ(cursor_x + edge*1.2 , cursor_y + edge*1.2 , 0),
                       key_note,
                       text_note_type_id
                      )
        cursor_y += edge*1.2
    return color_dict



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def wall_type_diagram(doc):
    walltypes_selected = REVIT_SELECTION.pick_system_types(doc, "wall")
    if not walltypes_selected:
        return

    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # create a legenda view
    legend_view = REVIT_VIEW.create_legend_view(doc, "Wall Type Diagram", scale = 100)

    # and add box and text per wall type
    try:
        color_dict = add_wall_type_box_and_text(doc, legend_view, walltypes_selected)
    except:
        t.RollBack()
        print (traceback.format_exc())

    # add filter to project by wall type

    # add filters to diagram template and apply color to each wall type


    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    wall_type_diagram(DOC)







