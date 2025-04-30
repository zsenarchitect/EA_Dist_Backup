__title__ = "Dockpane"
__doc__ = "A dockable panel that attaches to the side of Rhino window"

import rhinoscriptsyntax as rs
import Rhino
import Eto.Forms as forms
import Eto.Drawing as drawing
import scriptcontext as sc
import System
from EnneadTab import ERROR_HANDLE, LOG

class DockablePanel(forms.Panel):
    def __init__(self):
        super(DockablePanel, self).__init__()
        self.Title = "Dockpane"
        self.Padding = drawing.Padding(5)
        
        # Create controls
        self.textbox = forms.TextBox()
        self.textbox.Width = 200
        
        self.print_button = forms.Button(Text="Print Text")
        self.print_button.Click += self.on_print_click
        
        self.select_button = forms.Button(Text="Select All")
        self.select_button.Click += self.on_select_click
        
        # Create layout
        layout = forms.DynamicLayout()
        layout.Padding = drawing.Padding(5)
        layout.Spacing = drawing.Size(5, 5)
        
        layout.AddRow(self.textbox)
        layout.AddRow(self.print_button)
        layout.AddRow(self.select_button)
        
        self.Content = layout
    
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

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dockpane():
    """Create and show a dockable panel that attaches to the side of Rhino window"""
    # Create and register the panel
    panel = DockablePanel()
    Rhino.UI.Panels.RegisterPanel(panel, "EnneadTab Dockpane", System.Drawing.SystemIcons.Application.ToBitmap(), Rhino.UI.Panels.PanelType.Floating)
    
if __name__ == "__main__":
    dockpane()
