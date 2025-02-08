#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Export Revit Rooms/Areas to Rhino as color-coded diagrams.

This tool creates a simplified diagram representation of Rooms or Areas in Rhino:
- Exports boundaries with filleted corners
- Maintains color coding from Revit color schemes
- Adds text labels for space identifiers
- Creates solid hatches for each space
"""
__title__ = "RoomOrArea2Diagram"


import clr  # pyright: ignore
import sys  # pyright: ignore
import os

try:
    import System  # pyright: ignore
    clr.AddReference('RhinoCommon')
    import Rhino  # pyright: ignore
    clr.AddReference('RhinoInside.Revit')
    from RhinoInside.Revit.Convert.Geometry import GeometryDecoder as RIR_DECODER  # pyright: ignore
   
    IMPORT_OK = True
except:
    IMPORT_OK = False

    
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT, REVIT_RHINO
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


class RoomDiagramExporter:
    """Handles export of Revit Rooms/Areas to Rhino diagram representation."""
    
    def __init__(self, revit_doc):
        """Initialize exporter with Revit document.
        
        Args:
            revit_doc: Active Revit document
        """
        self.revit_doc = revit_doc
        self.output_file = r"C:\Temp\EnneadTabRevit2RhinoBubbleDiagram.3dm"
        self.rhino_doc = None
        
        self._setup_rhino_doc()
        


    def _get_color_dict(self):
        """Extract color mapping from active color fill scheme."""
        self.color_dict = {}
        built_in_category = DB.BuiltInCategory.OST_Areas
        if self.cate_selected == "Rooms":
            built_in_category = DB.BuiltInCategory.OST_Rooms
        color_scheme = self.revit_doc.GetElement(self.revit_doc.ActiveView.GetColorFillSchemeId(DB.ElementId(built_in_category)))
        if not color_scheme:
            return
        for entry in color_scheme.GetEntries ():
            self.color_dict[entry.GetStringValue ()] = entry.Color



    def _setup_rhino_doc(self):
        self.rhino_doc = REVIT_RHINO.setup_rhino_doc(self.revit_doc)
        self.rhino_doc.HatchPatterns.Add(Rhino.DocObjects.HatchPattern.Defaults.Solid)


    def export_as_diagram(self):
        self.para_name = "Area_$Department"


        
        options = ["Rooms", "Areas"]
        self.cate_selected = forms.SelectFromList.show(options, "Select the type of elements to export")
        if self.cate_selected is None:
            return
        if self.cate_selected == "Rooms":
            spaces = DB.FilteredElementCollector(self.revit_doc, self.revit_doc.ActiveView.Id)\
               .OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
        else:
            spaces = DB.FilteredElementCollector(self.revit_doc, self.revit_doc.ActiveView.Id)\
               .OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
        option = DB.SpatialElementBoundaryOptions()

        self.radius = forms.ask_for_number_slider(1, max = 10, prompt="Enter the radius of the fillet(in feet)", title="Fillet Radius")
        
        self._get_color_dict()
        for space in spaces:
            self._process_space_boundaries(space, option)

        self._write_rhino_file()


    def _get_layer(self, layer_name, color=None):
        """Get or create a Rhino layer with specified name and color.
        
        Args:
            layer_name (str): Name of the layer to find or create
            color (System.Drawing.Color, optional): Color to use if creating new layer
            
        Returns:
            Rhino.DocObjects.Layer: The found or created layer
        """

        layer = self.rhino_doc.Layers.FindName (layer_name)
        if not layer:
            layer = Rhino.DocObjects.Layer()


            layer.Name = layer_name
            if color:
                layer.Color = color
            self.rhino_doc.Layers.Add(layer)
            layer = self.rhino_doc.Layers.FindName(layer_name)
        return layer
    



    def _process_space_boundaries(self, space, option):
        self.space_color_identifier = space.LookupParameter(self.para_name).AsString()

        label_layer = self._get_layer("_Label", System.Drawing.Color.Black)
        label_attr = Rhino.DocObjects.ObjectAttributes()
        label_attr.LayerIndex = label_layer.Index

        text_geo = Rhino.Display.Text3d(self.space_color_identifier)
        text_geo.HorizontalAlignment  = Rhino.DocObjects.TextHorizontalAlignment .Center
        text_geo.TextPlane = RIR_DECODER.ToPlane(DB.Plane.CreateByNormalAndOrigin (DB.XYZ(0,0,1), space.Location.Point))
        self.rhino_doc.Objects.AddText(text_geo, label_attr)

        boundary_segments = space.GetBoundarySegments(option)
        for segment_array in boundary_segments:
            curve_segments = self._get_curve_segments(segment_array)
            if not curve_segments:
                continue
            joined_curve = Rhino.Geometry.Curve.JoinCurves(curve_segments)
            if not joined_curve or len(joined_curve) == 0:
                continue

            
            filleted_crv = self._create_filleted_curve(joined_curve[0])
            if not filleted_crv:
                continue
            self._create_and_add_hatch(filleted_crv)

    def _get_curve_segments(self, segment_array):
        curve_segments = []
        for segment in segment_array:
            curve = segment.GetCurve()
            rhino_curve = RIR_DECODER.ToCurve(curve)
            if rhino_curve:
                curve_segments.append(rhino_curve)
        return curve_segments

    def _create_filleted_curve(self, curve):
        curve = Rhino.Geometry.Curve.CreateFilletCornersCurve(
            curve,
            self.radius,
            self.rhino_doc.ModelAbsoluteTolerance,
            self.rhino_doc.ModelAngleToleranceDegrees
        )
        attr = Rhino.DocObjects.ObjectAttributes()
        layer = self._get_layer("_Outline::" + self.space_color_identifier)
        attr.LayerIndex = layer.Index
        out_line = self.rhino_doc.Objects.AddCurve(curve, attr)
        



        return curve

    
    def _create_and_add_hatch(self, curve):
        attr = Rhino.DocObjects.ObjectAttributes()
        revit_color = self.color_dict[self.space_color_identifier]
        layer_color = System.Drawing.Color.FromArgb(revit_color.Red, revit_color.Green, revit_color.Blue)
        layer = self._get_layer("_Hatch::" + self.space_color_identifier, layer_color)
        attr.LayerIndex = layer.Index
        


        solid_pattern = Rhino.DocObjects.HatchPattern.Defaults.Solid
        hatch_pattern_index = solid_pattern.Index
        tolerance = self.rhino_doc.ModelAbsoluteTolerance
        breps = Rhino.Geometry.Brep.CreatePlanarBreps([curve], tolerance)
        if not breps:
            print ("No hatch created for some shape, maybe radius too small or there is a gap in your line.")
            return
        for brep in breps:
            face_index = brep.Faces.Count - 1
            hatch = Rhino.Geometry.Hatch.CreateFromBrep(brep, 
                                                    face_index, 
                                                    hatch_pattern_index,
                                                    Rhino.RhinoMath.ToRadians(0), 
                                                    1,
                                                    Rhino.Geometry.Point3d.Origin)
            self.rhino_doc.Objects.AddHatch(hatch, attr)


    def _write_rhino_file(self):
        write_option = Rhino.FileIO.FileWriteOptions()
        write_option.FileVersion = 7
        self.rhino_doc.Write3dmFile(self.output_file, write_option)
        self.rhino_doc.Dispose()
        NOTIFICATION.messenger("Successfully exported Revit Spaces to Rhino file: {}".format(self.output_file))
        os.startfile(self.output_file)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def room2diagram(doc):
    """Main entry point for the Room/Area diagram export tool.
    
    Args:
        doc: Current Revit document
    """
    if not IMPORT_OK:
        NOTIFICATION.messenger("Please initiate Rhino Inside First")
        return
    
    exporter = RoomDiagramExporter(doc)
    exporter.export_as_diagram()

################## main code below #####################
if __name__ == "__main__":
    room2diagram(DOC)







