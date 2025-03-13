#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Line usage analysis tool that helps identify views with excessive detail and model lines. This diagnostic utility generates a ranked report of views containing the most line elements, helping pinpoint potential performance bottlenecks or documentation management issues. Perfect for troubleshooting slow performance or when establishing documentation standards for line usage."
__title__ = "Lines-In-View\nLocator"
__tip__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()
from collections import defaultdict

from pyrevit import script
output = script.get_output()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def lines_in_view_locator():
    process_line_type()



def process_line_type():
    output.print_md("\n\n## LINE COUNT IN CURRENT DOCUMENT: "+ DOC.Title+"\n")
    output.print_md("\n___\n")

    detail_lines = defaultdict(int)
    model_lines = defaultdict(int)
    detail_table_data = []
    model_table_data = []
    workset_table = DOC.GetWorksetTable()
    lines = DB.FilteredElementCollector(DOC).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
    for line in lines:
        if line.CurveElementType.ToString() == "DetailCurve":
            view_id_int = line.OwnerViewId.IntegerValue
            detail_lines[view_id_int] += 1
        if line.CurveElementType.ToString() == "ModelCurve":
            workset_id_int = line.WorksetId.IntegerValue
            model_lines[workset_id_int] += 1

    # print detail line table    
    for line_count, view_id_int in sorted(zip(detail_lines.values(), detail_lines.keys()),
                                            reverse=True):
        view_id = DB.ElementId(view_id_int)
        view_creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(DOC,view_id).Creator
        try:
            view_name = DOC.GetElement(view_id).Name
        except Exception:
            view_name = "<no view name available>"
        detail_table_data.append([line_count,  output.linkify(view_id, title = view_name), view_creator])
    detail_table_data.append([str(sum(detail_lines.values()))+" Detail Lines in Total","In "+str(len(detail_lines))+" Views",  ""])
    output.print_table(detail_table_data,columns=["Count", 'ViewName', 'ViewCreator'], last_line_style='font-weight:bold;font-size:1.2em;')

    print ("\n\n")
    output.print_md("\n___\n")
    print ("\n\n")

    # print model line table
    for line_count, workset_id_int in sorted(zip(model_lines.values(), model_lines.keys()),
                                            reverse=True):
        
        workset_name = workset_table.GetWorkset(DB.WorksetId(workset_id_int)).Name
        model_table_data.append([line_count, workset_name])
    model_table_data.append([str(sum(model_lines.values()))+" Model Lines in Total","",  ""])    
    output.print_table(model_table_data,columns=["Count", 'Workset'], last_line_style='font-weight:bold;font-size:1.2em;')
        

################## main code below #####################
if __name__ == "__main__":
    lines_in_view_locator()







