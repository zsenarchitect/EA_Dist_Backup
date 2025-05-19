#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Create view filters based on Generic Model family names, apply colors from CSS definitions, and generate a legend."
__title__ = "Make Filter Legend"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, COLOR, NOTIFICATION, DATA_CONVERSION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_FILTER
from Autodesk.Revit import DB # pyright: ignore 
import re
import os
import sys
from collections import defaultdict
from System.Collections.Generic import List, IList # pyright: ignore
from System import Array # pyright: ignore
import clr # pyright: ignore
import traceback
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def check_active_view():
    """Check if the active view is a non-sheet view and get its hosting sheet.
    
    Returns:
        tuple: (active_view, hosting_sheet) if valid, (None, None) if not valid
    """
    # Get current view
    active_view = UIDOC.ActiveView
    
    # Check if current view is not a sheet
    if active_view.ViewType == DB.ViewType.DrawingSheet:
        NOTIFICATION.messenger(main_text="Please run this tool from a view that's placed on a sheet, not from a sheet view.")
        return None, None
    
    # Find the hosting sheet
    hosting_sheet = get_hosting_sheet(active_view)
    
    if not hosting_sheet:
        NOTIFICATION.messenger(main_text="Please run this tool from a view that's placed on a sheet.")
        return None, None
    
    return active_view, hosting_sheet


def get_hosting_sheet(view):
    """Get the sheet hosting the given view.
    
    Args:
        view (DB.View): The view to find the hosting sheet for
        
    Returns:
        DB.ViewSheet: Hosting sheet or None if not found
    """
    viewports = DB.FilteredElementCollector(DOC).OfClass(DB.Viewport).ToElements()
    for viewport in viewports:
        if viewport.ViewId == view.Id:
            sheet_id = viewport.SheetId
            if sheet_id != DB.ElementId.InvalidElementId:
                return DOC.GetElement(sheet_id)
    return None


def load_color_map_from_css():
    """Load family names and colors from CSS file.
    
    Returns:
        dict: Dictionary mapping family names to their colors (RGB tuples)
    """
    script_dir = os.path.dirname(__file__)
    css_file_path = os.path.join(script_dir, "color_map.css")
    
    # Default empty dictionaries if file doesn't exist
    color_map = {}
    
    # Check if CSS file exists
    if not os.path.exists(css_file_path):
        NOTIFICATION.messenger(main_text="color_map.css file not found. Please create it first.")
        return color_map
    
    # Read CSS file and parse color definitions
    with open(css_file_path, 'r') as f:
        css_content = f.read()
    
    # Find all color definitions using regex
    # Format should be: .FamilyName { color: rgb(r, g, b); }
    pattern = r'\.([A-Za-z0-9_-]+)\s*{[^}]*color:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)'
    matches = re.finditer(pattern, css_content)
    
    for match in matches:
        family_name = match.group(1).replace('-', ' ')
        r = int(match.group(2))
        g = int(match.group(3))
        b = int(match.group(4))
        
        # Store color
        color_map[family_name] = (r, g, b)
    
    if not color_map:
        NOTIFICATION.messenger(main_text="No color definitions found in color_map.css file.")
        
    return color_map


def create_or_update_filters(view, color_map):
    """Create or update view filters for family names defined in color map.
    Uses the correct parameter for Generic Models (Family Name).
    
    Args:
        view (DB.View): Current view to apply filters to
        color_map (dict): Dictionary mapping family names to colors
        
    Returns:
        dict: Dictionary mapping filter names to their override settings
    """
    filter_overrides = {}
    
    # Get solid fill pattern
    solid_fill_id = REVIT_SELECTION.get_solid_fill_pattern_id(DOC)
    
    # Get existing filters in view
    existing_filters = {}
    for filter_id in view.GetFilters():
        filter_element = DOC.GetElement(filter_id)
        existing_filters[filter_element.Name] = filter_id
    
    # Create category set for Generic Models
    categories = DB.CategorySet()
    generic_model_category = DOC.Settings.Categories.get_Item(DB.BuiltInCategory.OST_GenericModel)
    categories.Insert(generic_model_category)
    
    # Convert categories to List<ElementId>
    category_ids = List[DB.ElementId]()
    category_ids.Add(generic_model_category.Id)
    
    # Process each family in the color map
    for family_name, rgb_color in color_map.items():
        try:
            # Create filter name using requested template
            filter_name = "ScreenPanel_{}".format(family_name)
            filter_name = filter_name.replace(":", "").replace("|", "").replace("?", "")
            
            # Use correct parameter for Generic Models: Family Name
            param_id = DB.ElementId(DB.BuiltInParameter.ALL_MODEL_FAMILY_NAME)
            
            # Create rule that contains the family name
            version = int(DOC.Application.VersionNumber)
            if version > 2023:
                rule = DB.ParameterFilterRuleFactory.CreateContainsRule(param_id, family_name)
            else:
                rule = DB.ParameterFilterRuleFactory.CreateContainsRule(param_id, family_name, True)
                
            elem_filter = DB.ElementParameterFilter(rule)
            
            # Create or get existing filter
            filter_element = None
            if filter_name in existing_filters:
                filter_element = DOC.GetElement(existing_filters[filter_name])
            else:
                # Create new filter with category IDs
                filter_element = DB.ParameterFilterElement.Create(DOC, filter_name, category_ids, elem_filter)
            
            # Apply filter to view if not already applied
            if filter_element.Id not in view.GetFilters():
                view.AddFilter(filter_element.Id)
            
            # Set override graphics
            r, g, b = rgb_color
            color = DB.Color(r, g, b)
            
            override = DB.OverrideGraphicSettings()
            override.SetSurfaceForegroundPatternColor(color)
            override.SetSurfaceForegroundPatternId(solid_fill_id)
            override.SetCutForegroundPatternColor(color)
            override.SetCutForegroundPatternId(solid_fill_id)
            
            view.SetFilterOverrides(filter_element.Id, override)
            
            # Store filter info for legend
            filter_overrides[filter_name] = {
                "name": family_name,
                "color": rgb_color,
                "override": override
            }
        except Exception as e:
            NOTIFICATION.messenger(main_text="Error creating filter for {}: {}".format(family_name, str(e)))
            print (traceback.format_exc())
            continue
    
    return filter_overrides


