__title__ = "Dockpane"
__doc__ = "A dockpane with text input and selection controls"

import rhinoscriptsyntax as rs
import Rhino
import Eto.Forms as Forms
import Eto.Drawing as Drawing
import scriptcontext as sc
from EnneadTab import ERROR_HANDLE, LOG

FORM_KEY = 'dockpane_modeless_forsm'

class DockpaneDialog(Forms.Dialog[bool]):
    def __init__(self):
        self.Title = "Dockpane"
        self.Padding = Drawing.Padding(5)
        self.Resizable = True
        self.MinimumSize = Drawing.Size(200, 150)
        
        # Create controls
        self.textbox = Forms.TextBox()
        self.textbox.Width = 200
        
        self.print_button = Forms.Button(Text="Print Text")
        self.print_button.Click += self.on_print_click
        
        self.select_button = Forms.Button(Text="Select All")
        self.select_button.Click += self.on_select_click
        
        self.close_button = Forms.Button(Text="Close")
        self.close_button.Click += self.on_close_click
        
        # Create layout
        layout = Forms.DynamicLayout()
        layout.Padding = Drawing.Padding(5)
        layout.Spacing = Drawing.Size(5, 5)
        
        layout.AddRow(self.textbox)
        layout.AddRow(self.print_button)
        layout.AddRow(self.select_button)
        layout.AddRow(self.close_button)
        
        self.Content = layout
        
    def on_print_click(self, sender, e):
        print(self.textbox.Text)
        
    def on_select_click(self, sender, e):
        doc = Rhino.RhinoDoc.ActiveDoc
        objects = doc.Objects.FindByFilter(Rhino.DocObjects.ObjectEnumeratorSettings())
        for obj in objects:
            obj.Select(True)
        doc.Views.Redraw()
        
    def on_close_click(self, sender, e):
        self.Close()
        
    def OnFormClosed(self, sender, e):
        if sc.sticky.has_key(FORM_KEY):
            del sc.sticky[FORM_KEY]
        self.Close()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dockpane():
    """Create and show a dockpane with text input and selection controls"""
    if sc.sticky.has_key(FORM_KEY):
        return
        
    dlg = DockpaneDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
    sc.sticky[FORM_KEY] = dlg
    
if __name__ == "__main__":
    dockpane()
