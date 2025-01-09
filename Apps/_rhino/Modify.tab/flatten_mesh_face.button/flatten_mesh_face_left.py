__title__ = "FlattenMeshFace"
__doc__ = "Try to flatten the mesh face so there is no bump"

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab import LOG, ERROR_HANDLE, DATA_CONVERSION
import Eto # pyright: ignore
import os
import time
import System # pyright: ignore     
from System.Drawing import Bitmap, Rectangle # pyright: ignore
from System.Drawing.Imaging import PixelFormat, ImageFormat, FrameDimension, PropertyItem # pyright: ignore
import System.Windows.Forms.Screen as Screen # pyright: ignore
from System.IO import MemoryStream # pyright: ignore
import traceback
class MeshFlattener:
    def __init__(self):
        self.strength = 0.1
        self.max_steps = 100  # Default steps
        self.mesh_id = None
        self.dot_name = "EA_mesh_flat_face_marker"
        self.tolerance = sc.doc.ModelAbsoluteTolerance * 10

    def show_strength_dialog(self):
        # Change Dialog to Form
        form = Eto.Forms.Form()
        form.Title = "Mesh Flattener Settings"
        form.Topmost = True  # Keep form on top
        form.Resizable = False  # Instead of MinimizeButton/MaximizeButton
        form.MinimumSize = Eto.Drawing.Size(300, 150)  # Set a reasonable size
        
        # Create inputs
        strength_label = Eto.Forms.Label(Text="Flattening Strength:")
        self.strength_input = Eto.Forms.NumericStepper()
        self.strength_input.Value = self.strength
        self.strength_input.MinValue = 0.1
        self.strength_input.MaxValue = 1.0
        self.strength_input.DecimalPlaces = 2
        self.strength_input.Increment = 0.1
        
        steps_label = Eto.Forms.Label(Text="Max Steps:")
        self.steps_input = Eto.Forms.NumericStepper()
        self.steps_input.Value = self.max_steps
        self.steps_input.MinValue = 1
        self.steps_input.MaxValue = 500
        self.steps_input.DecimalPlaces = 0
        
        # Add a close handler
        def on_form_closing(sender, e):
            form.Close()
        form.Closing += on_form_closing
        
        # Layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(10)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.AddRow(strength_label, self.strength_input)
        layout.AddRow(steps_label, self.steps_input)
        
        select_button = Eto.Forms.Button()
        select_button.Text = "Select Mesh"
        select_button.Click += self.on_select_mesh
        
        ok_button = Eto.Forms.Button()
        ok_button.Text = "Start Flattening"  # Changed text to be more descriptive
        ok_button.Click += self.on_ok_clicked
        
        btn_layout = Eto.Forms.DynamicLayout()
        btn_layout.AddRow(None, select_button)
        btn_layout.AddRow(None, ok_button)
        layout.AddRow(btn_layout)
        
        form.Content = layout
        # Show instead of ShowModal
        form.Show()
        return True  # Return True to continue execution
        
    def on_select_mesh(self, sender, e):
        self.mesh_id = rs.GetObject(message="Pick one mesh to flatten", filter=32, preselect=True)
        if self.mesh_id:
            sender.Text = "Mesh Selected"
            sender.BackgroundColor = Eto.Drawing.Colors.LightGreen

    def on_ok_clicked(self, sender, e):
        if not self.mesh_id:
            rs.MessageBox("Please select a mesh first!")
            return
        
        self.strength = self.strength_input.Value
        self.max_steps = int(self.steps_input.Value)
        

        
        mesh_obj = sc.doc.Objects.FindId(self.mesh_id)
        if not mesh_obj:
            rs.MessageBox("Selected mesh is no longer valid!")
            return

        backup_mesh = rs.CopyObject(mesh_obj)
        rs.HideObject(backup_mesh)
        
        mesh = mesh_obj.Geometry
        obj_attribute = mesh_obj.Attributes

        step = 0
        prev_mesh = None
        
        try:
            while step < self.max_steps:
                mesh = self.process_mesh(mesh)
                print("######### Steps {}#####".format(step + 1))
                
                # Check if mesh has stabilized
                if prev_mesh and mesh.Vertices.Count == prev_mesh.Vertices.Count:
                    max_movement = 0
                    for i in range(mesh.Vertices.Count):
                        dist = mesh.Vertices[i].DistanceTo(prev_mesh.Vertices[i])
                        max_movement = max(max_movement, dist)
                    if max_movement < self.tolerance:
                        print("Mesh stabilized after {} steps".format(step + 1))
                        break
                    
                if mesh_obj:
                    rs.DeleteObject(mesh_obj)
                mesh_obj = sc.doc.Objects.AddMesh(mesh, obj_attribute)
                rs.Redraw()
                
                prev_mesh = mesh.Duplicate()
                step += 1
                
                if step % 50 == 0:
                    self.highlight_planar_region(mesh)
        finally:
            # Show all objects again
            rs.ShowObject(backup_mesh)

            pass

        sender.ParentWindow.Close()

    def process_vertex(self, index, vertex, mesh):
        connected_face_indexs = mesh.TopologyVertices.ConnectedFaces(index)
        face_normals = mesh.FaceNormals
        face_normals.ComputeFaceNormals()
        
        connected_face_normals = [face_normals[x] for x in connected_face_indexs]
        connected_face_centers = [mesh.Faces.GetFaceCenter(x) for x in connected_face_indexs]
        
        temp_planes = [Rhino.Geometry.Plane(center, normal) for center, normal in zip(connected_face_centers, connected_face_normals)]
        
        vec = Rhino.Geometry.Vector3d(0,0,0)
        for plane in temp_planes:
            project_pt = plane.ClosestPoint(vertex)
            project_pt = Rhino.Geometry.Point3d(project_pt)
            vertex = Rhino.Geometry.Point3d(vertex)
            
            raw_vec = Rhino.Geometry.Vector3d(project_pt - vertex)
            # Use the user-defined strength
            current_strength = self.strength
            if raw_vec.Length > 0:
                current_strength *= max(0.1, min(1.0, 1.0 / (raw_vec.Length * 2)))
            
            vec += raw_vec * current_strength
        
        final_pt = vertex + vec
        return final_pt

    def highlight_planar_region(self, mesh):
        dot_name = "EA_mesh_flat_face_marker"
        dots = rs.ObjectsByName(dot_name)
        #rs.DeleteObjects(dots)
        tolerance = sc.doc.ModelAbsoluteTolerance
        for i, face in enumerate(mesh.Faces):
            if face.IsTriangle:
                dot = rs.AddTextDot("flat", mesh.Faces.GetFaceCenter(i))
                rs.ObjectName(dot, name = dot_name)
                continue

            face_corners = [face.A, face.B, face.C, face.D]
            face_corners = [Rhino.Geometry.Point3d(mesh.Vertices[x]) for x in face_corners]
            #print face_corners

            face_corners = DATA_CONVERSION.list_to_system_list(face_corners, type = Rhino.Geometry.Point3d)
            test_crv = Rhino.Geometry.PolylineCurve(face_corners)

            if test_crv.IsPlanar(tolerance):
                # print("is flat face")
                dot = rs.AddTextDot("flat", mesh.Faces.GetFaceCenter(i))
                rs.ObjectName(dot, name = dot_name)


        dots = rs.ObjectsByName(dot_name)
        rs.AddObjectsToGroup(dots, rs.AddGroup())

    def process_mesh(self, mesh):
        # all_face normals(not normals, that is for the vertice)
        # all topologyvetivecs


        topo_vertice = mesh.TopologyVertices

        new_topo_vertice_new_locations = [self.process_vertex(index, vertex, mesh) for index, vertex in enumerate(topo_vertice)]
        for index, topo_vertex in enumerate(topo_vertice):
            mesh_vertex_ids = topo_vertice.MeshVertexIndices (index)
            for mesh_vertex_id in mesh_vertex_ids:
                mesh.Vertices .SetVertex(mesh_vertex_id, new_topo_vertice_new_locations[index])
        return mesh

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def flatten_mesh_face():
    """Main function to create and show the mesh flattener dialog"""
    flattener = MeshFlattener()
    # Show the dialog but don't proceed with mesh processing yet
    flattener.show_strength_dialog()
    # Return something explicitly to avoid 'out' variable issue
    return True

if __name__ == "__main__":
    flatten_mesh_face()