def find_or_create_legend_view():
    """Find existing legend or create a new one named 'ScreenPanel'.
    
    Returns:
        DB.View: Legend view or None if creation fails
    """
    # Look for existing legend titled "ScreenPanel"
    legend_name = "ScreenPanel"
    
    legend_views = DB.FilteredElementCollector(DOC)\
                    .OfClass(DB.View)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
    
    for view in legend_views:
        if view.ViewType == DB.ViewType.Legend and view.Name == legend_name:
            return view
    
    # If not found, create new legend by duplicating an existing one
    existing_legends = [v for v in legend_views if v.ViewType == DB.ViewType.Legend]
    
    if not existing_legends:
        NOTIFICATION.messenger(main_text="No legend views found in the document. Please create a legend view first.")
        return None
    
    # Duplicate the first legend found
    new_legend_id = existing_legends[0].Duplicate(DB.ViewDuplicateOption.Duplicate)
    new_legend = DOC.GetElement(new_legend_id)
    
    # Rename the new legend
    try:
        new_legend.Name = legend_name
    except Exception:
        # If name already exists, try with a number
        for i in range(1, 100):
            try:
                new_legend.Name = "{0} ({1})".format(legend_name, i)
                break
            except:
                continue
    
    return new_legend


def create_legend_graphics(legend_view, filter_overrides):
    """Create legend graphics in the legend view.
    
    Args:
        legend_view (DB.View): Legend view to populate
        filter_overrides (dict): Dictionary mapping filter names to their override settings
    """
    # Clear existing elements in the legend
    ids_to_delete = []
    elements_in_legend = DB.FilteredElementCollector(DOC, legend_view.Id).WhereElementIsNotElementType().ToElementIds()
    
    for element_id in elements_in_legend:
        element = DOC.GetElement(element_id)
        if element.GetType().Name != "View":  # Don't delete the view itself
            ids_to_delete.append(element_id)
    
    if ids_to_delete:
        # Delete elements one by one to avoid collection issues
        for element_id in ids_to_delete:
            try:
                DOC.Delete(element_id)
            except Exception as e:
                NOTIFICATION.messenger(main_text="Error deleting element: " + str(e))
    
    # Get text note type for legend
    text_note_types = DB.FilteredElementCollector(DOC).OfClass(DB.TextNoteType).ToElements()
    text_note_type_id = text_note_types[0].Id
    
    # Get filled region type for color samples
    filled_region_type = None
    filled_region_types = DB.FilteredElementCollector(DOC).OfClass(DB.FilledRegionType).ToElements()
    
    for fr_type in filled_region_types:
        pattern = DOC.GetElement(fr_type.ForegroundPatternId)
        if pattern is not None and pattern.GetFillPattern().IsSolidFill:
            filled_region_type = fr_type
            break
    
    if not filled_region_type and filled_region_types:
        # Create a new filled region type with solid fill
        filled_region_type = filled_region_types[0].Duplicate("ScreenPanel Fill")
    
    # Organize by family names
    items = []
    for filter_name, data in filter_overrides.items():
        items.append(data)
    
    # Sort items by name
    sorted_items = sorted(items, key=lambda x: x["name"])
    
    # Create legend
    y_position = 0
    x_position = 0
    item_spacing = 0.15  # feet
    box_size = 0.25      # feet
    text_offset = 0.1    # feet
    
    # Add header
    header_point = DB.XYZ(x_position, y_position, 0)
    header_text = "Screen Panel Families"
    DB.TextNote.Create(DOC, legend_view.Id, header_point, header_text, text_note_type_id)
    
    # Update position for items
    y_position -= item_spacing * 2
    
    # Add items
    for item in sorted_items:
        try:
            # Create color box
            point0 = DB.XYZ(x_position, y_position, 0)
            point1 = DB.XYZ(x_position, y_position + box_size, 0)
            point2 = DB.XYZ(x_position + box_size, y_position + box_size, 0)
            point3 = DB.XYZ(x_position + box_size, y_position, 0)
            
            # Create boundary for filled region
            curves = DB.CurveLoop()
            curves.Append(DB.Line.CreateBound(point0, point1))
            curves.Append(DB.Line.CreateBound(point1, point2))
            curves.Append(DB.Line.CreateBound(point2, point3))
            curves.Append(DB.Line.CreateBound(point3, point0))
            
            # Create a simple list of CurveLoops
            curve_loops = List[DB.CurveLoop]()
            curve_loops.Add(curves)
            
            # Create filled region with the .NET List directly
            filled_region = DB.FilledRegion.Create(DOC, filled_region_type.Id, legend_view.Id, curve_loops)
            
            # Apply color override
            r, g, b = item["color"]
            color = DB.Color(r, g, b)
            ogs = DB.OverrideGraphicSettings()
            ogs.SetSurfaceForegroundPatternColor(color)
            ogs.SetSurfaceForegroundPatternId(REVIT_SELECTION.get_solid_fill_pattern_id(DOC))
            legend_view.SetElementOverrides(filled_region.Id, ogs)
            
            # Add text label
            text_point = DB.XYZ(x_position + box_size + text_offset, y_position + box_size/2 - 0.02, 0)
            DB.TextNote.Create(DOC, legend_view.Id, text_point, item["name"], text_note_type_id)
        except Exception as e:
            # Log the error but continue with other items
            NOTIFICATION.messenger(main_text="Error creating legend item: " + str(e))
        
        # Update position for next item
        y_position -= item_spacing
    
    return legend_view


