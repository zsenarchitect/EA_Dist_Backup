__title__ = "Shape2Revit"
__doc__ = """Convert EACH and EVERY selected geometry to INDIVIDUAL Revit families via temporary blocks.\nNot to be confused with the block2family button, which exports better defined blocks to Revit families and is much more memory efficient.\nOnly use this button sparingly so you do not introduce too many families to Revit.\n\nFeatures:\n- Converts surfaces, polysurfaces and meshes to blocks\n- Creates temporary blocks with unique names\n- Exports blocks to Revit families\n- Cleans up temporary blocks after export\n- Maintains original geometry properties"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab import ENVIRONMENT, ERROR_HANDLE, LOG, NOTIFICATION, DATA_FILE
from EnneadTab.RHINO import RHINO_OBJ_DATA, RHINO_UI
import Eto # pyright: ignore
import Rhino # pyright: ignore
import System

import os
import sys
# Add the block2family.button directory to sys.path
current_dir = os.path.dirname(__file__)
block2family_dir = os.path.abspath(os.path.join(current_dir, '..', 'block2family.button'))
if block2family_dir not in sys.path:
    sys.path.insert(0, block2family_dir)
import block2family_left as B2F

PREFIX = "{}_CONVERT_".format(ENVIRONMENT.PLUGIN_ABBR)

class Shape2RevitDialog(Eto.Forms.Dialog[bool]):
    def __init__(self):
        self.Title = "Shape2Revit"
        self.Padding = Eto.Drawing.Padding(10)
        self.Resizable = True
        self.MinimumSize = Eto.Drawing.Size(400, 300)
        
        # Create layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(10)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        # Add description
        description = Eto.Forms.Label()
        description.Text = __doc__
        description.Wrap = Eto.Forms.WrapMode.Word
        layout.AddRow(description)
        
        # Add checkbox
        self.never_show = Eto.Forms.CheckBox()
        self.never_show.Text = "Never show this dialog again"
        layout.AddRow(self.never_show)
        
        # Add buttons
        button_layout = Eto.Forms.DynamicLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 0)
        
        self.confirm_button = Eto.Forms.Button(Text = "Confirm")
        self.confirm_button.Click += self.on_confirm
        
        self.cancel_button = Eto.Forms.Button(Text = "Cancel")
        self.cancel_button.Click += self.on_cancel
        
        button_layout.AddRow(None, self.confirm_button, self.cancel_button)
        layout.AddRow(button_layout)
        
        self.Content = layout
        RHINO_UI.apply_dark_style(self)
        
    def on_confirm(self, sender, e):
        if self.never_show.Checked:
            DATA_FILE.set_sticky("SHAPE2REVIT_NEVER_SHOW", True)
        self.Close(True)
        
    def on_cancel(self, sender, e):
        self.Close(False)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def shape2revit():
    # Check if we should show the dialog
    if not DATA_FILE.get_sticky("SHAPE2REVIT_NEVER_SHOW", False):
        dialog = Shape2RevitDialog()
        result = Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        if not result:
            return
    
    # Get geometry with specific filters
    filter_value = rs.filter.surface | rs.filter.polysurface | rs.filter.mesh
    geos = rs.GetObjects("Select geometry to convert to Revit families, blocks will be ignored. Note this is a inefficent usage of revit, and will impact revit performance significantly.", filter_value)
    if not geos:
        return

    rs.EnableRedraw(False)
    temp_block_collection = []
    
    # Process each geometry
    for geo in geos:
        # Get bounding box center for insertion point
        bbox = rs.BoundingBox(geo)
        if not bbox:
            continue
        center = RHINO_OBJ_DATA.get_center(geo)
        
        # Create temporary block name
        block_name = "{}{}".format(PREFIX, str(geo)) # using guid from rs.parsing
        
        # Create block from geometry
        if rs.IsBlock(block_name):
            rs.DeleteBlock(block_name)
        rs.AddBlock([geo], center, name=block_name, delete_input=False)
        
        # Insert block instance
        temp_block = rs.InsertBlock(block_name, center)
        if not temp_block:
            continue
        
        # Copy user data from original geometry to block instance
        user_keys = rs.GetUserText(geo)
        if user_keys:
            for key in user_keys:
                value = rs.GetUserText(geo, key)
                rs.SetUserText(temp_block, key, value)
        
        temp_block_collection.append(temp_block)

    B2F.block2family(temp_block_collection)
    rs.DeleteObjects(temp_block_collection)
    for block_name in rs.BlockNames():
        rs.DeleteBlock(block_name) if block_name.startswith(PREFIX) else None
    
    NOTIFICATION.messenger("Conversion complete!")
    
if __name__ == "__main__":
    shape2revit()
