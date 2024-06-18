import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")

import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)




import System # pyright: ignore
import Rhino # pyright: ignore.UI
import Eto # pyright: ignore
import random
import os
FORM_KEY = 'game_sound_modeless_form'


class GameSound(Eto.Forms.Form):

    # Initializer
    def __init__(self):
        self.is_sound_enabled = True
        self.previous_index = None
        self.play_sound(["battle_control_online_1.wav",
                         "battle_control_online_2.wav",
                     "establishing_battlefield_control_stand_by.wav"],
                        is_announcer=True)
        self.m_selecting = False
        self.set_outline_distance()
        
        
        # Basic form initialization
        self.Initialize()
        # Create the form's controls
        self.CreateFormControls()
        # Fill the form's listbox
        self.FillListBox()
        # Create Rhino event handlers
        self.CreateEvents()


    def set_outline_distance(self):
        unit = rs.UnitSystemName(capitalize=False, singular=True, abbreviate=False, model_units=True)

        def get_factor(unit):
            if unit == "millimeter":
                return 200
            if unit == "meter":
                return 0.2
            if unit == "inch":
                return 20
            if unit == "foot":
                return 1
            return 1, "{0} x {0}".format(unit)
        self.outline_offset = get_factor(unit)





    # Basic form initialization
    def Initialize(self):
        self.Title = 'Game Sound My Rhino'
        self.Padding = Eto.Drawing.Padding(5)
        self.Resizable = True
        self.Maximizable = False
        self.Minimizable = False
        self.ShowInTaskbar = False
        self.MinimumSize = Eto.Drawing.Size(200, 150)

        self.test_list = "@@@@@@@@@"
        
        self.logo = Eto.Forms.ImageView()
        logo_path = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun\red alert logo.png"
        temp_bitmap = Eto.Drawing.Bitmap(logo_path)
        self.logo.Image = temp_bitmap.WithSize(400,400)
        # FormClosed event handler
        self.Closed += self.OnFormClosed

    # Adds a listitem to the listbox
    def AddObject(self, obj):
        item = Eto.Forms.ListItem()
        item.Text = obj.ShortDescription(False)
        if obj.Name:
            item.Text += " - " + obj.Name
        item.Tag = obj.Id
        self.m_listbox.Items.Add(item)
        self.update_UI()

    # Fills the listbox with document objects
    def FillListBox(self):
        iter = Rhino.DocObjects.ObjectEnumeratorSettings()
        iter.NormalObjects = True
        iter.LockedObjects = False
        iter.IncludeLights = True
        iter.IncludeGrips = False
        objects = sc.doc.Objects.GetObjectList(iter)
        for obj in objects:
            self.AddObject(obj)

    # CloseDocument event handler
    def OnCloseDocument(self, sender, e):
        self.m_listbox.Items.Clear()
        self.play_sound(["battle_control_terminated.wav",
                         "mission_accomplished.wav"], is_announcer=True)

    # NewDocument event handler
    def OnNewDocument(self, sender, e):
        self.FillListBox()
        self.play_sound(["battle_control_online_1.wav",
                         "battle_control_online_2.wav",
                     "establishing_battlefield_control_stand_by.wav",
                     "new_rally_point_established.wav"],
                        is_announcer=True)

    # EndOpenDocument event handler
    def OnEndOpenDocument(self, sender, e):
        self.FillListBox()
        self.play_sound(["battle_control_online_1.wav",
                         "battle_control_online_2.wav",
                     "establishing_battlefield_control_stand_by.wav"],
                        is_announcer=True)

    # OnAddRhinoObject event handler
    def OnAddRhinoObject(self, sender, e):
        self.play_sound(["construction_compelete_1.wav",
                         "construction_compelete_2.wav",
                         "unit_ready_1.wav",
                         "unit_ready_2.wav",
                         "building_1.wav",
                         "building_2.wav"], 
                        is_announcer=True)
        self.AddObject(e.TheObject)

    # OnDeleteRhinoObject event handler
    def OnDeleteRhinoObject(self, sender, e):
        self.play_sound(["tech_building_lost.wav",
                         "unit_sold.wav",
                         "structure_sold_1.wav",
                         "structure_sold_2.wav",
                         "unit_lost_1.wav",
                         "unit_lost_2.wav"], is_announcer=True)
        for item in self.m_listbox.Items:
            if item.Tag == e.ObjectId:
                self.m_listbox.Items.Remove(item)
                break
        self.update_UI()

    # OnSelectObjects event handler
    def OnSelectObjects(self, sender, e):
        self.play_sound()
        # rs.EnableRedraw(False)
        if self.m_selecting == True:
            return
        if e.RhinoObjects.Length == 1:
            i = 0
            for item in self.m_listbox.Items:
                if item.Tag == e.RhinoObjects[0].Id:
                    self.m_listbox.SelectedIndex = i
                    break
                else:
                    i += 1
        else:
            self.m_listbox.SelectedIndex = -1
            
        self.update_UI()
        
        self.outline_animated(e.RhinoObjects)

        # rs.EnableRedraw(True)

    # OnDeselectAllObjects event handler
    def OnDeselectAllObjects(self, sender, e):
        if self.m_selecting == True:
            return
        self.m_listbox.SelectedIndex = -1
        self.update_UI()
        
    def OnChangingGroup(self, sender, e):
        
        self.play_sound(["reinforcement_have_arrived.wav"], is_announcer=True)

    def OnChangingLayer(self, sender, e):
        
        self.play_sound(["new_rally_point_established.wav"], is_announcer=True)
        
    def OnChangingAttr(self, sender, e):
        return
        self.play_sound(["new_rally_point_established.wav"], is_announcer=True)
        
    def update_UI(self):
        self.msg_lb.Text = 'Rhino Objects:{}'.format(len(self.m_listbox.Items)) 

    # Create Rhino event handlers
    def CreateEvents(self):
        Rhino.RhinoDoc.CloseDocument += self.OnCloseDocument
        Rhino.RhinoDoc.NewDocument += self.OnNewDocument
        Rhino.RhinoDoc.EndOpenDocument += self.OnEndOpenDocument
        Rhino.RhinoDoc.AddRhinoObject += self.OnAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject += self.OnDeleteRhinoObject
        Rhino.RhinoDoc.SelectObjects += self.OnSelectObjects
        Rhino.RhinoDoc.DeselectAllObjects += self.OnDeselectAllObjects
        Rhino.RhinoDoc.GroupTableEvent += self.OnChangingGroup
        Rhino.RhinoDoc.LayerTableEvent += self.OnChangingLayer
        Rhino.RhinoDoc.ModifyObjectAttributes  += self.OnChangingAttr

    # Remove Rhino event handlers
    def RemoveEvents(self):
        Rhino.RhinoDoc.CloseDocument -= self.OnCloseDocument
        Rhino.RhinoDoc.NewDocument -= self.OnNewDocument
        Rhino.RhinoDoc.EndOpenDocument -= self.OnEndOpenDocument
        Rhino.RhinoDoc.AddRhinoObject -= self.OnAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject -= self.OnDeleteRhinoObject
        Rhino.RhinoDoc.SelectObjects -= self.OnSelectObjects
        Rhino.RhinoDoc.DeselectAllObjects -= self.OnDeselectAllObjects
        Rhino.RhinoDoc.GroupTableEvent -= self.OnChangingGroup
        Rhino.RhinoDoc.LayerTableEvent -= self.OnChangingLayer
        Rhino.RhinoDoc.ModifyObjectAttributes  -= self.OnChangingAttr
        

    
    
    # Create all of the controls used by the form
    def CreateFormControls(self):
        # Create table layout
        layout = Eto.Forms.TableLayout()
        layout.Padding = Eto.Drawing.Padding(10)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        # Add controls to layout
        if hasattr(self, "m_listbox"):
            self.msg_lb = Eto.Forms.Label(Text = 'Rhino Objects:' + len(self.m_listbox.Items))
        else:
            self.msg_lb = Eto.Forms.Label(Text = 'Rhino Objects:' )
            
        layout.Rows.Add(self.logo)
        layout.Rows.Add(Eto.Forms.Label(Text = 'Commander, any object selected/created/deleted will cue the soundtrack.' ))
        layout.Rows.Add(Eto.Forms.Label(Text = '------------' ))
        layout.Rows.Add(self.msg_lb)
        layout.Rows.Add(self.CreateListBoxRow())
        layout.Rows.Add(self.CreateButtonRow())
        # Set the content
        self.Content = layout
        
        # EnneadTab.RHINO.RHINO_UI.apply_dark_style(self)

    # Listbox.SelectedIndexChanged event handler
    def OnSelectedIndexChanged(self, sender, e):
        index = self.m_listbox.SelectedIndex
        if index == self.previous_index:
            return
        if index >= 0:
            self.m_selecting = True
            item = self.m_listbox.Items[index]
            Rhino.RhinoApp.RunScript("_SelNone", False)
            Rhino.RhinoApp.RunScript("_SelId " + item.Tag.ToString() + " _Enter", False)
            self.m_selecting = False
            rs.ZoomSelected()
            self.previous_index = index

    # Called by CreateFormControls to creates the
    # table row that contains the listbox
    def CreateListBoxRow(self):
        # Create the listbox
        self.m_listbox = Eto.Forms.ListBox()
        self.m_listbox.Size = Eto.Drawing.Size(200, 100)
        self.m_listbox.SelectedIndexChanged += self.OnSelectedIndexChanged
        # Create the table row
        table_row = Eto.Forms.TableRow()
        table_row.ScaleHeight = True
        table_row.Cells.Add(self.m_listbox)
        return table_row

    # 'Select' button click handler
    def OnSelectClick(self, sender, e):
        self.m_selecting = True
        self.m_listbox.SelectedIndex = -1
        Rhino.RhinoApp.RunScript("_SelAll", False)
        self.m_selecting = False
        
        self.play_sound()

    # 'Clear' button click handler
    def OnClearClick(self, sender, e):
        self.m_selecting = True
        self.m_listbox.SelectedIndex = -1
        Rhino.RhinoApp.RunScript("_SelNone", False)
        self.m_selecting = False

    # Called by CreateFormControls to creates the
    # table row that contains the button controls.
    def CreateButtonRow(self):
        # Select button
        select_button = Eto.Forms.Button(Text = 'Select All')
        select_button.Click += self.OnSelectClick
        # Clear button
        clear_button = Eto.Forms.Button(Text = 'Clear')
        clear_button.Click += self.OnClearClick
        # Create layout
        layout = Eto.Forms.TableLayout(Spacing = Eto.Drawing.Size(5, 5))
        layout.Rows.Add(Eto.Forms.TableRow(None, select_button, clear_button, None))
        return layout

    # Form Closed event handler
    def OnFormClosed(self, sender, e):
        self.play_sound(["battle_control_terminated.wav",
                         "mission_accomplished.wav"], is_announcer=True)
        # Remove the events added in the initializer
        self.RemoveEvents()
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key(FORM_KEY):
            form = sc.sticky[FORM_KEY]
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove(FORM_KEY)
            

    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def play_sound(self, file_name = None, is_announcer = False):
        if not self.is_sound_enabled:
            return
        
        
        folder = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Source Codes\\Fun\\sound effects\\red alert"
        if isinstance(file_name, list):
            file_name = random.choice(file_name)

        if not file_name:
            files = os.listdir(folder)
            files = [f for f in files if f.endswith('.wav')]
            # radnomly pick one
            file_name = random.choice(files)

        if is_announcer:
            file_name = "{}\\Announcer Speech\\{}".format(folder, file_name)
        
        file_name = os.path.join(folder, file_name)
        EnneadTab.SOUNDS.play_sound(file_name)
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def outline_animated(self, geos):
        if len(geos)==0:
            return
        # rs.MeshOutline()
        self.is_sound_enabled = False
        
        viewport = sc.doc.Views.ActiveView.MainViewport
        mesh_setting = Rhino.Geometry.MeshingParameters()
        view_cplane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        
        
        for geo in geos:
            geo = geo.Geometry 
            # print (geo)
            try:
                meshes = Rhino.Geometry.Mesh.CreateFromBrep (geo, mesh_setting)
            except Exception as e:
                print (e)
                continue
            
            mesh = Rhino.Geometry.Mesh()
            [mesh.Append(x) for x in meshes]
   
            # print (mesh)
            
        
            outlines = mesh.GetOutlines(viewport)
            tolerance = sc.doc.ModelAbsoluteTolerance
            style = System.Enum.ToObject(Rhino.Geometry.CurveOffsetCornerStyle, 2)
            bbox = geo.GetBoundingBox (True)
            bbox_center = bbox.Min + (bbox.Max - bbox.Min)/2
            
            collection = []
            max_ring = 5
            additional_factor = 0
            for i in range(1, 1 + max_ring * 2):
                additional_factor += 0.05
                if i <= max_ring:
                    for outline in outlines:
                        
                        curves_in = outline.ToPolylineCurve ().Offset(bbox_center, view_cplane.Normal, -self.outline_offset * i * additional_factor, tolerance, style)
                        curves_out = outline.ToPolylineCurve ().Offset(bbox_center, view_cplane.Normal, self.outline_offset * i * additional_factor, tolerance, style)
                        if self.get_crvs_sum_length(curves_in) > self.get_crvs_sum_length(curves_out):
                            curves = curves_in
                        else:
                            curves = curves_out

                        collection.append( [sc.doc.Objects.AddCurve(curve) for curve in curves])
                else:
                    while len(collection) > 0:
                        old_crvs = collection.pop(0)
                        rs.DeleteObjects(old_crvs)
                        sc.doc.Views.Redraw()
           
                
                sc.doc.Views.Redraw()
        
        self.is_sound_enabled = True   
                
            
    def get_crvs_sum_length(self, crvs):
        return sum([crv.GetLength() for crv in crvs])

################################################################################
# TestGameSound function
################################################################################
def add_game_sound():

    # See if the form is already visible
    if sc.sticky.has_key(FORM_KEY):
        return
        pass

    # Create and show form
    test_list = [1,2,3]
    form = GameSound()
    # print form.test_list
    form.test_list = test_list
    # print form.test_list
    #form.CreateFormControls()
    form.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    form.Show()
    #form.count_down(4)
    # Add the form to the sticky dictionary so it
    # survives when the main function ends.
    sc.sticky[FORM_KEY] = form





######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    add_game_sound()




"""
##The Search Paths options manage locations to search for bitmaps that used for render texture and bump maps.
rs.AddSearchPath(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EA_UTILITY.py')




rs.FindFile(filename)
Searches for a file using Rhino's search path. Rhino will look for a
    file in the following locations:
      1. The current document's folder.
      2. Folder's specified in Options dialog, File tab.
      3. Rhino's System folders
path = rs.FindFile("Rhino.exe")
print(path)




Rhino.RhinoObject.Select(True, True, True, False, True, False)

"""