def add_legend_to_sheet(sheet, legend_view):
    """Add the legend view to the sheet if not already there.
    
    Args:
        sheet (DB.ViewSheet): Sheet to add the legend to
        legend_view (DB.View): Legend view to add
        
    Returns:
        DB.Viewport: Created or existing viewport
    """
    # Check if legend is already on the sheet
    existing_viewports = sheet.GetAllViewports()
    for vp_id in existing_viewports:
        viewport = DOC.GetElement(vp_id)
        if viewport.ViewId == legend_view.Id:
            return viewport
    
    # Find a free space on the sheet
    sheet_size = sheet.GetViewportBoundingBox(None)
    sheet_min = sheet_size.Min
    sheet_max = sheet_size.Max
    
    # Find a position in the bottom right corner
    legend_size = DB.XYZ(2.0, 3.0, 0)  # Estimated size of legend
    
    # Start from bottom right and move left
    pos_x = sheet_max.X - legend_size.X - 0.5
    pos_y = sheet_min.Y + legend_size.Y + 0.5
    
    # Create viewport at free position
    center_point = DB.XYZ(pos_x, pos_y, 0)
    viewport = DB.Viewport.Create(DOC, sheet.Id, legend_view.Id, center_point)
    
    return viewport


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def make_filter_legend(doc):
    """Main function to create filter legend using structured steps.
    
    Args:
        doc (DB.Document): Active document
    """
    # Step 1: Check active view is non-sheet view and get hosting sheet
    active_view, hosting_sheet = check_active_view()
    if not active_view or not hosting_sheet:
        return
    
    # Step 2: Load family name and color map from CSS
    color_map = load_color_map_from_css()
    if not color_map:
        return
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # Step 3 & 4: Create/update filters and add to view template
    if active_view.ViewTemplateId != DB.ElementId.InvalidElementId:
        template = DOC.GetElement(active_view.ViewTemplateId)
        filter_overrides = create_or_update_filters(template, color_map)
    else:
        filter_overrides = create_or_update_filters(active_view, color_map)
    
    # Step 5: Create/update legend view
    legend_view = find_or_create_legend_view()
    if not legend_view:
        t.RollBack()
        return
    
    create_legend_graphics(legend_view, filter_overrides)
    
    # Step 6: Add legend to current hosting sheet
    add_legend_to_sheet(hosting_sheet, legend_view)
    
    t.Commit()
    
    success_message = "Filter legend created successfully!\nLegend placed on sheet: " + hosting_sheet.Name
    NOTIFICATION.messenger(main_text=success_message)


################## main code below #####################
if __name__ == "__main__":
    make_filter_legend(DOC)







