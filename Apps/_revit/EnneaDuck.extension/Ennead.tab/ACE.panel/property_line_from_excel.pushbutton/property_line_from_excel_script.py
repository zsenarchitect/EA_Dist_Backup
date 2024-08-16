#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Generate detail line from the Excel survey pt data. Best used for property line geneation."
__title__ = "Property Line From Excel"
import os

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, EXCEL, TIME, DATA_CONVERSION, FOLDER, DATA_FILE

from pyrevit import forms
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS, REVIT_GEOMETRY, REVIT_UNIT, REVIT_GEOMETRY
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def property_line_from_excel():
    opts = [
        "Pick excel and generate",
        "Get a sample excel"
    ]
    res = REVIT_FORMS.dialogue(main_text="Use excel survey coordinate to generat3e detail lines group that looks like property line.",
                               options = opts)
    if res == opts[0]:
        generate_property_line()
    elif res == opts[1]:
        open_sample_excel()


def open_sample_excel():
    tool_folder = os.path.dirname(os.path.abspath(__file__))
    sample_excel = os.path.join(tool_folder, "Sample Survey Data.xsl")
    safe_copy = FOLDER.copy_file_to_local_dump_folder(sample_excel)
    os.startfile(safe_copy)
    pass


def generate_property_line():
    excel = forms.pick_excel_file()
    if not excel:
        return
    if excel.endswith(".xlsx"):
        NOTIFICATION.messenger("Please save your excel as .xls for max compatiablity")
        return

    lines = EXCEL.read_data_from_excel(excel)

 
    
    pts = [DB.XYZ(REVIT_UNIT.m_to_internal(float(line[1][2:])), 
                  REVIT_UNIT.m_to_internal(float(line[2][2:])), 
                  0) 
           for line in lines]

    t = DB.Transaction(DOC, __title__)
    t.Start()
    print (pts[:2])
    pts = [REVIT_GEOMETRY.transform_survey_pt_to_internal_pt(DOC, pt) for pt in pts]
    print (pts[:2])


    # pts.append(pts[0]) # the excel alloready make a seconda record of pt for the loop

    detail_line_ids = []
    for i in range(len(pts)-1):
        # print (pts[i].DistanceTo (pts[i+1]))
        if pts[i].DistanceTo (pts[i+1]) < 0.0001:
            print ("Weird data, too close")
            continue
        # print ("Making")
        line = DB.Line.CreateBound(pts[i], pts[i+1])
        detail_line_ids.append(DOC.Create.NewDetailCurve(DOC.ActiveView, line).Id)

    group = DOC.Create.NewGroup(DATA_CONVERSION.list_to_system_list(detail_line_ids))

    group.GroupType.Name = "EA_PropertyLineMaker_({}_{})".format(DOC.ActiveView.Name,
                                                                        TIME.get_formatted_current_time())
    t.Commit()




################## main code below #####################
if __name__ == "__main__":
    property_line_from_excel()







