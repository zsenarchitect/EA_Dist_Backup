#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Duplicates a Revit area scheme to a new area scheme with all boundaries and areas.

This tool allows you to:
1. Select an existing area scheme to duplicate
2. Provide a new unique name for the duplicated scheme
3. Choose which views to include in the duplication process
4. Automatically transfer all boundaries and areas to the new scheme
"""
__title__ = "Duplicate\nArea Scheme"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_AREA_SCHEME
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import forms
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


class AreaSchemeDuplicator:
    """Class responsible for duplicating a Revit area scheme with all its properties."""
    
    class ViewOption(forms.TemplateListItem):
        """Class to represent a view option in the selection dialog."""
        @property
        def name(self):
            return "[{}] {}".format(self.item.GenLevel.Name, self.item.Name)
    
    def __init__(self, doc):
        """Initialize with Revit document."""
        self.doc = doc
        self.original_area_scheme = None
        self.new_area_scheme = None
        self.new_area_plan_view = None
        self.selected_views = []
    
    @LOG.log(__file__, __title__)
    @ERROR_HANDLE.try_catch_error()
    def run(self):
        """Main method to run the area scheme duplication process."""
        t = DB.Transaction(self.doc, __title__)
        t.Start()
        
        self._select_and_duplicate_scheme()
        if not self.original_area_scheme or not self.new_area_scheme:
            return
        self._select_views()
        self._process_views()
        
        t.Commit()
    
    def _select_and_duplicate_scheme(self):
        """Select the original area scheme and create a duplicate with new name."""
        # Pick area scheme to duplicate
        self.original_area_scheme = REVIT_SELECTION.pick_area_scheme(self.doc, 
                                                                     title="Pick the area scheme to duplicate from", 
                                                                     button_name="Select Area Scheme to Duplicate From")
        if not self.original_area_scheme:
            return
        self.new_area_scheme = REVIT_SELECTION.pick_area_scheme(self.doc, 
                                                                 title="Pick the target area scheme", 
                                                                 button_name="Pick Target AreaScheme")
        if not self.new_area_scheme:
            return


    def ARCHIVE_duplicate_area_scheme(self):

        """this is archived method because you after duplication this new area shcme has not color fill scheme to duplicate from."""
        # Get a new name for the new area scheme, cannot be same as other area schemes
        new_name = forms.ask_for_unique_string(
            title="New Area Scheme Name",
            reserved_values=[x.Name for x in REVIT_AREA_SCHEME.get_all_area_schemes(self.doc)],
            default=self.original_area_scheme.Name + "_copy"
        )

        # Copy this area scheme
        newElemIds = DB.ElementTransformUtils.CopyElement(
            self.doc, 
            self.original_area_scheme.Id, 
            DB.XYZ.Zero
        )
        self.new_area_scheme = self.doc.GetElement(newElemIds[0])
        self.new_area_scheme.Name = new_name
    
    def _select_views(self):
        """Let user select which views to duplicate."""
        # Get all views that use original area scheme
        all_views = DB.FilteredElementCollector(self.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        views_using_original_scheme = [v for v in all_views if hasattr(v, "AreaScheme") and v.AreaScheme and v.AreaScheme.Id == self.original_area_scheme.Id]

        self.selected_views = forms.SelectFromList.show(
            [self.ViewOption(v) for v in views_using_original_scheme],
            multiselect=True,
            width=800,
            title="Select View",
            button_name="Select View. (DO NOT PICK SAME LEVEL VIEW MORE THAN ONCE)"
        )
    
    def _process_views(self):
        """Process each selected view by creating a new view and transferring elements."""
        for view in self.selected_views:
            # Create a new view with the new area scheme
            self.new_area_plan_view = DB.ViewPlan.CreateAreaPlan(
                self.doc, 
                self.new_area_scheme.Id, 
                view.GenLevel.Id
            )
            
            # Transfer boundaries and areas
            boundary_lines = DB.FilteredElementCollector(self.doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaSchemeLines).ToElements()
            for boundary_line in boundary_lines:
                self._transfer_boundary(boundary_line)
            
            areas = DB.FilteredElementCollector(self.doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
            for area in areas:
                self._transfer_area(area)
    
    def _match_property(self, para_name, source, target):
        """Match a property from source to target element.
        
        Attempts to copy parameter values between elements with proper type handling.
        Supports String, Double, Integer and ElementId parameter types.
        
        Args:
            para_name: Name of the parameter to copy
            source: Source element to copy from
            target: Target element to copy to
        """
        # Skip if parameter doesn't exist in either source or target
        source_param = source.LookupParameter(para_name)

        # handle api change from 2024 to 2025
        if hasattr(source_param, "HasValue") and not source_param.HasValue:
            return
        if hasattr(source_param, "ParameterHasValue") and not source_param.ParameterHasValue:
            return


        target_param = target.LookupParameter(para_name)
        
        if not source_param or not target_param:
            return
            
        # Skip if parameter is read-only
        if target_param.IsReadOnly:
            return
            
        # Handle different parameter storage types
        try:
            storage_type = source_param.StorageType
            
            if storage_type == DB.StorageType.String:
                target_param.Set(source_param.AsString())
                
            elif storage_type == DB.StorageType.Double:
                target_param.Set(source_param.AsDouble())
                
            elif storage_type == DB.StorageType.Integer:
                target_param.Set(source_param.AsInteger())
                
            elif storage_type == DB.StorageType.ElementId:
                target_param.Set(source_param.AsElementId())
        except Exception as e:
            # Log error but continue with other parameters
            print("Could not set parameter '{}'".format(para_name))
    
    def _transfer_area(self, area):
        """Transfer an area from the original view to the new view."""
        area_location = area.Location.Point
        insert_location = DB.UV(area_location.X, area_location.Y)
        new_area = self.doc.Create.NewArea(self.new_area_plan_view, insert_location)
        
        para_names = [x.Definition.Name for x in area.Parameters]
        for para_name in para_names:
            self._match_property(para_name, area, new_area)
    
    def _transfer_boundary(self, boundary_line):
        """Transfer a boundary line from the original view to the new view."""
        ref_crv = boundary_line.Location.Curve
        new_area_boundary = self.doc.Create.NewAreaBoundaryLine(
            self.new_area_plan_view.SketchPlane, 
            ref_crv, 
            self.new_area_plan_view
        )


################## main code below #####################
if __name__ == "__main__":
    duplicator = AreaSchemeDuplicator(DOC)
    duplicator.run()







