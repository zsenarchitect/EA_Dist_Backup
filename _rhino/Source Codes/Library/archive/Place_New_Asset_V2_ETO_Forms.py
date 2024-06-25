
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

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
EnneadTab.NOTIFICATION.toast(main_text = "I am V2 eto")

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations

# make modal dialog
class ImageSelectionDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    def __init__(self, options, title, message,  multi_select, button_names , width, height):
        # Eto initials
        self.Title = title + "V2"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = height
        self.width = width
        self.multi_select = multi_select
        self.Message = message
        self.Button_Names = button_names
        self.DEFAULT_IMAGE = r"L:\4b_Applied Computing\00_Asset Library\Asset Preview Images\DEFAULT PREVIEW(DO NOT DELETE).png"
        self.DEFAULT_MISSING_IMAGE = r"L:\4b_Applied Computing\00_Asset Library\Asset Preview Images\DEFAULT PREVIEW_MISSING(DO NOT DELETE).png"
        self.IMAGE_MAX_SIZE = 800

        # fields
        #self.ScriptList = self.InitializeScriptList()
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
        left_layout.AddRow(self.CreateScriptListBox())
        left_layout.EndVertical()

        # add buttons
        left_layout.BeginVertical()
        left_layout.AddSeparateRow(self.CreateControlBox())
        left_layout.EndVertical()


        # add buttons
        left_layout.BeginVertical()
        left_layout.AddSeparateRow(*self.CreateButtons())
        left_layout.EndVertical()

        # add previews
        preview_image_layout = Eto.Forms.DynamicLayout()
        preview_image_layout.Padding = Eto.Drawing.Padding(5)
        preview_image_layout.Spacing = Eto.Drawing.Size(5, 5)
        preview_image_layout.BeginHorizontal()
        preview_image_layout.AddColumn(self.CreatePreviewImage())
        preview_image_layout.EndHorizontal()

        layout.AddRow(left_layout,preview_image_layout)

        # set content
        self.Content = layout



    # collect data for list
    def InitializeScriptList(self):
        return allDocLayers
        #return sorted(allDocLayers)


    # create preview image bar function
    def CreatePreviewImage(self):
        self.preview_image = Eto.Forms.ImageView()
        temp_bitmap = drawing.Bitmap(self.DEFAULT_IMAGE)
        self.preview_image.Image = temp_bitmap.WithSize(self.IMAGE_MAX_SIZE,self.IMAGE_MAX_SIZE)
        return self.preview_image


    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = self.Message
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    # create control boxn
    def CreateControlBox(self):
        self.block_insert_method_groupbox = Eto.Forms.GroupBox()
        self.block_insert_method_groupbox.Text = "How to insert block?"
        self.block_insert_method_groupbox.Padding = drawing.Padding (10)
        group_layout = Eto.Forms.DynamicLayout()
        group_layout.Spacing = drawing.Size(6,6)

        self.radio_button_list_ref_block_method = Eto.Forms.RadioButtonList()
        self.radio_button_list_ref_block_method.DataStore = ["As Ref Link", "Embed In Current File*"]
        self.radio_button_list_ref_block_method.Orientation = Eto.Forms.Orientation.Vertical
        self.radio_button_list_ref_block_method.SelectedIndex = 1
        self.radio_button_list_ref_block_method.Spacing = Eto.Drawing.Size(10,20)
        self.radio_button_list_ref_block_method.Padding = Eto.Drawing.Padding(10,5, 5, 5)


        self.ref_block_method_label = Eto.Forms.Label()
        self.ref_block_method_label.Text = "Note: \nUsing ref link will keep file light and layer clear, but you dont have ability to modify geomtry, material or use MakeBlockUnique.\nUsing embed block will make it a local block and lose connection to L drive.\n\n* Foot note: technically the block still listen to L drive, when you attempt to edit, you can break the connection at the prompt."

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

        self.tB_Search = Eto.Forms.TextBox()
        self.tB_Search.TextChanged += self.tB_Search_TextChanged

        return [self.lbl_Search, self.tB_Search]



    def CreateScriptListBox(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb = forms.GridView()
        self.lb.ShowHeader = True
        self.lb.AllowMultipleSelection = self.multi_select
        self.lb.Height = self.height
        self.lb.AllowColumnReordering = True


        self.lb.DataStore = sorted(self.ScriptList)
        #self.lb.DataStore = [x.split("00_Asset Library\\")[1] for x in self.ScriptList]

        self.lb.SelectedRowsChanged += self.RowsChanged


        # Create Gridview Column
        column1 = forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = forms.TextBoxCell(0)
        self.lb.Columns.Add(column1)

        self.lb.DataStore = self.SearchedScriptList
        #self.lb.DataStore = [x[0].split("00_Asset Library\\")[1] for x in self.SearchedScriptList]


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
            self.btn_Run.Click += self.btn_Run_Clicked
            user_buttons.append(self.btn_Run)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked
        self.btn_Cancel.Height = max_height

        user_buttons.extend([ None, self.btn_Cancel])


        return user_buttons



    # create a search function
    def Search(self, text):
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        if text == "":
            self.lb.DataStore = self.ScriptList
        else:
            print(self.ScriptList)
            temp = [ [str(x[0])] for x in self.ScriptList]
            print(temp)
            print(flatten(temp))
            print(fnmatch.filter(flatten(temp), "*" + text + "*"))
            print(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            print(list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)))

            self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))
            self.lb.DataStore = self.SearchedScriptList


    # Gridview SelectedRows Changed Event
    def RowsChanged (self,sender,e):

        self.update_preview_image()

        return self.lb.SelectedRows

    def update_preview_image(self):
        #print list(self.lb.SelectedItems)[0][0]
        if self.lb.SelectedItems is not None:
            current_item = list(self.lb.SelectedItems)[0][0]
            image_path = r"L:\4b_Applied Computing\00_Asset Library\Asset Preview Images\{}".format( current_item.replace("3dm", "png"))
        else:
           image_path = self.DEFAULT_IMAGE


        print(image_path)
        try:
            temp_bitmap = drawing.Bitmap(image_path)
        except Exception as e:
            print(str(e))
            temp_bitmap = drawing.Bitmap(self.DEFAULT_MISSING_IMAGE)

        self.preview_image.Image = temp_bitmap.WithSize(self.IMAGE_MAX_SIZE,self.IMAGE_MAX_SIZE)
        self.Title  = image_path
        #print self.preview_image

    # function to run when call at button click
    def RunScript(self):
        # return selected items
        return self.lb.SelectedItems



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged(self, sender, e):
        self.Search(self.tB_Search.Text)



    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)


