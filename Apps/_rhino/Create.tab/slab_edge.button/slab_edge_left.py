__title__ = "SlabEdge"
__doc__ = """Create custom slab edges by sweeping a profile block along selected edges.

This tool allows users to:
- Select individual edges or edge loops from a slab
- Choose a profile block to use as the edge detail
- Preview the result before finalizing
- Flip the profile orientation if needed

The tool maintains a live preview and allows for easy adjustments before finalizing the slab edge creation.
"""

import select
import rhinoscriptsyntax as rs
import Rhino # pyright:ignore
import scriptcontext as sc
import Eto # pyright:ignore
from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.RHINO import RHINO_SELECTION, RHINO_UI

FORM_KEY = 'slab_edge_modeless_form'

class SlabEdgeDialog(Eto.Forms.Form):
    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        self.Title = "Slab Edge"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        
        self.height = 300
        self.width = 900
        
        self.Closed += self.OnFormClosed
        
        # Create layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        # Create group box for selection methods
        selection_group = Eto.Forms.GroupBox(Text="Pick one method")
        selection_group.Padding = Eto.Drawing.Padding(5)
        selection_layout = Eto.Forms.DynamicLayout()
        selection_layout.Padding = Eto.Drawing.Padding(5)
        selection_layout.Spacing = Eto.Drawing.Size(5, 5)
        
        # Create labels and buttons
        self.select_edge_label = Eto.Forms.Label(Text="Select Edge(no edge loops):")
        self.select_edge_button = Eto.Forms.Button(Text="Select Edges")
        self.select_edge_button.Click += self.on_select_edge_click

        self.select_crv_label = Eto.Forms.Label(Text= "Select Crvs")
        self.select_crv_button = Eto.Forms.Button(Text = "Select Crvs")
        self.select_crv_button.Click += self.on_select_crv_click
        
        # Add selection methods to group layout
        selection_layout.AddRow(self.select_edge_label, self.select_edge_button)
        selection_layout.AddSeparateRow(Eto.Forms.Label(Text= "..or.."))
        selection_layout.AddRow(self.select_crv_label, self.select_crv_button)
        selection_group.Content = selection_layout
        
        # Add other controls
        self.profile_label = Eto.Forms.Label(Text="Select profile block to sweep:")
        self.profile_button = Eto.Forms.Button(Text="Select Profile Block")
        self.profile_button.Click += self.on_profile_click
        
        self.flip_label = Eto.Forms.Label(Text="Flip profile direction:")
        self.flip_button = Eto.Forms.Button(Text="Flip Profile")
        self.flip_button.Click += self.on_flip_click
        
        self.preview_label = Eto.Forms.Label(Text="Preview slab edge:")
        self.preview_button = Eto.Forms.Button(Text="Preview")
        self.preview_button.Click += self.on_preview_click
        
        self.confirm_label = Eto.Forms.Label(Text="Confirm and generate:")
        self.confirm_button = Eto.Forms.Button(Text="Confirm")
        self.confirm_button.Click += self.on_confirm_click
        
        # Add all controls to main layout
        layout.AddRow(None, selection_group)

        layout.AddRow(self.profile_label, self.profile_button)
        layout.AddRow(self.flip_label, self.flip_button)
        layout.AddRow(self.preview_label, self.preview_button)
        layout.AddRow(self.confirm_label, self.confirm_button)
        
        self.Content = layout
        RHINO_UI.apply_dark_style(self)
        
        # Initialize state
        self.selected_edges = None
        self.profile_block = None
        self.is_flipped = False

    @ERROR_HANDLE.try_catch_error()
    def on_select_edge_click(self, sender, e):
        selection = RHINO_SELECTION.select_subelements(include_face=False, 
                                                     include_edge=True, 
                                                     include_vertex=False, 
                                                     include_edgeloop=False)
        if selection:
            edges = selection.get("edge", [])
            edge_loops = selection.get("edge_loop", [])
            self.selected_edges = edges + edge_loops
            
            sender.Text = "Edges Selected"
            sender.BackgroundColor = Eto.Drawing.Colors.DarkGreen
            self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def on_select_crv_click(self,sender,e):
        selection = rs.GetObjects(filter=rs.filter.curve)
        if selection:
            self.selected_edges = [sc.doc.Objects.Find(x).CurveGeometry  for x in selection]
            sender.Text = "Crvs Selected"
            sender.BackgroundColor = Eto.Drawing.Colors.DarkGreen
            self.on_preview_click(None, None)
            

    @ERROR_HANDLE.try_catch_error()
    def on_profile_click(self, sender, e):
        crv_profile_block = rs.GetObject("pick block of profile", filter=rs.filter.instance)
        if crv_profile_block:
            self.profile_block = crv_profile_block
            sender.Text = "Profile Selected"
            sender.BackgroundColor = Eto.Drawing.Colors.DarkGreen
            self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def on_flip_click(self, sender, e):
        self.is_flipped = not self.is_flipped
        sender.Text = "Profile Flipped" if self.is_flipped else "Flip Profile"
        sender.BackgroundColor = Eto.Drawing.Colors.Orange if self.is_flipped else Eto.Drawing.Colors.DarkGray
        self.on_preview_click(None, None)

    @ERROR_HANDLE.try_catch_error()
    def generate_slab_edge(self, is_preview=False):
        if not self.selected_edges:
            NOTIFICATION.messenger("Please select guiding rail first!")
            return
            
        if not self.profile_block:
            NOTIFICATION.messenger("Please select a profile block first!")
            return

        rs.EnableRedraw(False)

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

        self.out = []
        
        for edge in edges:
            temp_edge = sc.doc.Objects.AddCurve(edge)

            start_pt = rs.CurveStartPoint(temp_edge)
            t = rs.CurveClosestPoint(temp_edge, start_pt)
            crv_plane = rs.CurvePerpFrame(temp_edge,t)

            if not crv_plane:
                print("no plane at crv")
                continue
            
                
            xform_final = Rhino.Geometry.Transform.PlaneToPlane(profile_plane, crv_plane)
            copy_profile = rs.TransformObjects(temp_profile_objs, xform_final, True)
            
            sweep = rs.AddSweep1(edge, copy_profile, True)
            rs.CapPlanarHoles(sweep)
            self.out.append(sweep)
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
        NOTIFICATION.messenger("{} Slab edge geometry added.".format(len(self.out)))

        self.selected_edges = None
        RHINO_UI.apply_styles_to_control(self.select_edge_button)
        RHINO_UI.apply_styles_to_control(self.select_crv_button)
        self.select_edge_button.Text = "Select edges"
        self.select_crv_button.Text = "Select Crvs"
            
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
