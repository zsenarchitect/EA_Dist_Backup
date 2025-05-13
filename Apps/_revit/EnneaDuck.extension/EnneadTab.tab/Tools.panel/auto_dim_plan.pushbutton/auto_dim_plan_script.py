#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Automatically dimensions walls in plan views.

Features:
- Works with selected walls or all walls in active view
- Creates dimensions between parallel walls
- Smart dimension placement perpendicular to walls
- Option to create dimensions to grids
- Filters out curved walls (future enhancement coming soon!)

"""
__title__ = "Auto Dim Plan"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms
import math

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def get_selected_walls(doc, uidoc):
    """Get selected walls or all walls in active view if nothing selected."""
    selection = uidoc.Selection.GetElementIds()
    
    if selection.Count > 0:
        # Filter selected elements to walls only
        walls = [doc.GetElement(id) for id in selection if doc.GetElement(id).Category.Name == "Walls"]
        if not walls:
            return None  # No walls in selection
        return walls
    return None  # Nothing selected


def get_all_walls_in_view(doc, view):
    """Get all walls in the active view."""
    wall_collector = DB.FilteredElementCollector(doc, view.Id)\
                      .OfCategory(DB.BuiltInCategory.OST_Walls)\
                      .WhereElementIsNotElementType()\
                      .ToElements()
    return list(wall_collector)


def get_grids_in_view(doc, view):
    """Get all grid lines in the active view."""
    grid_collector = DB.FilteredElementCollector(doc, view.Id)\
                     .OfCategory(DB.BuiltInCategory.OST_Grids)\
                     .WhereElementIsNotElementType()\
                     .ToElements()
    return list(grid_collector)


def create_wall_dimensions(doc, walls, view, options):
    """Create dimensions between walls in given view based on options."""
    # Filter walls
    straight_walls = []
    curved_walls = []
    
    for wall in walls:
        try:
            if isinstance(wall.Location.Curve, DB.Line):
                straight_walls.append(wall)
            elif isinstance(wall.Location.Curve, DB.Arc):
                curved_walls.append(wall)
        except:
            continue
    
    if not straight_walls:
        NOTIFICATION.toast("No straight walls found", "Warning")
        return False
    
    if curved_walls and options["show_curved_wall_warning"]:
        NOTIFICATION.toast(f"{len(curved_walls)} curved walls ignored", "Info")
    
    dimension_line_offset = options["dimension_offset"]
    include_grids = options["include_grids"]
    
    # Get grids if needed
    grids = []
    if include_grids:
        grids = get_grids_in_view(doc, view)
    
    # Create dimensions
    dimension_count = 0
    
    # Group walls by direction
    wall_groups = {}
    for wall in straight_walls:
        curve = wall.Location.Curve
        direction = (curve.GetEndPoint(1) - curve.GetEndPoint(0)).Normalize()
        angle = math.atan2(direction.Y, direction.X) * 180 / math.pi
        angle_key = round(angle / 10) * 10  # Group by 10 degree intervals
        
        if angle_key not in wall_groups:
            wall_groups[angle_key] = []
        wall_groups[angle_key].append(wall)
    
    # Create dimensions for each wall group
    for angle, parallel_walls in wall_groups.items():
        if len(parallel_walls) < 2 and not include_grids:
            continue
        
        # Sample wall to determine dimension direction
        sample_wall = parallel_walls[0]
        wall_curve = sample_wall.Location.Curve
        wall_direction = (wall_curve.GetEndPoint(1) - wall_curve.GetEndPoint(0)).Normalize()
        
        # Dimension direction perpendicular to wall
        dimension_direction = DB.XYZ(-wall_direction.Y, wall_direction.X, 0)
        
        # Create reference array for all parallel walls
        refs = DB.ReferenceArray()
        for wall in parallel_walls:
            refs.Append(wall.GetReferenceByName("Center"))
        
        # Add grid references if enabled
        if include_grids:
            for grid in grids:
                grid_curve = grid.Curve
                grid_direction = grid_curve.Direction
                
                # Check if grid is perpendicular to walls
                dot_product = abs(wall_direction.DotProduct(grid_direction))
                if dot_product < 0.3:  # Nearly perpendicular
                    refs.Append(grid.GetCurvesInView(DB.DimensionSegmentType.Linear, view)[0].Reference)
        
        if refs.Size > 1:
            # Find good location for dimension line
            dimension_points = []
            for wall in parallel_walls:
                curve = wall.Location.Curve
                midpoint = (curve.GetEndPoint(0) + curve.GetEndPoint(1)) / 2
                dimension_points.append(midpoint)
            
            # Average point as basis for dimension line
            avg_point = DB.XYZ(0, 0, 0)
            for pt in dimension_points:
                avg_point += pt
            avg_point = avg_point / len(dimension_points)
            
            # Place dimension line
            dim_line_point = avg_point + dimension_direction * dimension_line_offset
            
            try:
                DB.Dimension.Create(doc, view.Id, dim_line_point, refs, DB.DimensionType.Linear)
                dimension_count += 1
            except Exception as e:
                print(f"Error creating dimension: {e}")
    
    return dimension_count > 0


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def auto_dim_plan(doc):
    """Main function to auto dimension walls in plan."""
    active_view = doc.ActiveView
    
    # Check if the active view is a plan view
    if not isinstance(active_view, DB.ViewPlan):
        NOTIFICATION.toast("This tool works only in plan views", "Warning")
        return
    
    # Get walls to dimension
    walls = get_selected_walls(doc, UIDOC)
    selected_mode = True
    
    if not walls:
        # Ask user if they want to dimension all walls
        if forms.alert("No walls selected. Dimension all walls in view?", 
                       yes=True, no=True):
            walls = get_all_walls_in_view(doc, active_view)
            selected_mode = False
        else:
            return
    
    if not walls:
        NOTIFICATION.toast("No walls found to dimension", "Warning")
        return
    
    # Get user options
    options = {
        "dimension_offset": 2.0,  # Default 2 feet
        "include_grids": False,
        "show_curved_wall_warning": True
    }
    
    # Create options form
    components = [
        forms.Label("Dimension Options:"),
        forms.Separator(),
        forms.Label("Dimension offset distance (feet):"),
        forms.TextBox("dimension_offset", options["dimension_offset"]),
        forms.CheckBox("include_grids", "Include grids in dimensions", options["include_grids"]),
        forms.CheckBox("show_curved_wall_warning", "Show curved wall warnings", options["show_curved_wall_warning"]),
    ]
    
    form = forms.AlchemyForm(components, title="Auto Dimension Options")
    if form.show_dialog():
        # Get values from form
        try:
            options["dimension_offset"] = float(form.values["dimension_offset"])
        except:
            options["dimension_offset"] = 2.0
        
        options["include_grids"] = form.values["include_grids"]
        options["show_curved_wall_warning"] = form.values["show_curved_wall_warning"]
    else:
        return
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    success = create_wall_dimensions(doc, walls, active_view, options)
    
    if success:
        NOTIFICATION.toast("Walls dimensioned successfully", "Success")
    else:
        NOTIFICATION.toast("Could not dimension any walls", "Warning")
        
    t.Commit()


################## main code below #####################
if __name__ == "__main__":
    auto_dim_plan(DOC)







