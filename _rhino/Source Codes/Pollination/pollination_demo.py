import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

"""
Create a simple report on runtime to check rooms
------------------------------------------------------------------------------
Instructions:
    1. Run the script
------------------------------------------------------------------------------
Strategy:
    1. Get all Pollination Rooms
    2. Use Honeybee for reporting
"""

# import rhinocommon and Eto
import Rhino # pyright: ignore
import System # pyright: ignore
import Rhino # pyright: ignore.UI
import Eto # pyright: ignore.Drawing as drawing
import Eto # pyright: ignore.Forms as forms

# import pollination part
import clr # pyright: ignore
clr.AddReference('Pollination.Core.dll')
clr.AddReference('HoneybeeSchema.dll')
import HoneybeeSchema as hb # csharp version of HB Schema
import Core as po # It contains Pollination RhinoObject classes
import Core.Convert as co # It contains utilities to convert RhinoObject <> HB Schema

# import List collection
from System.Collections.Generic import List # pyright: ignore

try:  # import honeybee dependencies
    import io
    import csv
    import json
    import honeybee.dictutil as hb_dict_util
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import:\n\t{}'.format(e))

# SELECTION PART
#---------------------------------------------------------------------------------------------#
# doc info
doc = Rhino.RhinoDoc.ActiveDoc
tol = doc.ModelAbsoluteTolerance
a_tol = doc.ModelAngleToleranceRadians
current_model = po.Entity.ModelEntityTable.Instance.CurrentModelEntity
doc_unit = Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem

# get all objects
objects = Rhino.RhinoDoc.ActiveDoc.Objects

# filter by rooms
rooms = [_ for _ in objects if isinstance(_, po.Objects.RoomObject)]

if not rooms:
    raise ValueError('No rooms found.')

# REPORTING PART
#---------------------------------------------------------------------------------------------#

# define Eto grid
class RoomGridView(forms.Dialog[bool]):
    
    def __init__(self, data):
        unit = str(doc_unit).lower()
        
        self._data = data
        self.Title = "Room report"
        self.Resizable = True
        self.m_gridview = forms.GridView()
        self.m_gridview.ShowHeader = True
        self.m_gridview.DataStore = data
        self.m_gridview.Height = 300
        
        self._header = ('display_name', 'floor_area [{}2]'.format(unit),
        'volume [{}3]'.format(unit), 'exposed_area [{}2]'.format(unit),
        'exterior_wall_aperture_area [{}2]'.format(unit), 
        'exterior_wall_area [{}2]'.format(unit))
        
        column1 = forms.GridColumn()
        column1.HeaderText = self._header[0]
        column1.Editable = True
        column1.DataCell = forms.TextBoxCell(0)
        self.m_gridview.Columns.Add(column1)

        column2 = forms.GridColumn()
        column2.HeaderText = self._header[1]
        column2.Editable = True
        column2.DataCell = forms.TextBoxCell(1)
        self.m_gridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = self._header[2]
        column3.Editable = True
        column3.DataCell = forms.TextBoxCell(2)
        self.m_gridview.Columns.Add(column3)

        column4 = forms.GridColumn()
        column4.HeaderText = self._header[3]
        column4.Editable = True
        column4.DataCell = forms.TextBoxCell(3)
        self.m_gridview.Columns.Add(column4)
        
        column5 = forms.GridColumn()
        column5.HeaderText = self._header[4]
        column5.Editable = True
        column5.DataCell = forms.TextBoxCell(4)
        self.m_gridview.Columns.Add(column5)
        
        column6 = forms.GridColumn()
        column6.HeaderText = self._header[5]
        column6.Editable = True
        column6.DataCell = forms.TextBoxCell(5)
        self.m_gridview.Columns.Add(column6)
        
        self.m_button = forms.Button(self.OnSaveButton)
        self.m_button.Text = 'Save File'
        
        layout = forms.DynamicLayout()
        layout.Padding = drawing.Padding(10)
        layout.Spacing = drawing.Size(5, 5)
        layout.Add(self.m_gridview)
        layout.Add(self.m_button)
        
        self.save_dialog = forms.SaveFileDialog()
        self.save_dialog.Title = 'Save File As'
        self.save_dialog.FileName = '{}.csv'.format(Rhino.RhinoDoc.ActiveDoc.Name)
        
        self.Content = layout
    
    def OnSaveButton(self, s, e):
        result = self.save_dialog.ShowDialog(self.m_gridview)
        
        # write csv ironpython 2
        if result == forms.DialogResult.Ok:
            with io.open(self.save_dialog.FileName, 'w', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(self._header)
                writer.writerows(self._data)
            
            forms.MessageBox.Show(self, "Done!", self.Title)


    
    
    
@EnneadTab.ERROR_HANDLE.try_catch_error
def pollination_demo():
    # create the dataset
    data = []
    for rm in rooms:
        hb_dict = json.loads(rm.ToHBObject().ToJson())
        hb_room = hb_dict_util.dict_to_object(hb_dict, False)
        numeric = [hb_room.floor_area, \
                    hb_room.volume, hb_room.exposed_area, hb_room.exterior_wall_aperture_area, \
                    hb_room.exterior_wall_area]
        numeric = map(int, numeric)
        
        row = [hb_room.display_name]
        row.extend(numeric)
        
        data.append(row)

    # show the table
    if rooms:
        dialog = RoomGridView(data)
        rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    


######################  main code below   #########
if __name__ == "__main__":

    pollination_demo()




