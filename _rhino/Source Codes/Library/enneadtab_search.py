
import System # pyright: ignore
import Rhino # pyright: ignore
import Rhino # pyright: ignore.UI
import rhinoscriptsyntax as rs

import Eto # pyright: ignore
import Eto # pyright: ignore.Drawing as drawing
import Eto # pyright: ignore.Forms as forms

import scriptcontext as sc
import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations
import sys
# current = os.path.dirname(os.path.realpath(__file__))
# parent = os.path.dirname(current)
sys.path.append("..\lib")
import EnneadTab
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\Library")

import documentation_lookup as doc_lookup
reload(doc_lookup)



# make modal dialog
class EnneadSearchDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def __init__(self):
        # Eto initials
        self.Title = "EnneadTab For Rhino. Searcher"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 300
        self.width = 200
        self.icon_image_paths = []
       

        # fields
        self.ScriptList = self.InitializeScriptList()
        self.SearchedScriptList = self.ScriptList[::]


        # initialize layout
        left_layout = Eto.Forms.DynamicLayout()
        left_layout.Padding = Eto.Drawing.Padding(5)
        left_layout.Spacing = Eto.Drawing.Size(5, 5)
        right_layout = Eto.Forms.DynamicLayout()
        right_layout.Padding = Eto.Drawing.Padding(5)
        right_layout.Spacing = Eto.Drawing.Size(5, 5)
        

        right_layout.AddSeparateRow(None, self.CreateLogoImage())

        # add message
        left_layout.BeginVertical()
        left_layout.AddRow(self.CreateMessageBar())
        left_layout.EndVertical()

        # add search
        left_layout.BeginVertical()
        left_layout.AddRow(*self.CreateSearchBar())
        left_layout.EndVertical()

        # add listBox
        left_layout.BeginVertical()
        left_layout.AddRow(self.CreateScriptListBox())
        left_layout.EndVertical()

        # add buttons
        left_layout.BeginVertical()
        left_layout.AddRow(self.CreateButtons())
        left_layout.EndVertical()
        
        
        right_layout.BeginVertical()
        right_layout.AddRow(self.CreateInfoLabels_Button())
        right_layout.AddRow(self.CreateIconTray_Button())
        right_layout.AddRow(self.CreateInfoLabels_Tab())
        right_layout.AddRow(self.CreateIconTray_Tab())
        right_layout.EndVertical()

        # set content
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.AddRow(left_layout, right_layout)
        
        self.Content = main_layout


    # collect data for list
    def InitializeScriptList(self):
        rui_file = r"C:\Users\szhang\github\EnneadTab-for-Rhino\Source Codes\research.rui"
        rui_file = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Working\EnneadTab.rui"
        lookup_data = doc_lookup.DocumentationLookup(rui_file)
        lookup_data.collect_data()
        self.knowledge = lookup_data.knowledge
        self.data_folder = lookup_data.data_folder
        
        
        # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
        return sorted([[x] for x in self.knowledge.keys()])




    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo


    def CreateIconTray_Button(self):
        self.icon_tray_button_layout = Eto.Forms.DynamicLayout() 
        for i in range(1):
            image_viewer = Eto.Forms.ImageView()
            self.icon_tray_button_layout.AddRow(image_viewer)      
        return self.icon_tray_button_layout

    def CreateIconTray_Tab(self):
        self.icon_tray_tab_layout = Eto.Forms.DynamicLayout() 
        for i in range(1):
            image_viewer = Eto.Forms.ImageView()
            self.icon_tray_tab_layout.AddRow(image_viewer)      
        return self.icon_tray_tab_layout
 
    def update_icon_tray_button(self):
        


        def update_image_action(search_key, layout):
            
            icon_id = self.knowledge[self.selected_button_name].get(search_key, None)
            if icon_id is None:
                icon_id = "empty"
            related_icons = [x for x in os.listdir(self.data_folder) if x.startswith(icon_id) and "large" in x]
            icon_image_paths = [os.path.join(self.data_folder, x) for x in related_icons]
            # rank icon by file size, more complex one is the better quality, usually
            icon_image_paths.sort()


            if len(icon_image_paths) != 0:
                for i,image_path in enumerate(icon_image_paths):
                    image_viewer = list(layout.Controls)[i]
                    image = Eto.Drawing.Bitmap(image_path)
                    image_viewer.Image = image.WithSize(50,50)
  
        
        update_image_action("icon_id", self.icon_tray_button_layout)
        update_image_action("tab_icon_id", self.icon_tray_tab_layout)

    def update_info_text(self):
        # print (1232132130)
        # print self.selected_button_name
 
        # print self.knowledge
        data = self.knowledge[self.selected_button_name]
        # print data
        self.bt_info_A.Text = "Button Name = {}\nTooltip = {}\nAccess = {}\nButton Icon =".format(self.selected_button_name,
                                                                                            data["macro_tooltip"],
                                                                                            data["access"])
        self.bt_info_B.Text = "Tab Name = {}\nTab Icon =".format(data.get("tab_name", None))
    
        
        click_icon = "{}\{}.png".format(self.data_folder, data["access"])
        image = Eto.Drawing.Bitmap(click_icon)
        self.access_icon.Image = image.WithSize(20,20)
    
    
    def update_info_panel(self):
        try:
            self.selected_button_name = list(self.lb.SelectedItems)[0][0]
        except Exception as e:
            print (e)
            return
        self.update_icon_tray_button()
        self.update_info_text()
    
    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Find the what EnneadTab for Rhino can do and where are they?"
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    def CreateInfoLabels_Button(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.Width = 400
        label = Eto.Forms.Label()
        label.Text = "Button Info:"
        layout.AddSeparateRow(label)
        self.bt_info_A = Eto.Forms.Label()
        layout.AddSeparateRow( self.bt_info_A)
        self.access_icon = Eto.Forms.ImageView()
        layout.AddRow(self.access_icon)

        return layout
        
    def CreateInfoLabels_Tab(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.Width = 400
        label = Eto.Forms.Label()
        label.Text = "Tab Info:"
        layout.AddSeparateRow(label)
        self.bt_info_B = Eto.Forms.Label()
        layout.AddSeparateRow( self.bt_info_B)
        
        return layout
    

    # create search bar function
    def CreateSearchBar(self):
        """
        Creates two controls for the search bar
        self.lbl_Search as a simple label
        self.tB_Search as a textBox to input search strings to
        """
        self.lbl_Search = Eto.Forms.Label()
        self.lbl_Search.Text = "Type Here to Search: "
        self.lbl_Search.VerticalAlignment = Eto.Forms.VerticalAlignment.Center

        self.tB_Search = Eto.Forms.TextBox()
        self.tB_Search.TextChanged += self.tB_Search_TextChanged


        return [self.lbl_Search, self.tB_Search]



    def CreateScriptListBox(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb = forms.GridView()
        self.lb.ShowHeader = True
        self.lb.AllowMultipleSelection = False
        self.lb.Height = self.height
        self.lb.AllowColumnReordering = True

        self.lb.DataStore = sorted(self.ScriptList)

        self.lb.SelectedRowsChanged += self.RowsChanged


        # Create Gridview Column
        column1 = forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = forms.TextBoxCell(0)
        self.lb.Columns.Add(column1)

        self.lb.DataStore = self.SearchedScriptList

        return self.lb



    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        layout = Eto.Forms.DynamicLayout()
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.Padding = Eto.Drawing.Padding(5)
        
        
        self.checkbox_search_in_tooltip = Eto.Forms.CheckBox()
        self.checkbox_search_in_tooltip.Text = "Search include Tooltip?"
        self.checkbox_search_in_tooltip.CheckedChanged += self.checkbox_search_in_tooltip_CheckedChanged
        
        layout.AddSeparateRow(self.checkbox_search_in_tooltip)
        
        
        user_buttons = []
        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Pretty Print Dictionary!"
        self.btn_Run.Click += self.btn_Run_Clicked
        user_buttons.append(self.btn_Run)
        


        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked

        user_buttons.extend([ None, self.btn_Cancel])
        
        layout.AddSeparateRow(*user_buttons)
        return layout
    
    
    @property
    def is_search_in_tooltip(self):
        return self.checkbox_search_in_tooltip.Checked

    # create a search function
    def Search(self, text):
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        if text == "":
            self.lb.DataStore = self.ScriptList
        else:
            if not self.is_search_in_tooltip:
                #print self.ScriptList
                temp = [ [str(x[0])] for x in self.ScriptList]
                # print temp[0:2]
                self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            
            else:
                complete_data = [["{}^^^{}".format(x[0], self.knowledge[x[0]]["macro_tooltip"])] for x in self.ScriptList]
                # print complete_data[0:2]
                #print temp
                #print flatten(temp)
                #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
                #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

                # self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
                # print searched_compiler
                searched_compiler = list(graft(fnmatch.filter(flatten(complete_data), "*" + text + "*"), 1))
                # print searched_compiler
                self.SearchedScriptList = [[x[0].split("^^^")[0]] for x in searched_compiler]
                # print self.SearchedScriptList
            #print "######"
            #print self.SearchedScriptList

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))
            self.lb.DataStore = self.SearchedScriptList
            
        
        self.update_info_panel()


    # Gridview SelectedRows Changed Event
    def RowsChanged (self,sender,e):
        self.update_info_panel()
        return self.lb.SelectedRows



    # function to run when call at button click
    def pretty_print_knowledge_data(self):
        # return selected items
        import pprint

        text = pprint.pformat(self.knowledge, indent = 4, underscore_numbers=True)
        rs.TextOut(text)



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged(self, sender, e):
        self.Search(self.tB_Search.Text)

    def checkbox_search_in_tooltip_CheckedChanged(self, sender, e):
        self.Search(self.tB_Search.Text)



    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error

        #print sender
        #print e
        #print self.lb.SelectedItems
        #print dir(self.lb)
        #print len(list(self.lb.SelectedItems))
        #print len(list(self.lb.SelectedRows))
        # if len(list(self.lb.SelectedItems)) == 0:
        #     EnneadTab.NOTIFICATION.toast(main_text = "Need to select at least something")
        #     return
        # self.Close(True)
        self.pretty_print_knowledge_data()


    # event handler handling clicking on the 'run' button
    def btn_select_all_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.lb.SelectAll()
        EnneadTab.NOTIFICATION.toast(main_text = "{} items slected".format(len(self.SearchedScriptList)))


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)


@EnneadTab.ERROR_HANDLE.try_catch_error
def enneadtab_search():



    dlg = EnneadSearchDialog()
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)



if __name__ == "__main__":
    enneadtab_search()
