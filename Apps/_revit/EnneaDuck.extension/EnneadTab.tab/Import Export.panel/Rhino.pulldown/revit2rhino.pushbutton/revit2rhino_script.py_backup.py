#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ ="""
Script for exporting Revit Family Instances to Rhino.
It converts each FamilyInstance's geometry into a Rhino block containing all its Breps
(or fallback Meshes). The block definition is annotated with 'RevitElementID'.

GEOMETRY EXTRACTION METHODS:
1. First tries GetSymbolGeometry() - Returns untransformed geometry in family coordinate system.
   This is ideal for block definitions as it's in the symbol's local coordinate space.

2. If that fails, uses GetInstanceGeometry() - Returns geometry that includes the instance
   transformation and is already in the project coordinate system.
   For this case, we untransform the geometry before creating the block definition.

Block names in Rhino follow the format: "FamilyName_TypeName"
Each export includes a timestamp in the filename.
"""

__title__ = "Revit2Rhino"

import clr  # pyright: ignore
import os
import time
import logging

# Configure logging
logger = logging.getLogger("Revit2Rhino")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def enable_debug_logging():
    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")

try:
    import System  # pyright: ignore
    clr.AddReference('RhinoCommon')
    import Rhino  # pyright: ignore
    clr.AddReference('RhinoInside.Revit')
    from RhinoInside.Revit.Convert.Geometry import GeometryDecoder as RIR_DECODER  # pyright: ignore
    IMPORT_OK = True
except:
    IMPORT_OK = False


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
    """Main entry point for Revit to Rhino export."""
    # Check if Rhino.Inside is available
    if not IMPORT_OK:
        NOTIFICATION.messenger("Please initiate [Rhino.Inside] First")
        return
    
    # Enable debug logging for developers
    if USER.IS_DEVELOPER:
        enable_debug_logging()
    
    # Collect family instances
    logger.info("Collecting family instances from current view...")
    all_family_instances = (
        DB.FilteredElementCollector(doc, doc.ActiveView.Id)
        .OfClass(DB.FamilyInstance)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    
    # Organize by family
    family_dict = {}
    for instance in all_family_instances:
        try:
            family_name = instance.Symbol.FamilyName
            if family_name not in family_dict:
                family_dict[family_name] = []
            family_dict[family_name].append(instance)
        except:
            pass
    
    # Check if families were found
    family_names = sorted(list(family_dict.keys()))
    if not family_names:
        NOTIFICATION.messenger("No family instances found in the current view")
        return
    
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
    logger.info("Selected {} instances from {} families".format(total_count, len(selected_families)))
    
    # Confirm large exports
    if total_count > 10000:
        options = ["Yes, proceed with export", "No, cancel export"]
        result = REVIT_FORMS.dialogue(
            title="Large Export Warning",
            main_text="You are about to export {} elements.".format(total_count),
            sub_text="This operation may take a while to complete. Do you want to continue?",
            options=options,
            icon="warning"
        )
        
        if result == options[1]:
            NOTIFICATION.messenger("Export canceled by user")
            return
    
    # Track start time for performance measurement
    start_time = time.time()
    
    # Initialize exporter
    exporter = RevitToRhinoExporter(doc)
    exporter.family_instances = selected_instances
    exporter.setup_document()
    
    # Process elements with progress bar
    def process_element(element):
        exporter.process_element(element)
    
    def label_func(element):
        element_name = "{} - {}".format(
            exporter._get_family_name(element), 
            element.Id.IntegerValue
        )
        return "Exporting: {}".format(element_name)
    
    # Process elements with progress bar
    UI.progress_bar(
        selected_instances,
        process_element,
        label_func=label_func,
        title="Revit2Rhino: Exporting Elements"
    )
    
    # Complete export and save file
    logger.info("Finalizing Rhino file...")
    export_result = exporter.finalize_export()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    hours, mins = divmod(mins, 60)
    
    time_str = ""
    if hours > 0:
        time_str += "{:.0f} hours ".format(hours)
    if mins > 0:
        time_str += "{:.0f} minutes ".format(mins)
    time_str += "{:.1f} seconds".format(secs)
    
    if export_result:
        NOTIFICATION.messenger("Successfully exported to: {}\nTotal time: {}".format(export_result, time_str))
    else:
        NOTIFICATION.messenger("Export failed. Check log for details.\nTotal time: {}".format(time_str))


class RevitToRhinoExporter(object):
    def __init__(self, revit_doc):
        self.revit_doc = revit_doc
        
        # Generate timestamp for filename
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.output_file = os.path.join(ENVIRONMENT.DUMP_FOLDER, "{}_Revit2Rhino_{}.3dm".format(ENVIRONMENT.PLUGIN_NAME, timestamp))
        
        self.rhino_doc = None
        self.family_instances = None
        self.geom_options = None
        
        # Statistics tracking
        self.symbol_geo_count = 0
        self.instance_geo_count = 0
        self.failed_geo_count = 0
        self.layer_dict = {}
        
        # Cache for block definitions
        self.block_cache = {}
        self.block_geo_source = {}
        
        # Get the current document unit
        self.revit_unit = REVIT_UNIT.get_doc_length_unit_name(revit_doc)
        
    def setup_document(self):
        """Initialize Rhino document and geometry options"""
        self.rhino_doc = REVIT_RHINO.setup_rhino_doc(self.revit_doc)
        
        # Create geometry options
        opts = DB.Options()
        opts.DetailLevel = DB.ViewDetailLevel.Fine
        opts.IncludeNonVisibleObjects = True
        self.geom_options = opts
        
        return True
            
    def process_element(self, element):
        """Process a single family instance"""
        return self._process_element(element)
    
    def finalize_export(self):
        """Generate statistics and save the Rhino file"""
        # Print statistics
        logger.info("Geometry source statistics:")
        logger.info("  - Blocks using symbol geometry: {}".format(self.symbol_geo_count))
        logger.info("  - Blocks using instance geometry: {}".format(self.instance_geo_count))
        logger.info("  - Elements with no usable geometry: {}".format(self.failed_geo_count))
        
        # Save the file
        self._write_rhino_file()
        return self.output_file

    def _get_family_name(self, element):
        """Get family name from an element with error handling"""
        try:
            return element.Symbol.FamilyName
        except:
            return "Unknown"

    def _get_type_name(self, element):
        """Get type name from an element with error handling"""
        try:
            return element.Symbol.Name
        except:
            return "NoType"

    def _process_element(self, element):
        """Process a single family instance for export."""
        element_id = element.Id.IntegerValue
        family_name = self._get_family_name(element)
        type_name = self._get_type_name(element)
        symbol_id = element.Symbol.Id.IntegerValue
        
        # Check if we've already created a block for this symbol
        if symbol_id in self.block_cache:
            block_idx = self.block_cache[symbol_id]
            geo_source = self.block_geo_source.get(symbol_id, "Unknown")
            logger.debug("  Using cached block for symbol {}".format(symbol_id))
        else:
            # Extract geometry for this element
            geometry_data = self._get_geometry(element)
            
            if not geometry_data or len(geometry_data) <= 1:
                logger.warning("  WARNING: No valid geometry found for {}".format(family_name))
                self.failed_geo_count += 1
                return
            
            # Update statistics based on geometry source
            geo_source = geometry_data.get("geometry_source", "Unknown")
            if geo_source == "Symbol":
                self.symbol_geo_count += 1
            elif geo_source.startswith("Instance"):
                self.instance_geo_count += 1
            
            # For Instance geometry, untransform it to get it in symbol coordinates
            if geo_source == "Instance" and hasattr(element, "GetTransform"):
                transform = element.GetTransform()
                if transform:
                    geometry_data = self._untransform_geometry(geometry_data, transform)
                    geo_source = geometry_data.get("geometry_source", "Unknown")
            
            # Create a block definition from the geometry
            block_idx = self._create_block_definition(family_name, type_name, geometry_data)
            
            if block_idx < 0:
                logger.error("  ERROR: Failed to create block for {}".format(family_name))
                return
                
            # Cache the block for future instances of the same symbol
            self.block_cache[symbol_id] = block_idx
            self.block_geo_source[symbol_id] = geo_source
        
        # Place a block instance with the element's transformation
        self._place_block_instance(block_idx, element, geo_source)

    def _get_geometry(self, element):
        """Extract geometry from a family instance."""
        family_name = self._get_family_name(element)
        
        # First try to get symbol geometry (preferred)
        symbol_geometry = self._get_symbol_geometry(element.Symbol)
        
        if symbol_geometry and len(symbol_geometry) > 1:  # More than just metadata
            return symbol_geometry
        
        # If symbol geometry failed, try instance geometry
        instance_geometry = self._get_instance_geometry(element)
        
        if instance_geometry and len(instance_geometry) > 1:  # More than just metadata
            return instance_geometry
        
        # If both approaches failed
        return {"geometry_source": "None"}

    def _get_symbol_geometry(self, symbol):
        """Extract geometry directly from a family symbol (untransformed)."""
        try:
            # Initialize result dictionary with geometry source metadata
            geometry_by_subcategory = {"geometry_source": "Symbol"}
            total_objects = 0
            
            # Get the symbol's geometry
            geom_elem = symbol.get_Geometry(self.geom_options)
            if not geom_elem:
                return geometry_by_subcategory
                
            # Process each geometry object
            for geometry_object in geom_elem:
                if isinstance(geometry_object, DB.GeometryInstance):
                    # GetSymbolGeometry returns untransformed geometry
                    symbol_geo = geometry_object.GetSymbolGeometry()
                    if not symbol_geo:
                        continue
                    
                    # Process each geometry object in the symbol
                    for g_obj in symbol_geo:
                        # Get subcategory name for layer assignment
                        subcat_name = self._get_subcategory_name(g_obj)
                        
                        # Convert to Rhino geometry
                        converted = self._convert_revit_geometry(g_obj)
                        
                        if converted:
                            # Add to the appropriate subcategory/layer
                            if subcat_name not in geometry_by_subcategory:
                                geometry_by_subcategory[subcat_name] = []
                            geometry_by_subcategory[subcat_name].extend(converted)
                            total_objects += len(converted)
                
                elif isinstance(geometry_object, DB.Solid) or hasattr(geometry_object, 'Mesh'):
                    # Direct geometry objects in symbol
                    subcat_name = self._get_subcategory_name(geometry_object)
                    
                    converted = self._convert_revit_geometry(geometry_object)
                    
                    if converted:
                        if subcat_name not in geometry_by_subcategory:
                            geometry_by_subcategory[subcat_name] = []
                        geometry_by_subcategory[subcat_name].extend(converted)
                        total_objects += len(converted)
            
            return geometry_by_subcategory
            
        except Exception as e:
            logger.debug("  Error getting symbol geometry: {}".format(str(e)))
            return {"geometry_source": "Symbol"}

    def _get_instance_geometry(self, element):
        """Extract geometry from a family instance (transformed to project coordinates)."""
        try:
            # Initialize result dictionary with geometry source metadata
            geometry_by_subcategory = {"geometry_source": "Instance"}
            total_objects = 0
            
            # Get the instance's geometry
            geom_elem = element.get_Geometry(self.geom_options)
            if not geom_elem:
                return geometry_by_subcategory
                
            # Process each geometry object
            for geometry_object in geom_elem:
                if isinstance(geometry_object, DB.GeometryInstance):
                    # GetInstanceGeometry returns geometry already transformed to project coordinates
                    inst_geo = geometry_object.GetInstanceGeometry()
                    if not inst_geo:
                        continue
                    
                    # Process each geometry object in the instance
                    for g_obj in inst_geo:
                        # Get subcategory name for layer assignment
                        subcat_name = self._get_subcategory_name(g_obj)
                        
                        # Convert to Rhino geometry
                        converted = self._convert_revit_geometry(g_obj)
                        
                        if converted:
                            # Add to the appropriate subcategory/layer
                            if subcat_name not in geometry_by_subcategory:
                                geometry_by_subcategory[subcat_name] = []
                            geometry_by_subcategory[subcat_name].extend(converted)
                            total_objects += len(converted)
                
                elif isinstance(geometry_object, DB.Solid) or hasattr(geometry_object, 'Mesh'):
                    # Direct geometry objects
                    subcat_name = self._get_subcategory_name(geometry_object)
                    
                    converted = self._convert_revit_geometry(geometry_object)
                    
                    if converted:
                        if subcat_name not in geometry_by_subcategory:
                            geometry_by_subcategory[subcat_name] = []
                        geometry_by_subcategory[subcat_name].extend(converted)
                        total_objects += len(converted)
            
            return geometry_by_subcategory
            
        except Exception as e:
            logger.debug("  Error getting instance geometry: {}".format(str(e)))
            return {"geometry_source": "Instance"}

    def _get_subcategory_name(self, g_obj):
        """Get the subcategory name for a geometry object"""
        try:
            if g_obj.GraphicsStyleId and self.revit_doc.GetElement(g_obj.GraphicsStyleId):
                style = self.revit_doc.GetElement(g_obj.GraphicsStyleId)
                if hasattr(style, "GraphicsStyleCategory") and style.GraphicsStyleCategory:
                    return style.GraphicsStyleCategory.Name
        except:
            pass
        
        return "UnCategorized"

    def _convert_revit_geometry(self, g_obj):
        """Convert Revit geometry to Rhino geometry."""
        results = []
        
        # Handle Solids - convert to Breps if volume is significant
        if isinstance(g_obj, DB.Solid):
            if g_obj.Volume > 1e-6:
                try:
                    breps = RIR_DECODER.ToBrep(g_obj)
                    if breps:
                        if isinstance(breps, list):
                            for b in breps:
                                if b:
                                    results.append(b)
                        else:
                            results.append(breps)
                except:
                    pass
                    
        # Handle Meshes
        elif hasattr(g_obj, 'Mesh'):
            revit_mesh = g_obj.Mesh
            if revit_mesh and revit_mesh.NumTriangles > 0:
                try:
                    r_mesh = self._mesh_to_rhino(revit_mesh)
                    results.append(r_mesh)
                except:
                    pass
                
        return results

    def _mesh_to_rhino(self, revit_mesh):
        """Convert a Revit mesh to a Rhino mesh"""
        rhino_mesh = Rhino.Geometry.Mesh()
        
        # Add vertices
        for i in range(revit_mesh.NumVertices):
            rv_vertex = revit_mesh.Vertices[i]
            rhino_mesh.Vertices.Add(rv_vertex.X, rv_vertex.Y, rv_vertex.Z)
            
        # Add triangular faces
        for i in range(revit_mesh.NumTriangles):
            tri = revit_mesh.get_Triangle(i)
            idx0 = tri.get_VertexIndex(0)
            idx1 = tri.get_VertexIndex(1)
            idx2 = tri.get_VertexIndex(2)
            rhino_mesh.Faces.AddFace(idx0, idx1, idx2)
            
        return rhino_mesh

    def _create_block_definition(self, family_name, type_name, geometry_data):
        """Create a Rhino block definition for a family symbol."""
        # Create a block name
        if type_name == "NoType":
            block_name = "{}".format(family_name)
        else:
            block_name = "{}_{}".format(family_name, type_name)
        
        # Remove invalid characters
        block_name = block_name.replace(":", "_").replace("/", "_").replace("\\", "_").replace(" ", "_")
        
        # Collect all geometry and create layers for subcategories
        all_geometry = []
        all_attributes = []
        
        # Check if there's any actual geometry
        has_geometry = False
        for subcat_name, geo_list in geometry_data.items():
            if subcat_name != "geometry_source" and len(geo_list) > 0:
                has_geometry = True
                break
                
        if not has_geometry:
            return -1
            
        # Process each subcategory
        for subcat_name, geo_list in geometry_data.items():
            if subcat_name == "geometry_source" or not geo_list:
                continue
                
            # Create or get layer for this subcategory
            layer_index = self._get_or_create_layer(subcat_name)
            
            for geo in geo_list:
                if geo is None:
                    continue
                    
                all_geometry.append(geo)
                
                # Create attributes for this object that reference the layer
                attrib = Rhino.DocObjects.ObjectAttributes()
                attrib.LayerIndex = layer_index
                all_attributes.append(attrib)
                
                # Keep track of geometry by layer for statistics
                if subcat_name not in self.layer_dict:
                    self.layer_dict[subcat_name] = []
                self.layer_dict[subcat_name].append(geo)
        
        # Final validation
        if not all_geometry:
            return -1
        
        # Create the block definition
        base_point = Rhino.Geometry.Point3d(0, 0, 0)
        
        block_idx = self.rhino_doc.InstanceDefinitions.Add(
            block_name,
            "Created from Revit family",
            base_point,
            all_geometry,
            all_attributes
        )
            
        return block_idx

    def _get_or_create_layer(self, layer_name):
        """Get or create a layer with the given name and return its index"""
        # Check if layer already exists
        layer_index = self.rhino_doc.Layers.FindByFullPath(layer_name, True)
        if layer_index >= 0:
            return layer_index
            
        # Create new layer
        layer = Rhino.DocObjects.Layer()
        layer.Name = layer_name
        
        # Generate a color based on the layer name
        name_hash = hash(layer_name) % 1000
        r = (name_hash * 13) % 256
        g = (name_hash * 17) % 256
        b = (name_hash * 19) % 256
        layer.Color = System.Drawing.Color.FromArgb(r, g, b)
        
        # Add the layer to the document
        return self.rhino_doc.Layers.Add(layer)

    def _revit_transform_to_rhino(self, revit_transform):
        """Convert a Revit transform to a Rhino transform"""
        rhino_transform = Rhino.Geometry.Transform.Identity
        
        # Set basis vectors
        rhino_transform.M00 = revit_transform.BasisX.X
        rhino_transform.M10 = revit_transform.BasisX.Y
        rhino_transform.M20 = revit_transform.BasisX.Z
        
        rhino_transform.M01 = revit_transform.BasisY.X
        rhino_transform.M11 = revit_transform.BasisY.Y
        rhino_transform.M21 = revit_transform.BasisY.Z
        
        rhino_transform.M02 = revit_transform.BasisZ.X
        rhino_transform.M12 = revit_transform.BasisZ.Y
        rhino_transform.M22 = revit_transform.BasisZ.Z
        
        # Set origin (no unit conversion here - we'll handle that separately)
        rhino_transform.M03 = revit_transform.Origin.X
        rhino_transform.M13 = revit_transform.Origin.Y
        rhino_transform.M23 = revit_transform.Origin.Z
        
        return rhino_transform

    def _untransform_geometry(self, geometry_data, transform):
        """Untransform geometry extracted with GetInstanceGeometry() to get it back to symbol space."""
        # Make a copy of the input data
        result = dict(geometry_data)
        
        try:
            # If there's no geometry other than metadata, return as is
            if len(geometry_data) <= 1 and "geometry_source" in geometry_data:
                return result
                
            # Create the inverse transform to get back to symbol space
            inverse_transform = transform.Inverse
            
            # Convert the inverse transform to a Rhino transform
            rhino_inverse = self._revit_transform_to_rhino(inverse_transform)
            
            # Process each subcategory
            for subcat_name, geo_list in list(result.items()):
                if subcat_name == "geometry_source":
                    continue
                    
                # Create a new list for the untransformed geometry
                untransformed_list = []
                
                # Apply inverse transform to each geometry object
                for geo in geo_list:
                    try:
                        # Create a duplicate to avoid modifying the original
                        geo_copy = geo.Duplicate()
                        geo_copy.Transform(rhino_inverse)
                        untransformed_list.append(geo_copy)
                    except:
                        untransformed_list.append(geo)  # Keep original if transform fails
                
                # Replace the original list with the untransformed one
                result[subcat_name] = untransformed_list
            
            # Update the geometry source in the metadata
            result["geometry_source"] = "Instance_Untransformed"
            
            return result
        except:
            return geometry_data  # Return original data if anything fails

    def _place_block_instance(self, block_idx, element, geo_source):
        """Place a block instance in the Rhino document with the element's transformation."""
        # Get the element's transformation
        instance_transform = self._get_element_transform_no_scale(element)
        
        # Create a block instance with the transformation
        instance_id = self.rhino_doc.Objects.AddInstanceObject(block_idx, instance_transform)
        
        # Add element metadata if successful
        if instance_id:
            inst_obj = self.rhino_doc.Objects.FindId(instance_id)
            if inst_obj:
                element_id = element.Id.IntegerValue
                
                # Add metadata as user strings
                inst_obj.Attributes.SetUserString("RevitElementID", str(element_id))
                family_name = self._get_family_name(element)
                type_name = self._get_type_name(element)
                inst_obj.Attributes.SetUserString("FamilyName", family_name)
                inst_obj.Attributes.SetUserString("TypeName", type_name)
                
                inst_obj.CommitChanges()

    def _get_element_transform_no_scale(self, element):
        """Get a Rhino transform from a Revit family instance."""
        # Get the element's transform
        revit_transform = element.GetTransform()
        if revit_transform is None:
            return Rhino.Geometry.Transform.Identity
          
        # Create a new Rhino transform
        rhTrans = Rhino.Geometry.Transform.Identity

        # Copy basis vectors from Revit transform
        rhTrans.M00 = revit_transform.BasisX.X
        rhTrans.M10 = revit_transform.BasisX.Y
        rhTrans.M20 = revit_transform.BasisX.Z
        rhTrans.M30 = 0.0

        rhTrans.M01 = revit_transform.BasisY.X
        rhTrans.M11 = revit_transform.BasisY.Y
        rhTrans.M21 = revit_transform.BasisY.Z
        rhTrans.M31 = 0.0

        rhTrans.M02 = revit_transform.BasisZ.X
        rhTrans.M12 = revit_transform.BasisZ.Y
        rhTrans.M22 = revit_transform.BasisZ.Z
        rhTrans.M32 = 0.0

        # Convert origin coordinates to the proper units
        origin_x = REVIT_UNIT.internal_to_unit(revit_transform.Origin.X, self.revit_unit)
        origin_y = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Y, self.revit_unit)
        origin_z = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Z, self.revit_unit)
        
        rhTrans.M03 = origin_x
        rhTrans.M13 = origin_y
        rhTrans.M23 = origin_z
        rhTrans.M33 = 1.0
        
        return rhTrans

    def _write_rhino_file(self):
        """Write the Rhino document to a 3DM file and open it"""
        # Configure file write options
        write_option = Rhino.FileIO.FileWriteOptions()
        write_option.FileVersion = 7  # Save as Rhino 7 3dm
        
        # Zoom extents to all objects before saving
        if self.rhino_doc.Objects.Count > 0:
            # Get all objects' bounding box
            bbox = Rhino.Geometry.BoundingBox.Empty
            for obj in self.rhino_doc.Objects:
                if obj.Geometry is not None:
                    bbox.Union(obj.Geometry.GetBoundingBox(True))
            
            # Set all active views to this bounding box
            if bbox.IsValid:
                # Add some padding to the bounding box (10%)
                pad = bbox.Diagonal.Length * 0.1
                bbox.Inflate(pad, pad, pad)
                
                for view in self.rhino_doc.Views:
                    view.ActiveViewport.ZoomBoundingBox(bbox)
                    view.Redraw()
        
        # Write the file and dispose the document
        self.rhino_doc.Write3dmFile(self.output_file, write_option)
        self.rhino_doc.Dispose()
        
        # Open the file
        os.startfile(self.output_file)


if __name__ == "__main__":
    revit2rhino(DOC)
