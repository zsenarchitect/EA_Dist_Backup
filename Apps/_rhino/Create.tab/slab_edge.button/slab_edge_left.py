__title__ = "SlabEdge"
__doc__ = "This button does SlabEdge when left click"

import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import Eto.Forms as Forms
import Eto.Drawing as Drawing
from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.RHINO import RHINO_SELECTION, RHINO_UI

FORM_KEY = 'slab_edge_modeless_form'

class SlabEdgeDialog(Forms.Form):
    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        self.Title = "Slab Edge"
        self.Resizable = True
        self.Padding = Drawing.Padding(5)
        self.Spacing = Drawing.Size(5, 5)
        
        self.height = 300
        self.width = 900
        
        self.Closed += self.OnFormClosed
        
        # Create layout
        layout = Forms.DynamicLayout()
        layout.Padding = Drawing.Padding(5)
        layout.Spacing = Drawing.Size(5, 5)
        
        # Create labels and buttons
        self.select_label = Forms.Label(Text="Select edge(no edge loops):")
        self.select_button = Forms.Button(Text="Select Edges")
        self.select_button.Click += self.on_select_click
        
        self.profile_label = Forms.Label(Text="Select profile block to sweep:")
        self.profile_button = Forms.Button(Text="Select Profile Block")
        self.profile_button.Click += self.on_profile_click
        
        self.flip_label = Forms.Label(Text="Flip profile direction:")
        self.flip_button = Forms.Button(Text="Flip Profile")
        self.flip_button.Click += self.on_flip_click
        
        self.preview_label = Forms.Label(Text="Preview slab edge:")
        self.preview_button = Forms.Button(Text="Preview")
        self.preview_button.Click += self.on_preview_click
        
        self.confirm_label = Forms.Label(Text="Confirm and generate:")
        self.confirm_button = Forms.Button(Text="Confirm")
        self.confirm_button.Click += self.on_confirm_click
        
        # Add rows to layout
        layout.AddRow(self.select_label)
        layout.AddRow(self.select_button)
        layout.AddRow(self.profile_label)
        layout.AddRow(self.profile_button)
        layout.AddRow(self.flip_label)
        layout.AddRow(self.flip_button)
        layout.AddRow(self.preview_label)
        layout.AddRow(self.preview_button)
        layout.AddRow(self.confirm_label)
        layout.AddRow(self.confirm_button)
        
        self.Content = layout
        RHINO_UI.apply_dark_style(self)
        
        # Initialize state
        self.selected_edges = None
        self.profile_block = None
        self.is_flipped = False

    @ERROR_HANDLE.try_catch_error()
    def on_select_click(self, sender, e):
        selection = RHINO_SELECTION.select_subelements(include_face=False, 
                                                     include_edge=True, 
                                                     include_vertex=False, 
                                                     include_edgeloop=False)
        if selection:
            edges = selection.get("edge", [])
            edge_loops = selection.get("edge_loop", [])
            self.selected_edges = edges + edge_loops
            
            sender.Text = "Edges Selected"
            sender.BackgroundColor = Drawing.Colors.DarkGreen
            self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def on_profile_click(self, sender, e):
        crv_profile_block = rs.GetObject("pick block of profile", filter=rs.filter.instance)
        if crv_profile_block:
            self.profile_block = crv_profile_block
            sender.Text = "Profile Selected"
            sender.BackgroundColor = Drawing.Colors.DarkGreen
            self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def on_flip_click(self, sender, e):
        self.is_flipped = not self.is_flipped
        sender.Text = "Profile Flipped" if self.is_flipped else "Flip Profile"
        sender.BackgroundColor = Drawing.Colors.Orange if self.is_flipped else Drawing.Colors.DarkGray
        self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def generate_slab_edge(self, is_preview=False):
        if not self.selected_edges:
            NOTIFICATION.messenger("Please select edges first!")
            return
            
        if not self.profile_block:
            NOTIFICATION.messenger("Please select a profile block first!")
            return

        rs.EnableRedraw(False)
        # Remove existing preview objects if any
        if is_preview:
            for obj in rs.ObjectsByName("TEMP_SLAB_EDGE"):
                rs.DeleteObject(obj)
            
        block_name = rs.BlockInstanceName(self.profile_block)
        temp_profile_objs = rs.BlockObjects(block_name)
        # Flip the profile if needed
        if self.is_flipped:
            profile_plane = rs.PlaneFromPoints([0,0,0], [-1,0,0], [0,1,0])
        else:
            profile_plane = rs.PlaneFromPoints([0,0,0], [1,0,0], [0,1,0])

        tolerance = 2.1 * sc.doc.ModelAbsoluteTolerance
        edges = Rhino.Geometry.Curve.JoinCurves(self.selected_edges, tolerance)
        
        for edge in edges:
            temp_edge = sc.doc.Objects.AddCurve(edge)

            start_pt = rs.CurveStartPoint(temp_edge)
            t = rs.CurveClosestPoint(temp_edge, start_pt)
            crv_plane = rs.CurvePerpFrame(temp_edge,t)
            
                
            xform_final = Rhino.Geometry.Transform.PlaneToPlane(profile_plane, crv_plane)
            copy_profile = rs.TransformObjects(temp_profile_objs, xform_final, True)
            
            sweep = rs.AddSweep1(edge, copy_profile, True)
            if is_preview:
                rs.ObjectName(sweep, "TEMP_SLAB_EDGE")
                
            rs.DeleteObject(copy_profile)
            rs.DeleteObject(temp_edge)

        rs.EnableRedraw(True)

    @ERROR_HANDLE.try_catch_error()
    def on_preview_click(self, sender, e):
        self.generate_slab_edge(is_preview=True)

    @ERROR_HANDLE.try_catch_error()
    def on_confirm_click(self, sender, e):
        # Remove any existing preview objects
        for obj in rs.ObjectsByName("TEMP_SLAB_EDGE"):
            rs.DeleteObject(obj)
        self.generate_slab_edge(is_preview=False)
            
    def OnFormClosed(self, sender, e):
        # Remove any existing preview objects
        for obj in rs.ObjectsByName("TEMP_SLAB_EDGE"):
            rs.DeleteObject(obj)
        if sc.sticky.has_key(FORM_KEY):
            del sc.sticky[FORM_KEY]
        self.Close()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def slab_edge():
    if sc.sticky.has_key(FORM_KEY):
        return
        
    dlg = SlabEdgeDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg
    
if __name__ == "__main__":
    slab_edge()
