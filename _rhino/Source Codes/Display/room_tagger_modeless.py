
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
# import clr # pyright: ignore
# import System # pyright: ignore

"""
### TO-DO:
- Add help section to dialog window
#### Assigned to: **CM**
"""

import sys
sys.path.append("..\lib")
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

sys.path.append("..\Display")
import imp

RT = imp.load_source("room_tagger_conduit", r'L:\\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Display\room_tagger_conduit.py')



# import System # pyright: ignore

import Eto # pyright: ignore

FORM_KEY = 'ROOM_TAGGER_modeless_form'




# make modal dialog
class RoomTaggerDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Room Tagger"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 400
        self.width = 100
        
        self.is_color_triggering_enabled = True
        self.Closed += self.OnFormClosed




        # initialize layout
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.Padding = Eto.Drawing.Padding(5)
        main_layout.Spacing = Eto.Drawing.Size(5, 5)



       
        main_layout.BeginVertical()
        main_layout.AddRow(self.create_tag_adder())
        main_layout.AddRow(self.create_zone_adder())
        main_layout.AddRow( Rhino.UI.Controls.Divider())
        main_layout.AddRow(self.Create_graphic_control())
        main_layout.EndVertical()





        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        # add message
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.AddRow(self.CreateExpander())
        layout.EndVertical()


        layout.BeginVertical()
        layout.AddRow(None, main_layout, None)
        layout.EndVertical()

        # add buttons
       
        layout.AddSeparateRow(*self.CreateButtons())
    

        # set content
        layout.Width = 400
        self.Content = layout
        self.InitiateFiller()
        
        # print self.Content
        EnneadTab.RHINO.RHINO_UI.apply_dark_style(self)

  


    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Add new room dot and/or customize the graphic."
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left


    def CreateExpander(self):
        self.expander = Eto.Forms.Expander ()
        self.expander.Header = "Quick Help"
        self.expander.Expanded = False
        msg = Eto.Forms.Label()
        msg.Text = "helper document to be filled in....."
        self.expander.Content = msg
        return self.expander


    def create_zone_adder(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        A = Eto.Forms.Label(Text = 'Define a zone that seperate the area plans.')
        layout.AddRow(None, A, None)
        
        self.zone_name_input = Eto.Forms.TextBox()
        self.zone_name_input.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(None, self.zone_name_input, None)

        pick_bn = Eto.Forms.Button(Text = 'Draw a zone.')
        pick_bn.Click += self.btn_define_zone
        layout.AddRow(None, pick_bn,  None)

        return layout

    def create_tag_adder(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        A = Eto.Forms.Label(Text = 'Drop a room dot with the name below.\nIf feeling calcuation is slow, disable it while adding new dots.')
        layout.AddRow(A)
        
        self.room_name_input = Eto.Forms.TextBox()
        self.room_name_input.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(self.room_name_input)

        pick_bn = Eto.Forms.Button(Text = 'Pick Location.')
        pick_bn.Click += self.btn_pick_dot_location

        self.srf_label = Eto.Forms.Label(Text = '')
        layout.AddRow(pick_bn,  None)
        layout.AddRow(self.srf_label)
        layout.AddRow(Rhino.UI.Controls.Divider())

        return layout


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def Create_graphic_control(self):
        
        # control for hide unhide all tagger dot(will handle both user input and conduit dot)
        
        #control for pick color for a name
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        self.tbox_font_size = Eto.Forms.TextBox()
        self.tbox_font_size.TextAlignment = Eto.Forms.TextAlignment.Center
        self.tbox_font_size.Width = 50
        layout.AddSeparateRow(None, Eto.Forms.Label(Text="Label Font Size: "), self.tbox_font_size, None)
        
        bt_show = Eto.Forms.Button()
        bt_show.Text = " Show Working Dots "
        bt_show.Click += self.on_show_working_dots
        bt_hide = Eto.Forms.Button()
        bt_hide.Text = " Hide Working Dots "
        bt_hide.Click += self.on_hide_working_dots
        
        layout.AddSeparateRow(None, bt_show, bt_hide, None)
        
        
        layout.AddRow(Rhino.UI.Controls.Divider())
        
        
        self.room_list = Eto.Forms.ListBox()
        self.room_list.Height = 150
        self.room_list.SelectedIndexChanged += self.on_selected_index_changed
        self.reset_listbox()
        layout.AddSeparateRow(Eto.Forms.Label(Text = "Existing room names\nin current document:",
                                              VerticalAlign=Eto.Forms.VerticalAlign.Top ),
                              None,
                              self.room_list)
        
        self.color_picker = Eto.Forms.ColorPicker()
        layout.AddSeparateRow(Eto.Forms.Label(Text = "Pick a color for the selected room name:"), 
                               
                              self.color_picker)
        self.color_picker.ValueChanged += self.on_color_picker_changed
        return layout

    def reset_listbox(self):
        self.room_list.Items.Clear()
        [self.room_list.Items.Add(x) for x in self.get_available_room_names()]
        
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def on_color_picker_changed(self, sender, e):
        color = self.color_picker.Value
        color = color.ToHex(includeAlpha  = False)
        # print color
        color = EnneadTab.COLOR.hex_to_rgb(color)
        # print color
        current_color_map = EnneadTab.DATA_FILE.get_sticky_longterm(RT.KEY_COLOR_DICT,dict())
        # print self.room_list.SelectedValue
        current_color_map[self.room_list.SelectedKey] = list(color)
        EnneadTab.DATA_FILE.set_sticky_longterm(RT.KEY_COLOR_DICT, current_color_map)
        
        if self.is_color_triggering_enabled:
            self.trigger_refresh()
    

    
    # Listbox.SelectedIndexChanged event handler
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def on_selected_index_changed(self, sender, e):
        index = self.room_list.SelectedIndex
        if index < 0:
            return
        
        item = self.room_list.Items[index]
        
        objs = rs.ObjectsByName(RT.DOT_NAME)
        # print objs
        # print rs.TextDotText(objs[0])
        objs = [x for x in objs if rs.TextDotText(x) == str(item)]
        # print objs
        rs.UnselectAllObjects()
        rs.SelectObjects(objs)
            
            
       
        current_color_map = EnneadTab.DATA_FILE.get_sticky_longterm(RT.KEY_COLOR_DICT,dict())
        # print self.room_list.SelectedValue
        color_tuple = current_color_map.get(self.room_list.SelectedKey, None)
        if not color_tuple:
            color_tuple = RT.SAMPLE_COLOR_DICT.get(self.room_list.SelectedKey.lower(), (0,0,0))
        color = Eto.Drawing.Color(color_tuple[0]/255.0, color_tuple[1]/255.0, color_tuple[2]/255.0)
        
        self.is_color_triggering_enabled = False
        self.color_picker.Value = color
        self.is_color_triggering_enabled = True
            
           
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def on_show_working_dots(self, sender, e):
        objs = rs.ObjectsByName(RT.DOT_NAME)
        rs.ShowObjects(objs)
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def on_hide_working_dots(self, sender, e):
        objs = rs.ObjectsByName(RT.DOT_NAME)
        rs.HideObjects(objs)
            
            
    def get_available_room_names(self):
        dots = rs.ObjectsByName(RT.DOT_NAME)
        return sorted(list(set([rs.TextDotText(x) for x in dots])))

    def CreateButtons(self):

        user_buttons = []
   

        user_buttons.append(None)
        
        
        bt = Eto.Forms.Button()
        bt.Height = 30
        bt.Text = " Force Regenerate "
        bt.Click += self.btn_force_regenerate
        user_buttons.append(bt)
        user_buttons.append(None)
        
        bt = Eto.Forms.Button()
        bt.Height = 30
        bt.Text = " Bake ColorFill To File "
        bt.Click += self.btn_bake_colorfill
        user_buttons.append(bt)
        user_buttons.append(None)
        
        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Height = 30
        self.btn_Run.Text = " Export Data To Excel "
        temp_bitmap = Eto.Drawing.Bitmap(r"{}\excel.png".format(self.FOLDER_APP_IMAGES))
        self.btn_Run.Image = temp_bitmap.WithSize(200,50)
        self.btn_Run.Image = temp_bitmap
        self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Left
        self.btn_Run.Click += self.btn_export_to_excel
        user_buttons.append(self.btn_Run)


        user_buttons.append(None)

        #self.width = 400

        return user_buttons



    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_force_regenerate(self, sender, e):
        print ("force regenerating")
        self.trigger_refresh()
        

    # event handler handling clicking on the 'run' button
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_export_to_excel(self, sender, e):
        filename = "EnneadTab GFA Schedule"
        if sc.doc.Name is not None:
            filename = "{}_EnneadTab GFA Schedule".format(sc.doc.Name.replace(".3dm", ""))
            
        
        filepath = rs.SaveFileName(title = "Where to save the Excel?", filter = "Excel Files (*.xlsx)|*.xlsx||", filename = filename)
        if filepath is None:
            return
        
        sc.sticky[RT.KEY_EXCEL_PATH] = filepath
        
        
        self.trigger_refresh()
        
    def trigger_refresh(self):
        # this will trigger a recaulation
        
        rs.EnableRedraw(False)
        sc.sticky[RT.KEY_HOLDING_CALC] = True
        temp = rs.AddPoint(0,0,0)
        rs.ObjectName(temp, RT.DOT_NAME)
        sc.sticky[RT.KEY_HOLDING_CALC] = False
        
        rs.DeleteObject(temp)
        rs.EnableRedraw(True)


    @EnneadTab.ERROR_HANDLE.try_catch_error      
    def btn_bake_colorfill(self, sender, e):
        try:
            font_size = int(self.tbox_font_size.Text)
            if font_size <=0:
                EnneadTab.NOTIFICATION.messenger(main_text = "Need a positive font size.")
                return
        except:
            EnneadTab.NOTIFICATION.messenger(main_text = "Cannot convert font size to integer.")
            return
        
        sc.sticky[RT.KEY_LABEL_SIZE] = font_size
        sc.sticky[RT.KEY_BAKING_COLORFILL] = True
        EnneadTab.NOTIFICATION.messenger(main_text = "Baking ColorFill...")
        
    


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_pick_dot_location(self, sender, e):
        if not self.room_name_input.Text:
            EnneadTab.NOTIFICATION.messenger(main_text = "Room name is empty....")
            return
        dot = RT.add_room_tagger_dot(self.room_name_input.Text)
        
        if dot:
            temp_note = "Room Point Added!"
            self.srf_label.Text = temp_note
            EnneadTab.NOTIFICATION.messenger(main_text = temp_note)
            self.reset_listbox()
            
        else:
            temp_note = "Room Point NOT Added!"
            self.srf_label.Text = temp_note
            EnneadTab.NOTIFICATION.messenger(main_text = temp_note)

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_define_zone(self, sender, e):
        if not self.zone_name_input.Text:
            EnneadTab.NOTIFICATION.messenger(main_text = "Zone name is empty....")
            return
        
        
        zone_name = RT.ZONE_NAME + "_" + self.zone_name_input.Text
        if len(rs.ObjectsByName(zone_name)) != 0:
            EnneadTab.NOTIFICATION.messenger(main_text = "Zone name is already in use....")
            return
        
        rect_corners = rs.GetRectangle()
        if not rect_corners:
            return
        
        rect = rs.AddRectangle(Rhino.Geometry.Plane(rect_corners[0], Rhino.Geometry.Vector3d(0,0,1)),
                                rs.Distance(rect_corners[0], rect_corners[1]),
                                rs.Distance(rect_corners[0], rect_corners[3]))

        rs.ObjectName(rect, zone_name)
        dot = rs.AddTextDot(self.zone_name_input.Text, rect_corners[0])
        rs.ObjectName(dot, zone_name)
        rs.AddObjectsToGroup([rect, dot], rs.AddGroup(zone_name))
        
        
        self.trigger_refresh()

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def OnFormClosed(self, sender, e):
        self.Close()


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def InitiateFiller(self):
        # use this filler to control what to record and preload for UI setting

        self.ui_input = ["tbox_font_size"]
        for x in self.ui_input:
            sticky_key = FORM_KEY + x
            if not hasattr(self, x):
                continue
            user_input_ui = getattr(self, x)
            
            
            if "tbox" in x:
                value = EnneadTab.DATA_FILE.get_sticky_longterm(sticky_key, "")
                setattr(user_input_ui, "Text", value)
            elif "checkbox" in x:
                value = EnneadTab.DATA_FILE.get_sticky_longterm(sticky_key, False)
                setattr(user_input_ui, "Checked", value)

                
                
        return


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def Close(self):
      
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key(FORM_KEY):
            form = sc.sticky[FORM_KEY]
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove(FORM_KEY)

        for x in self.ui_input:
            if not hasattr(self, x):
                continue
            user_input_ui = getattr(self, x)
            sticky_key = FORM_KEY + x
            #print x
            if hasattr(user_input_ui,"Text"):
                EnneadTab.DATA_FILE.set_sticky_longterm(sticky_key, user_input_ui.Text)
            if hasattr(user_input_ui,"Checked"):
                EnneadTab.DATA_FILE.set_sticky_longterm(sticky_key, user_input_ui.Checked)




@EnneadTab.ERROR_HANDLE.try_catch_error
def room_tagger_modeless():
    rs.EnableRedraw(False)
    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = RoomTaggerDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg
    return


######################  main code below   #########
if __name__ == "__main__":

    room_tagger_modeless()
