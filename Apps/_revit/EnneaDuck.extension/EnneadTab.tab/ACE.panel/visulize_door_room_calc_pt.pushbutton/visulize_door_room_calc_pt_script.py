#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Visualize door calculation points by drawing detail lines from To/From points to door insertion points. Blue lines for ToRoom, red lines for FromRoom. Works on selected views."
__title__ = "Door Calc\nPt Visualizer"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_GEOMETRY
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def visualize_door_cal_pts(doc):
    # Get selected views
    selected_views = forms.select_views(title="Select Views to Process", multiple=True)
    if not selected_views:
        print("No views selected. Operation cancelled.")
        return

    # Create line styles if they don't exist
    to_room_style = REVIT_SELECTION.get_linestyle(doc, "_internal_ToRoom", 
                                                 creation_data_if_not_exsit={"line_weight": 3, "color": (0, 0, 255)})
    from_room_style = REVIT_SELECTION.get_linestyle(doc, "_internal_FromRoom", 
                                                   creation_data_if_not_exsit={"line_weight": 3, "color": (255, 0, 0)})

    total_doors = 0
    doors_without_cal_pts = 0
    for view in selected_views:
        # Get all doors in current view
        doors = DB.FilteredElementCollector(doc, view.Id)\
                 .OfCategory(DB.BuiltInCategory.OST_Doors)\
                 .WhereElementIsNotElementType()\
                 .ToElements()
        
        if not doors:
            print("No doors found in view: {}".format(view.Name))
            continue

        t = DB.Transaction(doc, "{} - {}".format(__title__, view.Name))
        t.Start()
        
        for door in doors:
            # Check if door has calculation points
            if not door.HasSpatialElementFromToCalculationPoints:
                doors_without_cal_pts += 1
                continue
                
            # Get calculation points
            cal_pts = door.GetSpatialElementFromToCalculationPoints()
            if not cal_pts or len(cal_pts) != 2:
                doors_without_cal_pts += 1
                continue
                
            # Get door insertion point
            insert_pt = door.Location.Point
            
            # Project points onto view plane
            projected_insert_pt = REVIT_GEOMETRY.project_pt_in_view(insert_pt, view)
            
            # Create lines from calculation points to insertion point
            for i, pt in enumerate(cal_pts):
                projected_pt = REVIT_GEOMETRY.project_pt_in_view(pt, view)
                line = DB.Line.CreateBound(projected_pt, projected_insert_pt)
                try:
                    detail_line = doc.Create.NewDetailCurve(view, line)
                    # Set line style based on point index (0 = From, 1 = To)
                    detail_line.LineStyle = from_room_style if i == 0 else to_room_style
                except Exception as e:
                    print("Failed to create line for door {} in view {}: {}".format(
                        door.Id, view.Name, str(e)))
                    continue
        
        t.Commit()
        total_doors += len(doors)
        print("Visualized calculation points for {} doors in view: {}".format(len(doors), view.Name))
    
    print("\nTotal doors processed: {}".format(total_doors))
    if doors_without_cal_pts > 0:
        print("{} doors did not have calculation points and were skipped.".format(doors_without_cal_pts))

################## main code below #####################
if __name__ == "__main__":
    visualize_door_cal_pts(DOC)







