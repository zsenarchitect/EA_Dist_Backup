__title__ = "MoveFixedDist"
__doc__ = """Move selected objects a fixed distance in 6 directions.

Features:
- Simple modeless interface with 6 directional buttons
- Persistent distance value between sessions
- Input validation for numeric values
- North/South/East/West/Up/Down movement
- Safe window handling to prevent UI errors
- Allows full interaction with Rhino while dialog is open
- Gamepad-style button layout
- Zoom to selected function"""


from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.RHINO import RHINO_UI
import rhinoscriptsyntax as rs # pyright: ignore
import scriptcontext as sc # pyright: ignore
import Rhino # pyright: ignore
import Eto # pyright: ignore
import System # pyright: ignore

FORM_KEY = 'move_fixed_dist_modeless_form'

class MoveFixedDistDialog(Eto.Forms.Form):
    def __init__(self):
        self.Title = "Move Fixed Distance"
        self.Padding = Eto.Drawing.Padding(10)
        self.Resizable = False
        self.ShowInTaskbar = False
        self.TopMost = True  # Make dialog stay on top
        
        # Get saved distance value
        self.distance = DATA_FILE.get_sticky("move_fixed_dist_value", 1.0)
        
        # Create distance input
        distance_label = Eto.Forms.Label(Text="Distance:")
        self.distance_textbox = Eto.Forms.TextBox(Text=str(self.distance))
        self.distance_textbox.KeyDown += self.on_distance_keydown
        self.distance_textbox.LostFocus += self.on_distance_changed
        
        # Validation message
        self.validation_label = Eto.Forms.Label(Text="")
        self.validation_label.TextColor = Eto.Drawing.Colors.Red
        
        # Create direction buttons
        north_button = Eto.Forms.Button(Text="North")
        north_button.Click += self.on_north_click
        
        south_button = Eto.Forms.Button(Text="South")
        south_button.Click += self.on_south_click
        
        east_button = Eto.Forms.Button(Text="East")
        east_button.Click += self.on_east_click
        
        west_button = Eto.Forms.Button(Text="West")
        west_button.Click += self.on_west_click
        
        up_button = Eto.Forms.Button(Text="Up")
        up_button.Click += self.on_up_click
        
        down_button = Eto.Forms.Button(Text="Down")
        down_button.Click += self.on_down_click
        
        # Create zoom button
        zoom_button = Eto.Forms.Button(Text="Zoom Selected")
        zoom_button.Click += self.on_zoom_click
        
        # Create layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        # Add controls to layout
        layout.AddSeparateRow(distance_label, self.distance_textbox)
        layout.AddRow(self.validation_label)
        
        # Create button layout according to sketch
        button_layout = Eto.Forms.TableLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 5)
        button_layout.Padding = Eto.Drawing.Padding(5)
        
        # Row 1: North
        button_layout.Rows.Add(Eto.Forms.TableRow(None, north_button, None))
        
        # Row 2: West, Zoom, East
        button_layout.Rows.Add(Eto.Forms.TableRow(west_button, zoom_button, east_button))
        
        # Row 3: South
        button_layout.Rows.Add(Eto.Forms.TableRow(None, south_button, None))
        
        layout.AddRow(button_layout)
        

        
        layout.AddSeparateRow(None, up_button, down_button, None)
        
        self.Content = layout
        
        # Apply EnneadTab dark style
        RHINO_UI.apply_dark_style(self)
        
        # Set form closed event handler
        self.Closed += self.OnFormClosed
    
    def validate_distance(self):
        try:
            value = float(self.distance_textbox.Text)
            if value <= 0:
                self.validation_label.Text = "Value must be greater than 0"
                return False
            self.validation_label.Text = ""
            self.distance = value
            DATA_FILE.set_sticky("move_fixed_dist_value", value)
            return True
        except:
            self.validation_label.Text = "Invalid number format"
            return False
    
    def on_distance_keydown(self, sender, e):
        if e.Key == Eto.Forms.Keys.Enter:
            self.validate_distance()
    
    def on_distance_changed(self, sender, e):
        self.validate_distance()
    
    def move_objects(self, direction_vector):
        # Check if any objects are selected
        selected_objects = rs.SelectedObjects()
        if not selected_objects:
            NOTIFICATION.messenger("No objects selected")
            return
        
        # Validate distance
        if not self.validate_distance():
            return
        
        # Create movement vector
        move_vector = rs.VectorScale(direction_vector, self.distance)
        
        # Move objects
        rs.MoveObjects(selected_objects, move_vector)
    
    def on_north_click(self, sender, e):
        self.move_objects([0, self.distance, 0])
    
    def on_south_click(self, sender, e):
        self.move_objects([0, -self.distance, 0])
    
    def on_east_click(self, sender, e):
        self.move_objects([self.distance, 0, 0])
    
    def on_west_click(self, sender, e):
        self.move_objects([-self.distance, 0, 0])
    
    def on_up_click(self, sender, e):
        self.move_objects([0, 0, self.distance])
    
    def on_down_click(self, sender, e):
        self.move_objects([0, 0, -self.distance])
    
    def on_zoom_click(self, sender, e):
        # Check if any objects are selected
        selected_objects = rs.SelectedObjects()
        if not selected_objects:
            NOTIFICATION.messenger("No objects selected")
            return
        
        # Zoom to selected objects
        rs.ZoomSelected()
    
    def OnFormClosed(self, sender, e):
        if sc.sticky.has_key(FORM_KEY):
            del sc.sticky[FORM_KEY]

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def move_fixed_dist():
    # If the dialog is already shown, just return
    if sc.sticky.has_key(FORM_KEY):
        return
        
    # Create a new dialog
    dlg = MoveFixedDistDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg

if __name__ == "__main__":
    move_fixed_dist()