@EnneadTab.ERROR_HANDLE.try_catch_error
def ShowImageSelectionDialog(image_list,
                                title = "EnneadTab",
                                message = "",
                                multi_select = False,
                                button_names = ["Run"],
                                width = 300,
                                height = 200):


    # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
    formated_list = [[x[1]] for x in image_list]
    """
    i = 0
    while i < len(docLayers):
        to_do.append(docLayers[i:i+1])
        i += 1
    """

    dlg = ImageSelectionDialog(formated_list, title, message, multi_select, button_names, width, height)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):


        OUT = [x[0] for x in dlg.RunScript()]
        OUT.sort()
        #pickedLayers.append(dlg.RunScript())

        #print OUT
        is_ref_block_method = False if "Embed" in dlg.radio_button_list_ref_block_method.SelectedValue else True
        return OUT, is_ref_block_method

    else:
        print("Dialog did not run")
        return None

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
        print(ShowImageSelectionDialog(image_list,)
                                        title = "EnneadTab",
                                        message = "",
                                        multi_select = False,
                                        button_names = ["Run"],
                                        width = 300,
                                        height = 200)
    except:
        error =  traceback.format_exc()
        print(error)
        filepath = r"C:\Users\szhang\Desktop\error.txt"

        EnneadTab.DATA_FILE.save_list_to_txt([error], filepath, end_with_new_line = False)
