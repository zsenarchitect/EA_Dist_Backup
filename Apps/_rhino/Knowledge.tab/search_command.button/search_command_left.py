__title__ = ["SearchCommand"
             "LearnEnneadTabForRhino",
             "CommandList"]
__doc__ = "Learn all the buttons functions."


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs

import Eto # pyright: ignore

import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations

import os
import json
from EnneadTab import LOG, ERROR_HANDLE, NOTIFICATION, ENVIRONMENT
from EnneadTab.RHINO import RHINO_ALIAS, RHINO_UI

import logging

# Add at the start of the file
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KNOWLEDGE_FILE = "{}\\knowledge_database.sexyDuck".format(ENVIRONMENT.RHINO_FOLDER)



# make modal dialog
class EnneadSearchDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    
    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        logger.info("Initializing EnneadSearchDialog")
        # Eto initials
        self.Title = "EnneadTab For Rhino. Searcher"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = None
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 600
        self.width = 400
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

        
        self.checkbox_search_in_tooltip = Eto.Forms.CheckBox()
        self.checkbox_search_in_tooltip.Text = "Search include Tooltip?"
        self.checkbox_search_in_tooltip.CheckedChanged += self.checkbox_search_in_tooltip_CheckedChanged
        left_layout.AddSeparateRow(None, self.checkbox_search_in_tooltip)
        
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

        RHINO_UI.apply_dark_style(self)


    # collect data for list
    def InitializeScriptList(self):
        logger.info("Initializing script list and get base knowledge")

        with open(KNOWLEDGE_FILE, "r") as f:
            knowledge_pool = json.load(f)


        self.knowledge = {}
        
        # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
        for value in knowledge_pool.values():
            command_names = value["alias"]
            if not isinstance(command_names, list):
                command_names = [command_names]
            for command_name in command_names:
                self.knowledge[command_name] = value


        # wrap each command name in a list to fit grid view format
        return sorted([[x] for x in self.knowledge.keys()])




    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()
        return self.logo


    def CreateIconTray_Button(self):
        icon_tray_button_layout = Eto.Forms.DynamicLayout() 
        
        self.icon_tray_button_image_viewer = Eto.Forms.ImageView()
        icon_tray_button_layout.AddRow(self.icon_tray_button_image_viewer)      
        return icon_tray_button_layout

    def CreateIconTray_Tab(self):
        icon_tray_tab_layout = Eto.Forms.DynamicLayout() 

        self.icon_tray_tab_image_viewer = Eto.Forms.ImageView()
        icon_tray_tab_layout.AddRow(self.icon_tray_tab_image_viewer)    

        label = Eto.Forms.Label()
        label.Text = ""
        icon_tray_tab_layout.AddSeparateRow(label)  
        return icon_tray_tab_layout
 
    def update_icon_tray_button(self):
        


        def update_image_action(search_key, image_viewer):
            
            icon_path = self.knowledge[self.selected_button_name].get(search_key, None)
            if icon_path is None:
                icon_path = os.path.join(os.path.dirname(__file__), "missing_icon.png")
           
            # rank icon by file size, more complex one is the better quality, usually
            icon_image_path = os.path.join(ENVIRONMENT.RHINO_FOLDER, icon_path)


            if os.path.exists(icon_image_path):
                image = Eto.Drawing.Bitmap(icon_image_path)
                image_viewer.Image = image.WithSize(50,50)
  
        
        update_image_action("icon", self.icon_tray_button_image_viewer)
        update_image_action("tab_icon", self.icon_tray_tab_image_viewer)

    def update_info_text(self):

 
        # print self.knowledge
        data = self.knowledge[self.selected_button_name]
        if "_right.py" in data["script"]:
            access = "Right Click"
        else:
            access = "Left Click"

        tab_name = data.get("tab", None)
        if tab_name is None:
            tab_name = "Unknown"
        tab_name = tab_name.replace(".tab", " Tab").replace(".menu", " Menu")

        commands = data.get("alias", None)
        if not isinstance(commands, list):
            commands = [commands]
        final_commands = []
        for command in commands:
            if command is None:
                continue
            if command.upper() == command:
                final_commands.append(command)
            else:
                final_commands.append("EA_{}".format(command))
        commands = " / ".join(final_commands)
        # print data
        self.bt_info_A.Text = "Button Name: {}\nCommand: {}\nTooltip: {}\nAccess: {}\nButton Icon:".format(self.selected_button_name,
                                                                                            commands,
                                                                                            data.get("doc"),
                                                                                            access)
        self.bt_info_B.Text = "Find this button in: {}\nTab Icon:".format(tab_name)
    
        
        click_icon = "{}\\{}.png".format(os.path.join(os.path.dirname(__file__)), access)
        image = Eto.Drawing.Bitmap(click_icon)
        self.access_icon.Image = image.WithSize(30,30)
    
    
    def update_info_panel(self):
        try:
            logger.info("Updating info panel")
            if len(list(self.lb.SelectedItems)) == 0:
                return
            self.selected_button_name = list(self.lb.SelectedItems)[0][0]
        except Exception as e:
            logger.error("Error updating info panel: {}".format(str(e)))
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
        # label = Eto.Forms.Label()
        # label.Text = "Tab Info:"
        # layout.AddSeparateRow(label)
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
        self.lb = Eto.Forms.GridView()
        self.lb.ShowHeader = True
        self.lb.AllowMultipleSelection = False
        self.lb.Height = self.height
        self.lb.AllowColumnReordering = True

        self.lb.DataStore = sorted(self.ScriptList)

        self.lb.SelectedRowsChanged += self.RowsChanged


        # Create Gridview Column
        column1 = Eto.Forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = Eto.Forms.TextBoxCell(0)
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
        logger.info("Performing search with text: '{}'".format(text))
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        if text == "":
            logger.debug("Empty search - showing full script list")
            self.lb.DataStore = self.ScriptList
        else:
            if not self.is_search_in_tooltip:
                #print self.ScriptList
                temp = [ [str(x[0])] for x in self.ScriptList]
                # print temp[0:2]
                self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            
            else:
                complete_data = [["{}^^^{}".format(x[0], self.knowledge[x[0]]["doc"])] for x in self.ScriptList]
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

                self.SearchedScriptList.sort(key=lambda x: text.lower() in x[0].lower(), reverse=True)
                # print self.SearchedScriptList
            #print "######"
            #print self.SearchedScriptList

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))
            self.lb.DataStore = self.SearchedScriptList
            
        
        self.update_info_panel()


    # Gridview SelectedRows Changed Event
    def RowsChanged (self,sender,e):
        logger.info("Selection changed in grid view")
        self.update_info_panel()
        return self.lb.SelectedRows



    # function to run when call at button click
    def pretty_print_knowledge_data(self):
        # return selected items
        import pprint

        text = pprint.pformat(self.knowledge, indent = 4)
        rs.TextOut(text)



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged(self, sender, e):
        self.Search(self.tB_Search.Text)

    def checkbox_search_in_tooltip_CheckedChanged(self, sender, e):
        self.Search(self.tB_Search.Text)



    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        logger.info("Run button clicked")
        # close window after double click action. Otherwise, run with error

        #print sender
        #print e
        #print self.lb.SelectedItems
        #print dir(self.lb)
        #print len(list(self.lb.SelectedItems))
        #print len(list(self.lb.SelectedRows))
        # if len(list(self.lb.SelectedItems)) == 0:
        #     NOTIFICATION.toast(main_text = "Need to select at least something")
        #     return
        # self.Close(True)
        self.pretty_print_knowledge_data()


    # event handler handling clicking on the 'run' button
    def btn_select_all_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.lb.SelectAll()
        NOTIFICATION.toast(main_text = "{} items slected".format(len(self.SearchedScriptList)))


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        logger.info("Cancel button clicked")
        self.Close(False)



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def search_command():
    logger.info("Starting search command")
    RHINO_ALIAS.register_alias_set()
    
    dlg = EnneadSearchDialog()
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)




if __name__ == "__main__":
    search_command()