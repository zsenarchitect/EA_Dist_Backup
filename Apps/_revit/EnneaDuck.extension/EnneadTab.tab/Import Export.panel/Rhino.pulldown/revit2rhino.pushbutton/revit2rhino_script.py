#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ ="""
Script for exporting Revit Family Instances to Rhino.
It converts each FamilyInstance's geometry into a **single Rhino block** containing all its Breps
(or fallback Meshes). The block definition is annotated with 'RevitElementID'.


This only process current view.

TO-DO: accept layer making

"""


__title__ = "Revit2Rhino"

import clr  # pyright: ignore

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

# Example references to other modules in your environment
import proDUCKtion  # pyright: ignore
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, UI, ENVIRONMENT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT, REVIT_RHINO
from Autodesk.Revit import DB  # pyright: ignore

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def revit2rhino(doc):
    if not IMPORT_OK:
        NOTIFICATION.messenger("Please initate Rhino Inside First")
        return
    
    exporter = RevitToRhinoExporter(doc)
    exporter.export_family_instances()
    

class RevitToRhinoExporter(object):
    def __init__(self, revit_doc):
        self.revit_doc = revit_doc
        self.output_file = r"C:\\Temp\\{}RevitSelectionHelper.3dm".format(ENVIRONMENT.PLUGIN_NAME)
        self.rhino_doc = None

    def export_family_instances(self):
        """Collects FamilyInstances, creates a block for each instance,
        scales geometry from feet->mm, places block with only rotation+translation,
        and saves the result to a 3DM file."""
        self.rhino_doc = REVIT_RHINO.setup_rhino_doc(self.revit_doc)
        geom_options = self._create_geometry_options()
        family_instances = self._collect_family_instances()

        for i, element in enumerate(family_instances):
            if i % 5 == 0:
                NOTIFICATION.messenger("Exporting {} of {} elements".format(i+1, len(family_instances)))
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

    def _process_element(self, element, geom_options):
        """Converts Revit geometry to Rhino objects (in feet), scales them to mm,
        then creates a block definition. Finally places a block instance at the
        element's rotation+translation, ignoring scale (since geometry is already scaled)."""
        geom_elem = element.get_Geometry(geom_options)
        if not geom_elem:
            return

        element_geometry = []
        for geometry_object in geom_elem:
            if isinstance(geometry_object, DB.GeometryInstance):
                true_geo = geometry_object.GetSymbolGeometry()
                true_geo = geometry_object.GetInstanceGeometry ()
                if not true_geo:
                    continue
                for g_obj in true_geo:
                    
                    converted = self._convert_revit_geometry(g_obj)
                    if converted:
                        element_geometry.extend(converted)

        if element_geometry:


            # Create block definition
            block_idx = self._create_block_for_element(element.Id.IntegerValue, element_geometry)
            if block_idx >= 0:
                self._place_block_instance(block_idx, element)

    def _convert_revit_geometry(self, g_obj):
        """Convert a single Revit geometry object (Solid or Mesh) to Rhino geometry in feet.
        We do NOT scale it here."""
        if self.revit_doc.GetElement(g_obj.GraphicsStyleId):
            sub_c = self.revit_doc.GetElement(g_obj.GraphicsStyleId).GraphicsStyleCategory
            print (sub_c.Name)
        # results = {
        #     "meta_data":{
        #         "layer":sub_c.Name
        #         },
        #     "geo":[]
        #     }
        results = []
        if isinstance(g_obj, DB.Solid) and g_obj.Volume > 1e-6:
            breps = RIR_DECODER.ToBrep(g_obj)
            if not breps:
                return results
            if isinstance(breps, list):
                for b in breps:
                    if b:
                        # results["geo"].append(b)
                        results.append(b)
            else:
                results.append(breps)
        elif hasattr(g_obj, 'Mesh'):
            revit_mesh = g_obj.Mesh
            if revit_mesh and revit_mesh.NumTriangles > 0:
                r_mesh = self._mesh_to_rhino(revit_mesh)
                # results["geo"].append(r_mesh)
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



    def _create_block_for_element(self, element_id, geometry_data):
        """Create a new block definition from scaled geometry (in mm). Returns block index."""
        block_name = "Element_{}".format(element_id)
        attributes = []
        base_point = Rhino.Geometry.Point3d(0, 0, 0)

        # Create the block definition now that geometry is in mm
        block_idx = self.rhino_doc.InstanceDefinitions.Add(
            block_name,
            "Created from Revit element",
            base_point,
            geometry_data,
            attributes
        )

        if block_idx < 0:
            print("Warning: block with name {} already exists.".format(block_name))
            return -1

        return block_idx

    def _place_block_instance(self, block_idx, element):
        """Place an instance of the block using Revit's rotation+translation only.
        We do not scale here because geometry was already scaled.
        Also set user string 'RevitElementID' on the instance object."""
        instance_transform = self._get_element_transform_no_scale(element)
        instance_id = self.rhino_doc.Objects.AddInstanceObject(block_idx, instance_transform)
        if instance_id:
            inst_obj = self.rhino_doc.Objects.FindId(instance_id)
            if inst_obj:
                inst_obj.Attributes.SetUserString("RevitElementID", str(element.Id.IntegerValue))
                inst_obj.CommitChanges()

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

        # Origin
      
        rhTrans.M03 = REVIT_UNIT.internal_to_unit(revit_transform.Origin.X , self.revit_unit)
        rhTrans.M13 = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Y , self.revit_unit)
        rhTrans.M23 = REVIT_UNIT.internal_to_unit(revit_transform.Origin.Z , self.revit_unit)
        rhTrans.M33 = 1.0

        return rhTrans

    def _write_rhino_file(self):
        write_option = Rhino.FileIO.FileWriteOptions()
        write_option.FileVersion = 7  # Save as Rhino 7 3dm
        self.rhino_doc.Write3dmFile(self.output_file, write_option)
        self.rhino_doc.Dispose()
        NOTIFICATION.messenger("Successfully exported Revit FamilyInstances to Rhino file: {0}".format(self.output_file))
        os.startfile(self.output_file)

################## main code below #####################
if __name__ == "__main__":
    revit2rhino(DOC)
