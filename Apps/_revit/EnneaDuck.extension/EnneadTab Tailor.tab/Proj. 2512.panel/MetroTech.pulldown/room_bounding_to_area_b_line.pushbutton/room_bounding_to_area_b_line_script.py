#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Creates area boundary lines from room boundaries in selected Area Plan views.

The tool processes each selected Area Plan view, finds all rooms on the associated level,
and creates area boundary lines based on the room boundaries. The newly created area
boundary lines are grouped by view for easier management."""
__title__ = "Room Bounding To Area Boundary Lines"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
from System.Collections.Generic import List # pyright: ignore

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import forms


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def room_bounding_to_area_b_line(doc):
    # Get selected views
    processed_levels = set()
    def filter_area_plan_views(x):
        if x.ViewType != DB.ViewType.AreaPlan:
            return False
        if x.GenLevel in processed_levels:
            return False
        processed_levels.add(x.GenLevel)
        return True
    
    selected_views = forms.select_views(title = "Select Area Plan Views", multiple = True, filterfunc = filter_area_plan_views)
    
  
        
    if not selected_views:
        ERROR_HANDLE.print_note("None of the selected views are Area Plan views.")
        return
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    for view in selected_views:
        
        
        level = doc.GetElement(view.GenLevel.Id)
        
        # Get all rooms on this level
        room_collector = DB.FilteredElementCollector(doc)\
            .OfCategory(DB.BuiltInCategory.OST_Rooms)\
            .WhereElementIsNotElementType()
        
        rooms = [room for room in room_collector if room.Level is not None and room.Level.Id == level.Id]
        
        if not rooms:
            ERROR_HANDLE.print_note("No rooms found on level: {}".format(level.Name))
            continue
        
        # Create group for area boundary lines
        group_elements = List[DB.ElementId]()
        
        for room in rooms:
            try:
                options = DB.SpatialElementBoundaryOptions()
                boundary_segments = room.GetBoundarySegments(options)
                
                for boundary_segment_list in boundary_segments:
                    curve_array = DB.CurveArray()
                    for segment in boundary_segment_list:
                        curve_array.Append(segment.GetCurve())
                    
                    if curve_array.Size > 0:
                        curve_loop = DB.CurveLoop()
                        for i in range(curve_array.Size):
                            curve_loop.Append(curve_array[i])
                        
                        # Create area boundary lines
                        sketch_plane = DB.SketchPlane.Create(doc, view.GenLevel.Id)
                        for curve in curve_loop:
                            area_boundary = doc.Create.NewAreaBoundaryLine(sketch_plane, curve, view)
                            if area_boundary:
                                group_elements.Add(area_boundary.Id)
            except Exception as e:
                ERROR_HANDLE.print_note("Error processing room {}: {}".format(room.Id, str(e)))
        
        # Create group if elements were created
        if group_elements.Count > 0:
            group_name = "Area Boundaries Transferred From Rooms - {}".format(level.Name)
            group = doc.Create.NewGroup(group_elements)
            group.GroupType.Name = group_name
    
    t.Commit()


################## main code below #####################
if __name__ == "__main__":
    room_bounding_to_area_b_line(DOC) 