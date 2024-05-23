import System # pyright: ignore
import Rhino # pyright: ignore
import Rhino # pyright: ignore.UI
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Eto # pyright: ignore
import os
import fnmatch
import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
EnneadTab.NOTIFICATION.toast(main_text = "V9 eto")

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations

# make modal dialog
class ImageSelectionDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    def __init__(self, options):
        # Eto initials
        self.Title = "V9"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 400
        self.width = 600
        self.multi_select = False
        self.Message = "EnneadTab's Asset Search Tool(Work In progress). Features roadmap:\n-Set and read doc data from outside\n-Multiple selection and drop\n-Multiple selection and drop with multiple preview.\n-Interactive insertion.\n-Record download count and option to rank by office popularity\n-Make as Rhino dock panel"
        self.Button_Names = ["Place Asset!"]
        self.PRIMARY_FOLDER = r"L:\4b_Applied Computing\00_Asset Library"
        self.DEFAULT_IMAGE_NOTHING_SELECTED = r"{}\Database\app images\DEFAULT PREVIEW_NOTHING SELECTED.png".format(self.PRIMARY_FOLDER)
        self.DEFAULT_IMAGE_CANNOT_FIND_PREVIEW_IMAGE = r"{}\Database\app images\DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png".format(self.PRIMARY_FOLDER)
        self.LOGO_IMAGE = r"{}\Database\app images\Ennead_Architects_Logo.png".format(self.PRIMARY_FOLDER)
        print(self.LOGO_IMAGE)
        self.IMAGE_MAX_SIZE = 800
        self.MANAGER_NAMES = ["szhang",
                            "eshaw"]
        if EnneadTab.USER.get_user_name() in self.MANAGER_NAMES:
            self.MANAGER_MODE = True
        else:
            self.MANAGER_MODE = False

        self.META_DATA  = dict()

        # fields
        self.ScriptList = options
        self.SearchedScriptList = self.ScriptList[::]


        # initialize layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)


        left_layout = Eto.Forms.DynamicLayout()
        left_layout.Padding = Eto.Drawing.Padding(5)
        left_layout.Spacing = Eto.Drawing.Size(5, 5)

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
        left_layout.AddRow(self.CreateScriptListBox(), None, self.CreateTagBox())
        left_layout.EndVertical()


        # add tag box
        left_layout.BeginVertical()
        left_layout.AddSeparateRow(self.CreateOccupancyGroup())
        left_layout.EndVertical()


        # add option box
        left_layout.BeginVertical()
        left_layout.AddSeparateRow(self.CreateControlBox())
        left_layout.EndVertical()

        left_layout.AddSpace()#this will make strectchable empty space, make sure it IS BETWEEN LAYOUT BUNDLES

        # add buttons
        left_layout.BeginVertical()
        left_layout.AddRow(*self.CreateButtons())
        left_layout.EndVertical()

        # add previews
        preview_image_layout = Eto.Forms.DynamicLayout()
        preview_image_layout.Padding = Eto.Drawing.Padding(5)
        preview_image_layout.Spacing = Eto.Drawing.Size(5, 5)
        #preview_image_layout.BeginHorizontal()
        preview_image_layout.AddSeparateRow(None, self.CreateLogoImage())
        preview_image_layout.AddRow(None)
        preview_image_layout.AddSeparateRow(self.CreatePreviewImage())
        if self.MANAGER_MODE:
            preview_image_layout.AddSpace()
            preview_image_layout.AddSeparateRow(self.CreateTagAssignment())
        #preview_image_layout.EndHorizontal()



        layout.AddRow(left_layout,preview_image_layout)

        # set content
        self.Content = layout







    """
    ##  create content ############################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    """


    # create preview image bar function
    def CreatePreviewImage(self):
        self.preview_image = Eto.Forms.ImageView()
        temp_bitmap = Eto.Drawing.Bitmap(self.DEFAULT_IMAGE_NOTHING_SELECTED)
        self.preview_image.Image = temp_bitmap.WithSize(self.IMAGE_MAX_SIZE,self.IMAGE_MAX_SIZE)
        return self.preview_image

    # create logo image bar function
    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,50)
        return self.logo



    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = self.Message
        self.msg.Font = Eto.Drawing.Font("Arial", 7)#, TextColor = Eto.Drawing.Color(0,0,240))
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    # create tag boxn
    def CreateOccupancyGroup(self):
        self.tag_option_groupbox = Eto.Forms.GroupBox()
        self.tag_option_groupbox.Text = "How many poeple can this asset accomendate?(Future function)"
        self.tag_option_groupbox.Padding = Eto.Drawing.Padding (10)
        group_layout = Eto.Forms.DynamicLayout()
        group_layout.Spacing = Eto.Drawing.Size(6,6)


        #self.TAG_DEFAULT_LIST = ["Asset Group", "Social", "Meet", "Work", "1 Person", "2 People", "3"]

        self.radiobutton_list_occupancy_filter = Eto.Forms.RadioButtonList()
        self.OCCUPANCY_DEFAULT_LIST = ["Any", "0", "1", "2", "3 ", "4", "5+"]
        self.radiobutton_list_occupancy_filter.DataStore = self.OCCUPANCY_DEFAULT_LIST
        self.radiobutton_list_occupancy_filter.Orientation = Eto.Forms.Orientation.Horizontal
        self.radiobutton_list_occupancy_filter.SelectedValue = self.OCCUPANCY_DEFAULT_LIST[0]
        self.radiobutton_list_occupancy_filter.Spacing = Eto.Drawing.Size(10,20)
        self.radiobutton_list_occupancy_filter.Padding = Eto.Drawing.Padding(10,5, 5, 5)
        self.radiobutton_list_occupancy_filter.SelectedValueChanged += self.occupancy_radiobutton_update


        #group_layout.AddRow(self.tag_filter_chairs,self.tag_filter_desks,self.tag_filter_socials )

        group_layout.AddRow(self.radiobutton_list_occupancy_filter )

        self.tag_option_groupbox.Content = group_layout

        return self.tag_option_groupbox


    # create tag boxn
    def CreateTagBox(self):
        self.tag_option_groupbox_vertical = Eto.Forms.GroupBox()
        self.tag_option_groupbox_vertical.Text = "Tags:"
        self.tag_option_groupbox_vertical.Padding = Eto.Drawing.Padding (10)

        group_layout = Eto.Forms.DynamicLayout()
        group_layout.Spacing = Eto.Drawing.Size(6,6)
        group_layout.Width = 100

        """
        self.tag_filter_chairs = Eto.Forms.CheckBox()
        self.tag_filter_desks = Eto.Forms.CheckBox()
        self.tag_filter_socials = Eto.Forms.CheckBox()
        """

        self.checkbox_list_tag_filter = Eto.Forms.CheckBoxList()
        self.TAG_DEFAULT_LIST = ["Furn",
                                "Setting",
                                "Work",
                                "Office",
                                "Lab",
                                "Social",
                                "Cafe",
                                "Meet",
                                "Privacy",
                                "Focus",
                                "Chair",
                                "Seat",
                                "Sofa",
                                "Lounge",
                                "Bar",
                                "Desk",
                                "Table",
                                "Door",
                                "Stor",
                                "Circle",
                                "Rect",
                                "Tree",
                                "Car"]
        self.checkbox_list_tag_filter.DataStore = self.TAG_DEFAULT_LIST
        self.checkbox_list_tag_filter.Orientation = Eto.Forms.Orientation.Vertical
        self.checkbox_list_tag_filter.SelectedValues  = []
        self.checkbox_list_tag_filter.Spacing = Eto.Drawing.Size(5,5)
        self.checkbox_list_tag_filter.Padding = Eto.Drawing.Padding(10,5, 5, 5)
        self.checkbox_list_tag_filter.SelectedValuesChanged += self.tag_box_update
        self.IS_TAG_LIST_CHANGING = False



        self.tag_vertical_clear_button = Eto.Forms.Button()
        self.tag_vertical_clear_button.Height = 20
        self.tag_vertical_clear_button.Width = 100
        self.tag_vertical_clear_button.Text = "Clear Filter"
        self.tag_vertical_clear_button.Click += self.tag_button_clear



        #group_layout.AddRow(self.tag_filter_chairs,self.tag_filter_desks,self.tag_filter_socials )
        group_layout.AddColumn(self.checkbox_list_tag_filter, None, self.tag_vertical_clear_button )



        self.tag_option_groupbox_vertical.Content = group_layout

        return self.tag_option_groupbox_vertical

    # create control boxn
    def CreateControlBox(self):
        self.block_insert_method_groupbox = Eto.Forms.GroupBox()
        self.block_insert_method_groupbox.Text = "How to insert block?"
        self.block_insert_method_groupbox.Padding = Eto.Drawing.Padding (10)
        group_layout = Eto.Forms.DynamicLayout()
        group_layout.Spacing = Eto.Drawing.Size(6,6)

        self.radio_button_list_ref_block_method = Eto.Forms.RadioButtonList()
        self.radio_button_list_ref_block_method.DataStore = ["As Ref Link", "Embed In Current File"]
        self.radio_button_list_ref_block_method.Orientation = Eto.Forms.Orientation.Vertical
        self.radio_button_list_ref_block_method.SelectedIndex = 1
        self.radio_button_list_ref_block_method.Spacing = Eto.Drawing.Size(10,20)
        self.radio_button_list_ref_block_method.Padding = Eto.Drawing.Padding(10,5, 5, 5)


        self.ref_block_method_label = Eto.Forms.Label()
        self.ref_block_method_label.Text = "Note: \nUsing ref link will keep file light and layer clear, but you dont have ability to modify geomtry, material or use MakeBlockUnique.\nUsing embed block will make it a local block and lose connection to L drive."

        group_layout.AddRow(self.radio_button_list_ref_block_method )
        group_layout.AddRow(self.ref_block_method_label )
        self.block_insert_method_groupbox.Content = group_layout

        return self.block_insert_method_groupbox
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    # create search bar function
    def CreateSearchBar(self):
        """
        Creates two controls for the search bar
        self.lbl_Search as a simple label
        self.tB_Search as a textBox to input search strings to
        """
        self.lbl_Search = Eto.Forms.Label()
        self.lbl_Search.Text = "Type Here to Search Keywords in the Asset name: "
        self.lbl_Search.VerticalAlignment = Eto.Forms.VerticalAlignment.Center
        self.lbl_Search.Font = Eto.Drawing.Font("Arial", 12, Eto.Drawing.FontStyle.Italic, Eto.Drawing.FontDecoration.Underline)

        self.tB_Search = Eto.Forms.TextBox()
        self.tB_Search.Width = 250
        self.tB_Search.TextChanged += self.textbox_textchanged_search_bar

        self.button_clear_text = Eto.Forms.Button()
        self.button_clear_text.Text = "Clear Search Bar"
        self.button_clear_text.Height = 5
        self.button_clear_text.Image = Eto.Drawing.Bitmap(r"{}\Database\app images\clear_text.png".format(self.PRIMARY_FOLDER))
        self.button_clear_text.ImagePosition = Eto.Forms.ButtonImagePosition.Left
        self.button_clear_text.Click += self.button_clicked_search_bar_clear_text
        return [self.lbl_Search, self.tB_Search,   self.button_clear_text]


    def update_item_tag_pool(self):
        self.ITEM_TAG_POOL = dict()
        self.ITEM_DOWNLOADS = dict()
        for item in self.ScriptList:
            rhino = item[0]
            self.ITEM_TAG_POOL[rhino] = self.read_item_tags(rhino)





    def CreateScriptListBox(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb = Eto.Forms.GridView()
        self.lb.ShowHeader = True
        self.lb.AllowMultipleSelection = self.multi_select
        self.lb.Height = self.height
        self.lb.AllowColumnReordering = True


        #self.lb.DataStore = sorted(self.ScriptList)
        #self.lb.DataStore = [[x, -1] for x in sorted(self.ScriptList)]
        #self.lb.DataStore = [sorted(self.ScriptList), [10*len(self.lb.DataStore)]]
        #self.lb.DataStore = [x.split("00_Asset Library\\")[1] for x in self.ScriptList]

        # inital a big dict for item tags data so later it is faster to lookup
        self.update_item_tag_pool()




        self.lb.SelectedRowsChanged += self.listbox_row_changed_main_grid_view


        self.lb.DataStore = self.get_listbox_data_store()
        print(self.lb.DataStore)
        #self.lb.DataStore = [x[0].split("00_Asset Library\\")[1] for x in self.SearchedScriptList]

        # Create Gridview Column
        column1 = Eto.Forms.GridColumn()
        column1.Editable = False
        column1.HeaderText = "Asset File"
        column1.Width = self.width
        column1.DataCell = Eto.Forms.TextBoxCell(0)
        column1.Sortable = True
        self.lb.Columns.Add(column1)


        column2 = Eto.Forms.GridColumn()
        column2.Editable = False
        column2.HeaderText = "Downloads"
        column2.Width = 100
        column2.DataCell = Eto.Forms.TextBoxCell(1)
        column2.Sortable = True
        self.lb.Columns.Add(column2)






        return self.lb



    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []
        max_height = 50
        for b_name in self.Button_Names:
            self.btn_Run = Eto.Forms.Button()
            self.btn_Run.Height = max_height
            self.btn_Run.Text = b_name
            self.btn_Run.Image = Eto.Drawing.Bitmap(r"L:\4b_Applied Computing\00_Asset Library\Database\app images\download.png")
            self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Right
            self.btn_Run.Click += self.button_clicked_place_asset
            user_buttons.append(self.btn_Run)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked
        self.btn_Cancel.Height = max_height

        user_buttons.extend([ None, self.btn_Cancel])


        return user_buttons

    def CreateTagAssignment(self):


        self.tag_assignment_groupbox = Eto.Forms.GroupBox()
        self.tag_assignment_groupbox.Text = "For Asset Manager use only.(Future function)"
        self.tag_assignment_groupbox.Padding = Eto.Drawing.Padding (10)
        group_layout = Eto.Forms.DynamicLayout()
        group_layout.Spacing = Eto.Drawing.Size(6,6)

        self.description_label = Eto.Forms.Label()
        self.description_label.Text = "Access Currently Allowed:{}".format(self.MANAGER_NAMES)
        self.tag_assignment_refresh_button = Eto.Forms.Button()
        self.tag_assignment_refresh_button.Text = "Refresh Tag Data Pool(Only use if want to see update on selection list.)"
        self.tag_assignment_refresh_button.Image = Eto.Drawing.Bitmap(r"L:\4b_Applied Computing\00_Asset Library\Database\app images\update_data.png")
        self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Right
        self.tag_assignment_refresh_button.Click += self.button_clicked_tag_assignment_refresh

        group_layout.AddSeparateRow(self.description_label , None, self.tag_assignment_refresh_button)
        self.TAG_ASSIGN_BUTTONS = []

        max_height = 50
        tag_buttons = [None]
        max_row_count = 12
        row_count = 0
        for b_name in self.TAG_DEFAULT_LIST:
            if row_count > max_row_count:
                tag_buttons.append(None)
                group_layout.AddSeparateRow(*tag_buttons)
                tag_buttons = [None]
                row_count = 0
            self.btn_Run = Eto.Forms.ToggleButton ()
            self.btn_Run.Height = max_height
            self.btn_Run.Text = b_name
            self.btn_Run.Image = Eto.Drawing.Bitmap(r"L:\4b_Applied Computing\00_Asset Library\Database\app images\checked_toggle_inactive.png")
            self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Overlay#behind text
            self.btn_Run.Click += self.button_clicked_tag
            #tag_buttons.append(None)
            tag_buttons.append(self.btn_Run)
            self.TAG_ASSIGN_BUTTONS.append(self.btn_Run)
            row_count += 1

        #for i in range(max_row_count-len(tag_buttons)):
            #tag_buttons.append(None)
        tag_buttons.append(None)
        group_layout.AddSeparateRow(*tag_buttons)

        self.tag_assignment_groupbox.Content = group_layout
        return self.tag_assignment_groupbox



    def read_item_tags(self, rhino_file_name):
        meta_data_file = r"{}\Database\data\{}".format(self.PRIMARY_FOLDER, rhino_file_name.replace("3dm", "meta"))
        if os.path.exists(meta_data_file):
            temp_dict = EA.read_txt_as_dict(filepath = meta_data_file, use_encode = False)
            self.ITEM_DOWNLOADS[rhino_file_name] = temp_dict["Download"]
        else:
            # assign a default no tag dict
            self.default_tag_data_reset()
            EnneadTab.DATA_FILE.save_dict_to_txt(self.META_DATA, meta_data_file, end_with_new_line = False)
            temp_dict = EA.read_txt_as_dict(filepath = meta_data_file, use_encode = False)

        OUT = []
        for key, value in temp_dict.items():
            if value == True:
                OUT.append(key.lower())

        return OUT

    def get_item_tags(self, rhino_file_name):
        return self.ITEM_TAG_POOL[rhino_file_name]


    # create a search function
    def Search(self):############################################################################################################################
        #########################################################################################################################################
        #########################################################################################################################################
        #########################################################################################################################################
        #########################################################################################################################################
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        text = self.tB_Search.Text
        include_list = list(self.checkbox_list_tag_filter.SelectedValues)
        exclude_list = list(set(self.TAG_DEFAULT_LIST) - set(include_list))

        """
        filter to has to include those keywords
        """
        def include_tag(x):
            if include_list == []:
                return True
            for tag in include_list:
                if tag.lower() not in x[0].lower():
                    return False
            else:
                return True

        def include_real_tag(x):
            if include_list == []:
                return True
            for tag in include_list:
                if tag.lower() not in self.get_item_tags(x[0]) and tag.lower() not in x[0].lower():
                    return False
            else:
                return True

        def OLD_exclude_tag(x):
            if include_list == []:
                return True
            for tag in exclude_list:
                if tag.lower() in x[0].lower():
                    return False
            return True


            # return list of tags that is true

            pass



        #print "%%%%%%%%%%%%%%"
        #print include_list
        #print exclude_list
        reduced_pool = filter(include_real_tag, self.ScriptList)
        #reduced_pool = filter(exclude_tag, reduced_pool)
        #print reduced_pool
        #print "$$$$$$$$$$$$$$$$"

        #  enable this line to disable tag filter
        #reduced_pool = self.ScriptList[::]

        if text == "":
            self.lb.DataStore = reduced_pool
        else:
            #print reduced_pool
            temp = [ [str(x[0])] for x in reduced_pool]

            #print temp

            #print flatten(temp)
            #print fnmatch.filter(flatten(temp), "*" + text + "*")
            #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
            #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))
            self.lb.DataStore = self.SearchedScriptList

        self.update_available_tags()
        #########################################################################################################################################
        #########################################################################################################################################
        #########################################################################################################################################
        #########################################################################################################################################

    def update_available_tags(self):
        """
        # dynamicaly find out what other tags can stay and update
        #self.checkbox_list_tag_filter.DataStore = ["aaaa", "ggg"]

        after the list is update, run a func and find what keyword tag is still possible to keep:
        ex. if a tag is shown in any item in current list, it should stay, else gone.

        record the value that is currently check, make a new tag list, set select as record.
        """
        checked_tags = list(self.checkbox_list_tag_filter.SelectedValues)
        possible_tags_pool = set()
        for item_name in self.lb.DataStore:
            for tag in self.TAG_DEFAULT_LIST:
                #print tag, item_name[0]
                if tag in checked_tags or tag.lower() in item_name[0].lower() or tag.lower() in self.get_item_tags(item_name[0]):
                    possible_tags_pool.add(tag)


        possible_tags = []
        for tag in self.TAG_DEFAULT_LIST:
            if tag in possible_tags_pool:
                possible_tags.append(tag)

        #print "%%%%%%%%%"
        #print possible_tags_pool
        #print possible_tags
        #print checked_tags

        self.IS_TAG_LIST_CHANGING = True
        self.checkbox_list_tag_filter.DataStore = possible_tags
        self.checkbox_list_tag_filter.SelectedValues = checked_tags
        self.IS_TAG_LIST_CHANGING = False






    def update_preview_image(self):
        #print list(self.lb.SelectedItems)[0][0]
        if self.lb.SelectedItems is not None:
            try:
                current_item = self.get_selected_item_item()
                image_path = r"{}\Database\data\{}".format(self.PRIMARY_FOLDER, current_item.replace("3dm", "png"))
            except IndexError:
                image_path = self.DEFAULT_IMAGE_NOTHING_SELECTED


        else:
           image_path = self.DEFAULT_IMAGE_NOTHING_SELECTED


        #print image_path
        try:
            temp_bitmap = Eto.Drawing.Bitmap(image_path)
        except Exception as e:
            print(str(e))
            temp_bitmap = Eto.Drawing.Bitmap(self.DEFAULT_IMAGE_CANNOT_FIND_PREVIEW_IMAGE)

        self.preview_image.Image = temp_bitmap.WithSize(self.IMAGE_MAX_SIZE,self.IMAGE_MAX_SIZE)
        self.Title  = image_path
        #print self.preview_image

    # function to run when call at button click
    def RunScript(self):
        # return selected items
        return self.lb.SelectedItems

    """
    ####  event call ##############################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################
    """
    # Gridview SelectedRows Changed Event
    def listbox_row_changed_main_grid_view (self,sender,e):

        self.update_preview_image()
        self.update_tag_assignment_status()
        return self.lb.SelectedRows


    # event handler handling text input in ther search bar
    def textbox_textchanged_search_bar(self, sender, e):
        self.Search()

    def button_clicked_search_bar_clear_text(self, sender, e):
        self.tB_Search.Text = ""



    # event handler handling clicking on the 'run' button
    def button_clicked_place_asset(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()


    def button_clicked_tag_assignment_refresh(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.update_item_tag_pool()
        self.Search()
        EnneadTab.NOTIFICATION.toast(main_text = "The tags data pool is updated.")




    # event handler handling clicking on the 'tag' button
    def button_clicked_tag(self, sender, e):



        data = dict()

        for button in self.TAG_ASSIGN_BUTTONS:
            if button.Checked:
                image = "checked_toggle_on.png"
            else:
                image = "checked_toggle_off.png"

            if self.is_nothing_selected():
                image = "checked_toggle_inactive.png"

            button.Image = Eto.Drawing.Bitmap(r"L:\4b_Applied Computing\00_Asset Library\Database\app images\{}".format(image))

            data[button.Text] = button.Checked


        data["Download"] = 0
        data["Capacity"] = -1
        self.META_DATA = data


        if self.lb.SelectedItems is None:
            return

        print(self.META_DATA)
        self.meta_data_write()


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)


    # event handler handling clicking on the 'clear tag filter' button
    def tag_button_clear(self, sender, e):
        # set checkbox list to None
        self.checkbox_list_tag_filter.SelectedValues  = []

        # call search() to update list
        self.Search()
        pass


    # event handler handling clicking on the tag any checkbox item
    def tag_box_update(self, sender, e):

        # call search() to update list
        if self.IS_TAG_LIST_CHANGING:
            return
        self.Search()
        pass


    # event handler handling clicking on the occupancy radio change item
    def occupancy_radiobutton_update(self, sender, e):

        # call search() to update list
        self.Search()
        pass


    """
    misc
    """
    def is_nothing_selected(self):
        if self.lb.SelectedItems is None:
            return True
        if list(self.lb.SelectedItems) == []:
            return True
        if list(self.lb.SelectedItems)[0][0] is None:
            return True
        return False


    def meta_data_write(self):
        if self.is_nothing_selected():
            return
        #print "$$$$$"
        #print list(self.lb.SelectedItems)
        current_item = self.get_selected_item_item()
        meta_data_file = r"{}\Database\data\{}".format(self.PRIMARY_FOLDER, current_item.replace("3dm", "meta"))

        try:
            EnneadTab.DATA_FILE.save_dict_to_txt(self.META_DATA, meta_data_file, end_with_new_line = False)
        except Exception as e:
            EnneadTab.NOTIFICATION.toast(main_text = str(e))

    def meta_data_read(self):
        if self.is_nothing_selected():
            return
        current_item = self.get_selected_item_item()
        meta_data_file = r"{}\Database\data\{}".format(self.PRIMARY_FOLDER, current_item.replace("3dm", "meta"))
        if os.path.exists(meta_data_file):
            return EA.read_txt_as_dict(filepath = meta_data_file, use_encode = False)
        else:
            # assign a default no tag dict
            self.default_tag_data_reset()
            self.meta_data_write()


    def default_tag_data_reset(self):
        data = dict()
        for button in self.TAG_ASSIGN_BUTTONS:

            data[button.Text] = False

        data["Download"] = 0
        data["Capacity"] = -1
        self.META_DATA = data


    def update_tag_assignment_status(self):
        if not self.MANAGER_MODE:
            return
        datas = self.meta_data_read()
        self.META_DATA = datas
        if self.META_DATA is None:
            return


        for button in self.TAG_ASSIGN_BUTTONS:
            if not self.META_DATA.has_key(button.Text):
                self.META_DATA[button.Text] = False
            button.Checked = self.META_DATA[button.Text]
            if button.Checked:
                image = "checked_toggle_on.png"
            else:
                image = "checked_toggle_off.png"

            if self.is_nothing_selected() or datas is None or datas == []:
                image = "checked_toggle_inactive.png"

            button.Image = Eto.Drawing.Bitmap(r"L:\4b_Applied Computing\00_Asset Library\Database\app images\{}".format(image))


    def get_selected_item_item(self):
        return [x[0] for x in self.lb.SelectedItems][0]

    def get_selected_item_download(self):
        return [x[1] for x in self.lb.SelectedItems][0]

    def get_listbox_data_store(self):
        return [[x[0], self.ITEM_DOWNLOADS[x[0]]] for x in sorted(self.SearchedScriptList)]



"""
####  outside dialog ################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
#####################################################################################################################################################
"""
@EnneadTab.ERROR_HANDLE.try_catch_error
def ShowImageSelectionDialog(image_list):


    # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
    formated_list = [[x[1]] for x in image_list]
    """
    i = 0
    while i < len(docLayers):
        to_do.append(docLayers[i:i+1])
        i += 1
    """

    dlg = ImageSelectionDialog(formated_list)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):


        OUT = [x[0] for x in dlg.RunScript()]
        OUT.sort()
        #pickedLayers.append(dlg.RunScript())

        #print OUT
        is_ref_block_method = False if "Embed" in dlg.radio_button_list_ref_block_method.SelectedValue else True
        if dlg.META_DATA.has_key("Download"):
            dlg.META_DATA["Download"] += 1
            dlg.meta_data_write()
        return OUT, is_ref_block_method

    else:
        print("Dialog did not run")
        return None, None

if __name__ == "__main__":


    image_list = [(r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-5-54.3dm', 'Setting-Meet-5-54.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-5-72x30.3dm', 'Setting-Meet-5-72x30.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-5-U-Sm.3dm', 'Setting-Meet-5-U-Sm.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-6-54.3dm', 'Setting-Meet-6-54.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-6-60.3dm', 'Setting-Meet-6-60.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-6-60x42.3dm', 'Setting-Meet-6-60x42.3dm'),
                    (r'L:\\4b_Applied Computing\\00_Asset Library\\Setting-Meet-6-63x27.3dm', 'Setting-Meet-6-63x27.3dm')]
    import traceback
    try:
        print(ShowImageSelectionDialog(image_list))
    except:
        error =  traceback.format_exc()
        print(error)
        filepath = r"C:\Users\szhang\Desktop\error.txt"

        EnneadTab.DATA_FILE.save_list_to_txt([error], filepath, end_with_new_line = False)
