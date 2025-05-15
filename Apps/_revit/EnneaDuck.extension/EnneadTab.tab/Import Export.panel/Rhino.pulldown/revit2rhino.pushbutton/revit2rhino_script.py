#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ ="""
Script for exporting Revit Family Instances to Rhino.
It converts each FamilyInstance's geometry into a **single Rhino block** containing all its Breps
(or fallback Meshes). The block definition is annotated with 'RevitElementID'.

The script will first try to extract untransformed geometry from the symbol, but if that fails,
it will fall back to using instance geometry for creating blocks.

Users can select which families to export through an interactive selection dialog.

Block names in Rhino follow the format: "FamilyName_ElementID"
"""


__title__ = "Revit2Rhino"

import clr  # pyright: ignore

import os
import time

try:
    import System  # pyright: ignore
    clr.AddReference('RhinoCommon')
    import Rhino  # pyright: ignore
    clr.AddReference('RhinoInside.Revit')
    from RhinoInside.Revit.Convert.Geometry import GeometryDecoder as RIR_DECODER  # pyright: ignore
    IMPORT_OK = True
except:
    IMPORT_OK = False

# Example references to other modules in your environment
import proDUCKtion  # pyright: ignore
proDUCKtion.validify()

from pyrevit import forms
from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, UI, ENVIRONMENT, USER
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT, REVIT_RHINO, REVIT_FORMS
from Autodesk.Revit import DB  # pyright: ignore

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def revit2rhino(doc):
    if not IMPORT_OK:
        NOTIFICATION.messenger("Please initate [Rhino.Inside] First")
        return
    
    # Print developer info
    if USER.IS_DEVELOPER:
        ERROR_HANDLE.print_note("\n=== DEVELOPER INFO ===")
        ERROR_HANDLE.print_note("Document title: {}".format(doc.Title))
        ERROR_HANDLE.print_note("Document path: {}".format(doc.PathName))
        ERROR_HANDLE.print_note("Active view: {}".format(doc.ActiveView.Name))
        ERROR_HANDLE.print_note("Revit document unit: {}".format(REVIT_UNIT.get_doc_length_unit_name(doc)))
        ERROR_HANDLE.print_note("======================\n")
    
    # Collect all family instances from current view
    all_family_instances = (
        DB.FilteredElementCollector(doc, doc.ActiveView.Id)
        .OfClass(DB.FamilyInstance)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    
    # Get unique family names
    family_names = set()
    family_dict = {}  # To map family names to instances
    
    for instance in all_family_instances:
        try:
            family_name = instance.Symbol.FamilyName
            if family_name not in family_dict:
                family_dict[family_name] = []
            family_dict[family_name].append(instance)
            family_names.add(family_name)
        except:
            pass
    
    # Convert to list and sort
    family_names = sorted(list(family_names))
    
    if USER.IS_DEVELOPER:
        ERROR_HANDLE.print_note("Found {} unique families in current view:".format(len(family_names)))
        for i, name in enumerate(family_names):
            ERROR_HANDLE.print_note("  {}: {} ({} instances)".format(i+1, name, len(family_dict[name])))
    
    # Let user select which families to export
    selected_families = forms.SelectFromList.show(
        family_names,
        multiselect=True,
        title="Select Families to Export",
        button_name="Export Selected Families"
    )
    
    if not selected_families:
        NOTIFICATION.messenger("No families selected for export")
        return
    
    # Collect all instances from selected families
    selected_instances = []
    for family_name in selected_families:
        selected_instances.extend(family_dict[family_name])
    
    total_count = len(selected_instances)
    
    # Show warning if exporting more than 100 elements
    if total_count > 100:
        proceed = forms.alert(
            "You are about to export {} elements. This may take a while. Continue?".format(total_count),
            options=["Yes", "No"],
            title="Large Export Warning"
        )
        if proceed == "No":
            NOTIFICATION.messenger("Export canceled by user")
            return
    
    NOTIFICATION.messenger("Exporting {} instances from {} families".format(
        total_count, len(selected_families)))
    
    if USER.IS_DEVELOPER:
        ERROR_HANDLE.print_note("\nSelected families for export:")
        for name in selected_families:
            ERROR_HANDLE.print_note("  - {} ({} instances)".format(name, len(family_dict[name])))
    
    exporter = RevitToRhinoExporter(doc)
    exporter.family_instances = selected_instances  # Pass the selected instances
    exporter.export_family_instances()
    

class RevitToRhinoExporter(object):
    def __init__(self, revit_doc):
        self.revit_doc = revit_doc
        
        # Generate timestamp for filename using time module
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.output_file = os.path.join(ENVIRONMENT.DUMP_FOLDER, "{}_Revit2Rhino_{}.3dm".format(ENVIRONMENT.PLUGIN_NAME, timestamp))
        
        self.rhino_doc = None
        self.family_instances = None
        
        # Get the current document unit
        self.revit_unit = REVIT_UNIT.get_doc_length_unit_name(revit_doc)
        
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("\n=== EXPORTER SETTINGS ===")
            ERROR_HANDLE.print_note("Output file: {}".format(self.output_file))
            ERROR_HANDLE.print_note("Revit unit: {}".format(self.revit_unit))
            ERROR_HANDLE.print_note("Dump folder: {}".format(ENVIRONMENT.DUMP_FOLDER))
            ERROR_HANDLE.print_note("========================\n")

    def export_family_instances(self):
        """Collects FamilyInstances, creates a block for each instance,
        scales geometry from feet->mm, places block with only rotation+translation,
        and saves the result to a 3DM file."""
        self.rhino_doc = REVIT_RHINO.setup_rhino_doc(self.revit_doc)
        geom_options = self._create_geometry_options()
        
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("Rhino document settings:")
            ERROR_HANDLE.print_note("  - Model unit system: {}".format(self.rhino_doc.ModelUnitSystem))
            ERROR_HANDLE.print_note("  - Page unit system: {}".format(self.rhino_doc.PageUnitSystem))
            ERROR_HANDLE.print_note("  - Model absolute tolerance: {}".format(self.rhino_doc.ModelAbsoluteTolerance))
        
        # Use pre-collected instances if available, otherwise collect them
        if not self.family_instances:
            self.family_instances = self._collect_family_instances()

        # Cache block definitions by family symbol ID to avoid duplicates
        self.block_cache = {}
        
        total_count = len(self.family_instances)
        for i, element in enumerate(self.family_instances):
            if i % 5 == 0:
                NOTIFICATION.messenger("Exporting {} of {} elements".format(i+1, total_count))
            self._process_element(element, geom_options)

        self._write_rhino_file()

    def _create_geometry_options(self):
        opts = DB.Options()
        opts.DetailLevel = DB.ViewDetailLevel.Fine
        opts.IncludeNonVisibleObjects = True
        return opts

    def _collect_family_instances(self):
        return (
            DB.FilteredElementCollector(self.revit_doc, self.revit_doc.ActiveView.Id)
            .OfClass(DB.FamilyInstance)
            .WhereElementIsNotElementType()
            .ToElements()
        )

    def _get_family_name(self, element):
        """Get family name from an element with error handling"""
        try:
            return element.Symbol.FamilyName
        except:
            return "Unknown"

    def _process_element(self, element, geom_options):
        """Extracts geometry for the block definition, then places a block instance
        with the element's transformation."""
        element_id = element.Id.IntegerValue
        family_name = self._get_family_name(element)
        symbol_id = element.Symbol.Id.IntegerValue
        
        if USER.IS_DEVELOPER and element_id % 50 == 0:
            ERROR_HANDLE.print_note("Processing element ID: {}, Family: {}".format(element_id, family_name))
            if hasattr(element, "GetTransform"):
                transform = element.GetTransform()
                if transform:
                    ERROR_HANDLE.print_note("  - Transform origin: ({:.4f}, {:.4f}, {:.4f})".format(
                        transform.Origin.X, transform.Origin.Y, transform.Origin.Z))
        
        # Check if we've already created a block for this symbol
        if symbol_id in self.block_cache:
            block_idx = self.block_cache[symbol_id]
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("  Using cached block for symbol {}".format(symbol_id))
        else:
            # First try to get geometry from the symbol (preferred)
            block_geometry = self._get_geometry(element, geom_options)
            
            if not block_geometry:
                if USER.IS_DEVELOPER:
                    ERROR_HANDLE.print_note("  WARNING: No valid geometry found for {}".format(family_name))
                return
            
            # Create block definition using the geometry
            block_idx = self._create_block_for_element(family_name, symbol_id, block_geometry)
            
            if block_idx < 0:
                if USER.IS_DEVELOPER:
                    ERROR_HANDLE.print_note("  WARNING: Failed to create block for {}".format(family_name))
                return
                
            # Cache the block index
            self.block_cache[symbol_id] = block_idx
        
        # Place a block instance with the element's transformation
        self._place_block_instance(block_idx, element)

    def _get_geometry(self, element, geom_options):
        """Try to get geometry for creating a block definition.
        First tries to get symbol geometry, then falls back to instance geometry if needed."""
        family_name = self._get_family_name(element)
        element_id = element.Id.IntegerValue
        
        # First try symbol geometry
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("  Trying symbol geometry for {}".format(family_name))
            
        symbol_geometry = self._get_symbol_geometry(element.Symbol, geom_options)
        if symbol_geometry:
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("  Successfully got symbol geometry for {}".format(family_name))
            return symbol_geometry
            
        # If symbol geometry failed, try instance geometry
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("  Symbol geometry failed, trying instance geometry for {}".format(family_name))
            
        instance_geometry = self._get_instance_geometry(element, geom_options)
        if instance_geometry:
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("  Successfully got instance geometry for {}".format(family_name))
            return instance_geometry
            
        # If both approaches failed
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("  Both symbol and instance geometry approaches failed for {}".format(family_name))
        
        return []

    def _get_symbol_geometry(self, symbol, geom_options):
        """Extract geometry from a family symbol (untransformed)"""
        try:
            symbol_geom = symbol.get_Geometry(geom_options)
            if not symbol_geom:
                return []
                
            element_geometry = []
            for geometry_object in symbol_geom:
                if isinstance(geometry_object, DB.GeometryInstance):
                    # Get the symbol geometry (untransformed)
                    true_geo = geometry_object.GetSymbolGeometry()
                    if not true_geo:
                        continue
                        
                    for g_obj in true_geo:
                        converted = self._convert_revit_geometry(g_obj)
                        if converted:
                            element_geometry.extend(converted)
            
            return element_geometry
        except Exception as e:
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("  Error getting symbol geometry: {}".format(str(e)))
            return []

    def _get_instance_geometry(self, element, geom_options):
        """Extract geometry from a family instance"""
        try:
            geom_elem = element.get_Geometry(geom_options)
            if not geom_elem:
                return []
                
            element_geometry = []
            for geometry_object in geom_elem:
                if isinstance(geometry_object, DB.GeometryInstance):
                    # Get the instance geometry (may include transformation)
                    true_geo = geometry_object.GetInstanceGeometry()
                    if not true_geo:
                        continue
                        
                    for g_obj in true_geo:
                        converted = self._convert_revit_geometry(g_obj)
                        if converted:
                            element_geometry.extend(converted)
            
            return element_geometry
        except Exception as e:
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("  Error getting instance geometry: {}".format(str(e)))
            return []

    def _convert_revit_geometry(self, g_obj):
        """Convert a single Revit geometry object (Solid or Mesh) to Rhino geometry in feet.
        We do NOT scale it here."""
        if self.revit_doc.GetElement(g_obj.GraphicsStyleId):
            sub_c = self.revit_doc.GetElement(g_obj.GraphicsStyleId).GraphicsStyleCategory
            if USER.IS_DEVELOPER:
                ERROR_HANDLE.print_note("dev only: sub_c.Name: {}".format(sub_c.Name))
                
        results = []
        if isinstance(g_obj, DB.Solid) and g_obj.Volume > 1e-6:
            breps = RIR_DECODER.ToBrep(g_obj)
            if not breps:
                return results
            if isinstance(breps, list):
                for b in breps:
                    if b:
                        results.append(b)
            else:
                results.append(breps)
        elif hasattr(g_obj, 'Mesh'):
            revit_mesh = g_obj.Mesh
            if revit_mesh and revit_mesh.NumTriangles > 0:
                r_mesh = self._mesh_to_rhino(revit_mesh)
                results.append(r_mesh)
        return results

    def _mesh_to_rhino(self, revit_mesh):
        """Convert Revit mesh to a Rhino mesh object (in feet)."""
        rhino_mesh = Rhino.Geometry.Mesh()
        for i in range(revit_mesh.NumVertices):
            rv_vertex = revit_mesh.Vertices[i]
            rhino_mesh.Vertices.Add(rv_vertex.X, rv_vertex.Y, rv_vertex.Z)
        for i in range(revit_mesh.NumTriangles):
            tri = revit_mesh.get_Triangle(i)
            idx0 = tri.get_VertexIndex(0)
            idx1 = tri.get_VertexIndex(1)
            idx2 = tri.get_VertexIndex(2)
            rhino_mesh.Faces.AddFace(idx0, idx1, idx2)
        return rhino_mesh

    def _create_block_for_element(self, family_name, symbol_id, geometry_data):
        """Create a new block definition. Returns block index."""
        # Create block name with family name as prefix
        block_name = "{}_Symbol_{}".format(family_name, symbol_id)
        
        # Replace invalid characters for Rhino block names
        block_name = block_name.replace(":", "_").replace("/", "_").replace("\\", "_")
        
        attributes = []
        base_point = Rhino.Geometry.Point3d(0, 0, 0)

        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("  Creating block '{}' with {} geometry objects".format(
                block_name, len(geometry_data)))

        # Create the block definition
        block_idx = self.rhino_doc.InstanceDefinitions.Add(
            block_name,
            "Created from Revit family",
            base_point,
            geometry_data,
            attributes
        )

        if block_idx < 0:
            ERROR_HANDLE.print_note("Warning: block with name {} already exists.".format(block_name))
            return -1

        return block_idx

    def _place_block_instance(self, block_idx, element):
        """Place an instance of the block using Revit's element transformation.
        Also set user string attributes with element metadata."""
        # Get the element's transformation
        instance_transform = self._get_element_transform_no_scale(element)
        
        # Create a block instance with the transformation
        instance_id = self.rhino_doc.Objects.AddInstanceObject(block_idx, instance_transform)
        
        if instance_id:
            inst_obj = self.rhino_doc.Objects.FindId(instance_id)
            if inst_obj:
                element_id = element.Id.IntegerValue
                
                # Add metadata as user strings
                inst_obj.Attributes.SetUserString("RevitElementID", str(element_id))
                family_name = self._get_family_name(element)
                inst_obj.Attributes.SetUserString("FamilyName", family_name)
                
                inst_obj.CommitChanges()
                
                if USER.IS_DEVELOPER and element_id % 50 == 0:
                    ERROR_HANDLE.print_note("  - Block instance placed with ID: {}".format(instance_id))
                    ERROR_HANDLE.print_note("  - Element metadata added")

    def _get_element_transform_no_scale(self, element):
        """Compute a Rhino transform from this FamilyInstance's Revit transform.
        Extract only rotation + translation from Revit's matrix, ignoring scale.
        Geometry is already in mm, so no additional scale is applied here."""
        revit_transform = element.GetTransform()
        if revit_transform is None:
            return Rhino.Geometry.Transform.Identity
          
        rhTrans = Rhino.Geometry.Transform.Identity

        # X basis
        rhTrans.M00 = revit_transform.BasisX.X
        rhTrans.M10 = revit_transform.BasisX.Y
        rhTrans.M20 = revit_transform.BasisX.Z
        rhTrans.M30 = 0.0

        # Y basis
        rhTrans.M01 = revit_transform.BasisY.X
        rhTrans.M11 = revit_transform.BasisY.Y
        rhTrans.M21 = revit_transform.BasisY.Z
        rhTrans.M31 = 0.0

        # Z basis
        rhTrans.M02 = revit_transform.BasisZ.X
        rhTrans.M12 = revit_transform.BasisZ.Y
        rhTrans.M22 = revit_transform.BasisZ.Z
        rhTrans.M32 = 0.0

        # Origin - use correct unit conversion from REVIT_UNIT
        origin_x = REVIT_UNIT.internal_to_unit(revit_transform.Origin.X, self.revit_unit)
        origin_y = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Y, self.revit_unit)
        origin_z = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Z, self.revit_unit)
        
        rhTrans.M03 = origin_x
        rhTrans.M13 = origin_y
        rhTrans.M23 = origin_z
        rhTrans.M33 = 1.0
        
        if USER.IS_DEVELOPER and element.Id.IntegerValue % 50 == 0:
            ERROR_HANDLE.print_note("  - Transform origin (converted): ({:.4f}, {:.4f}, {:.4f})".format(
                origin_x, origin_y, origin_z))

        return rhTrans

    def _write_rhino_file(self):
        write_option = Rhino.FileIO.FileWriteOptions()
        write_option.FileVersion = 7  # Save as Rhino 7 3dm
        
        if USER.IS_DEVELOPER:
            ERROR_HANDLE.print_note("\nSaving Rhino file:")
            ERROR_HANDLE.print_note("  - Path: {}".format(self.output_file))
            ERROR_HANDLE.print_note("  - Number of blocks: {}".format(self.rhino_doc.InstanceDefinitions.Count))
            ERROR_HANDLE.print_note("  - Number of objects: {}".format(self.rhino_doc.Objects.Count))
        
        self.rhino_doc.Write3dmFile(self.output_file, write_option)
        self.rhino_doc.Dispose()
        NOTIFICATION.messenger("Successfully exported Revit FamilyInstances to Rhino file: {0}".format(self.output_file))
        os.startfile(self.output_file)

################## main code below #####################
if __name__ == "__main__":
    revit2rhino(DOC)
