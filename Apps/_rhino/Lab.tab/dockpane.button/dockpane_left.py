# -*- coding: utf-8 -*-
__title__ = "Dockpane"
__doc__ = "A dockable panel that attaches to the side of Rhino window"

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import Eto.Forms as forms # pyright: ignore
import Eto.Drawing as drawing # pyright: ignore
import scriptcontext as sc
import System # pyright: ignore
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT
from Rhino.UI import Panels # pyright: ignore


class DockablePanel(forms.Panel):
    def __init__(self):
        super(DockablePanel, self).__init__()
        self.Title = ENVIRONMENT.PLUGIN_NAME + " Panel"
        self.Padding = drawing.Padding(5)
        
        # Create controls
        self.create_controls()
        
        # Create layout
        self.create_layout()
    
    def create_controls(self):
        # Text section
        self.text_label = forms.Label(Text="Enter Text:")
        self.textbox = forms.TextBox()
        self.textbox.Width = 200
        self.print_button = forms.Button(Text="Print Text")
        self.print_button.Click += self.on_print_click
        
        # Selection section
        self.selection_label = forms.Label(Text="Objects:")
        self.select_button = forms.Button(Text="Select All")
        self.select_button.Click += self.on_select_click
        self.filter_button = forms.Button(Text="Select Lines Only")
        self.filter_button.Click += self.on_filter_click
        
        # Layer section
        self.layer_label = forms.Label(Text="Active Layer:")
        self.layer_dropdown = forms.DropDown()
        self.update_layer_list()
        self.layer_dropdown.SelectedIndexChanged += self.on_layer_changed
        self.add_layer_button = forms.Button(Text="Add New Layer")
        self.add_layer_button.Click += self.on_add_layer_click
        
        # Color section
        self.color_label = forms.Label(Text="Color:")
        self.color_picker = forms.ColorPicker()
        self.color_picker.Value = drawing.Colors.Red
        self.apply_color_button = forms.Button(Text="Apply Color")
        self.apply_color_button.Click += self.on_apply_color_click
    
    def create_layout(self):
        layout = forms.DynamicLayout()
        layout.Padding = drawing.Padding(10)
        layout.Spacing = drawing.Size(5, 10)
        
        # Add text section
        layout.AddRow(self.text_label)
        layout.AddRow(self.textbox)
        layout.AddRow(self.print_button)
        
        # Add spacing
        layout.AddRow(None)
        layout.AddRow(forms.Label(Text="─────────────"))
        layout.AddRow(None)
        
        # Add selection section
        layout.AddRow(self.selection_label)
        layout.AddRow(self.select_button)
        layout.AddRow(self.filter_button)
        
        # Add spacing
        layout.AddRow(None)
        layout.AddRow(forms.Label(Text="─────────────"))
        layout.AddRow(None)
        
        # Add layer section
        layout.AddRow(self.layer_label)
        layout.AddRow(self.layer_dropdown)
        layout.AddRow(self.add_layer_button)
        
        # Add spacing
        layout.AddRow(None)
        layout.AddRow(forms.Label(Text="─────────────"))
        layout.AddRow(None)
        
        # Add color section
        layout.AddRow(self.color_label)
        layout.AddRow(self.color_picker)
        layout.AddRow(self.apply_color_button)
        
        self.Content = layout
    
    def update_layer_list(self):
        self.layer_dropdown.Items.Clear()
        for layer in Rhino.RhinoDoc.ActiveDoc.Layers:
            self.layer_dropdown.Items.Add(layer.Name)
        if self.layer_dropdown.Items.Count > 0:
            self.layer_dropdown.SelectedIndex = 0
    
    @ERROR_HANDLE.try_catch_error()    
    def on_print_click(self, sender, e):
        print(self.textbox.Text)
    
    @ERROR_HANDLE.try_catch_error()    
    def on_select_click(self, sender, e):
        doc = Rhino.RhinoDoc.ActiveDoc
        objects = doc.Objects.FindByFilter(Rhino.DocObjects.ObjectEnumeratorSettings())
        for obj in objects:
            obj.Select(True)
        doc.Views.Redraw()
    
    @ERROR_HANDLE.try_catch_error()    
    def on_filter_click(self, sender, e):
        doc = Rhino.RhinoDoc.ActiveDoc
        # Clear current selection
        doc.Objects.UnselectAll()
        
        # Only select curve objects
        settings = Rhino.DocObjects.ObjectEnumeratorSettings()
        settings.ObjectTypeFilter = Rhino.DocObjects.ObjectType.Curve
        objects = doc.Objects.FindByFilter(settings)
        
        for obj in objects:
            obj.Select(True)
        doc.Views.Redraw()
    
    @ERROR_HANDLE.try_catch_error()    
    def on_layer_changed(self, sender, e):
        selected_layer = self.layer_dropdown.SelectedValue
        if selected_layer:
            rs.CurrentLayer(selected_layer)
    
    @ERROR_HANDLE.try_catch_error()    
    def on_add_layer_click(self, sender, e):
        # Create a timestamp-based layer name instead of using GUID
        import time
        timestamp = int(time.time())
        new_layer_name = "NewLayer_{}".format(timestamp)
        rs.AddLayer(new_layer_name)
        self.update_layer_list()
        # Select the newly created layer
        for i, layer in enumerate(self.layer_dropdown.Items):
            if layer == new_layer_name:
                self.layer_dropdown.SelectedIndex = i
                break
    
    @ERROR_HANDLE.try_catch_error()    
    def on_apply_color_click(self, sender, e):
        doc = Rhino.RhinoDoc.ActiveDoc
        objects = doc.Objects.GetSelectedObjects(False, False)
        if not objects:
            print("No objects selected. Please select objects first.")
            return
            
        # Convert Eto color to Rhino color
        eto_color = self.color_picker.Value
        rhino_color = System.Drawing.Color.FromArgb(eto_color.Rb, eto_color.Gb, eto_color.Bb)
        
        for obj in objects:
            obj.Attributes.ObjectColor = rhino_color
            obj.Attributes.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
            obj.CommitChanges()
        
        doc.Views.Redraw()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dockpane():
    """Create and show a dockable panel that attaches to the side of Rhino window"""
    # Create and register the panel
    panel_id = System.Guid("12345678-1234-1234-1234-123456789012")  # Use a fixed GUID for the panel
    
    # Check if panel already exists
    existing_panel = Panels.GetPanel(panel_id)
    if existing_panel:
        Panels.ClosePanel(panel_id)
    
    # Create new panel
    panel = DockablePanel()
    
    # Try to load a custom bitmap
    try:
        icon_path = Rhino.PlugIns.PlugIn.PathFromName("EnneadTab") + "\\resources\\rhino\\dockpanel.png"
        panel_bitmap = System.Drawing.Bitmap.FromFile(icon_path)
    except:
        # Use default bitmap if loading fails
        panel_bitmap = System.Drawing.SystemIcons.Application.ToBitmap()
        
    # Get the plugin instance
    plugin = Rhino.PlugIns.PlugIn.Find("EnneadTab")
    # Register with the plugin and panel class
    Panels.RegisterPanel(plugin, DockablePanel, "EnneadTab Dockpane", panel_bitmap)
    
    # Show the panel
    Panels.OpenPanel("EnneadTab Dockpane")
    
if __name__ == "__main__":
    dockpane()
