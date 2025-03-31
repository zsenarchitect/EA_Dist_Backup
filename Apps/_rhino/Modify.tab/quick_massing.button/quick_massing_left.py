__title__ = "QuickMassing"
__doc__ = "This button does QuickMassing when left click"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Eto.Forms as Forms # pyright: ignore
import Eto.Drawing as Drawing # pyright: ignore
import Rhino # pyright: ignore
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.RHINO import RHINO_UI

FORM_KEY = 'quick_massing_modeless_form'

class QuickMassingDialog(Forms.Form):
    def __init__(self):
        self.Title = "Quick Massing Settings"
        self.Resizable = True
        self.Padding = Drawing.Padding(5)
        self.Spacing = Drawing.Size(5, 5)
        
        self.height = 300
        self.width = 300
        
        self.Closed += self.OnFormClosed
        
        # Create layout
        layout = Forms.DynamicLayout()
        layout.Padding = Drawing.Padding(5)
        layout.Spacing = Drawing.Size(5, 5)
        
        # Create inputs
        first_level_label = Forms.Label(Text="First Level Height:")
        self.first_level_input = Forms.TextBox()
        self.first_level_input.Text = str(DATA_FILE.get_sticky("quick_massing_first_level", 6.0, DATA_FILE.DataType.FLOAT, tiny_wait=True))
        self.first_level_input.TextChanged += self.check_input

        typical_level_label = Forms.Label(Text="Typical Level Height:")
        self.typical_level_input = Forms.TextBox()
        self.typical_level_input.Text = str(DATA_FILE.get_sticky("quick_massing_typical_level", 4.5, DATA_FILE.DataType.FLOAT, tiny_wait=True))
        self.typical_level_input.TextChanged += self.check_input
        
        level_count_label = Forms.Label(Text="Typical Level Count:")
        self.level_count_input = Forms.TextBox()
        self.level_count_input.Text = str(DATA_FILE.get_sticky("quick_massing_typical_level_count", 4, DATA_FILE.DataType.INT))
        self.level_count_input.TextChanged += self.check_input

     
        # Add rows to layout
        layout.AddRow(first_level_label, self.first_level_input)
        layout.AddRow(typical_level_label, self.typical_level_input)
        layout.AddRow(level_count_label, self.level_count_input)
        
        # Create buttons
        self.ok_button = Forms.Button(Text="Create Massing")
        self.ok_button.Click += self.on_ok_clicked
        
        self.cancel_button = Forms.Button(Text="Cancel")
        self.cancel_button.Click += self.on_cancel_clicked
        
        layout.AddRow(None, self.ok_button, self.cancel_button)
        
        self.Content = layout
        RHINO_UI.apply_dark_style(self)


    def check_input(self):
        def validate_input(input_text, input_type, error_message):
            while True:
                try:
                    return True, input_type(input_text)
                except ValueError:
                    NOTIFICATION.messenger(error_message)
                    return False, None

        status, self.first_level = validate_input(self.first_level_input.Text, float, "Please enter a valid number for first level")
        if not status:
            return False
        status, self.typical_level = validate_input(self.typical_level_input.Text, float, "Please enter a valid number for typical level")
        if not status:
            return False
        status, self.typical_level_count = validate_input(self.level_count_input.Text, int, "Please enter a valid number for typical level count")
        if not status:
            return False

        return True

                

    def on_ok_clicked(self, sender, e):
        if not self.check_input():
            return
        self.first_level = float(self.first_level_input.Text)
        self.typical_level = float(self.typical_level_input.Text)
        self.typical_level_count = int(self.level_count_input.Text)
       
                
        self.Close()

        self.create_massing()

        
        DATA_FILE.set_sticky("quick_massing_first_level", self.first_level, DATA_FILE.DataType.FLOAT, tiny_wait=True)
        DATA_FILE.set_sticky("quick_massing_typical_level", self.typical_level, DATA_FILE.DataType.FLOAT, tiny_wait=True)
        DATA_FILE.set_sticky("quick_massing_typical_level_count", self.typical_level_count, DATA_FILE.DataType.INT)


    def create_massing(self):
            

            
        objs = rs.GetObjects("Select objects to quick massing", preselect=True, filter=rs.filter.surface)
        if not objs:
            return

        rs.EnableRedraw(False)

        levels = [self.first_level]
        for _ in range(self.typical_level_count):
            levels.append(self.typical_level)

        for obj in objs:
            ref_pt = [0,0,0]
            
            for level in levels:
                crv = rs.AddCurve([ref_pt, rs.PointAdd(ref_pt, [0,0,level])])
                ref_pt = rs.PointAdd(ref_pt, [0,0,level])
                backup_obj = rs.CopyObject(obj, [0,0,level])
                mass_obj = rs.ExtrudeSurface(obj, crv)
                rs.DeleteObject(obj)
                rs.DeleteObject(crv)
                obj = backup_obj
            rs.DeleteObject(obj)
    

        rs.EnableRedraw(True)

        
    def on_cancel_clicked(self, sender, e):
        self.Close()
        
    def OnFormClosed(self, sender, e):
        if sc.sticky.has_key(FORM_KEY):
            del sc.sticky[FORM_KEY]
        self.Close()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def quick_massing():
    if sc.sticky.has_key(FORM_KEY):
        return
        
    dlg = QuickMassingDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg

    
if __name__ == "__main__":
    quick_massing()
