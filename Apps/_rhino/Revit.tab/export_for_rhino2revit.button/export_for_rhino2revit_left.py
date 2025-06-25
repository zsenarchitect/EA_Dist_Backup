__title__ = "Rhino2Revit"
__doc__ = "Export Layer Contents to 3dm and dwg for Rhino2Revit in EnneadTab for Revit."
__is_popular__ = True
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Eto # pyright: ignore

FORM_KEY = 'export_for_rhino2revit_modeless_form'

import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations


from EnneadTab import NOTIFICATION, SPEAK, SOUND, ENVIRONMENT, CONFIG, DATA_FILE
from EnneadTab import LOG, ERROR_HANDLE , FOLDER
from EnneadTab.RHINO import RHINO_LAYER, RHINO_UI


# make modal dialog
class Rhino2RevitExporterDialog(Eto.Forms.Dialog[bool]):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Rhino2Revit Exporter"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 400
        self.width = 400

        all_layers = rs.LayerNames()
        self.ScriptList = [RHINO_LAYER.rhino_layer_to_user_layer(x) for x in all_layers]
        #print self.ScriptList
        self.SearchedScriptList = self.ScriptList[::]


        # initialize layout
        layout_A = Eto.Forms.DynamicLayout()
        layout_A.Padding = Eto.Drawing.Padding(5)
        layout_A.Spacing = Eto.Drawing.Size(5, 5)

        layout_A.BeginVertical()
        layout_A.AddRow(*self.CreateSearchBar())
        layout_A.EndVertical()

        # add listBox
        layout_A.BeginVertical()
        layout_A.AddRow(self.CreateScriptListBox())
        layout_A.EndVertical()
        layout_A.AddSeparateRow(*self.Create_Option_A_Buttons())
        layout_A.AddSeparateRow(*self.Create_Option_B_Buttons())





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
        layout.AddRow(layout_A)
        layout.EndVertical()

        # add checkbox for public address
        layout.BeginVertical()
        layout.AddRow(self.CreatePublicAddressCheckBox())
        layout.EndVertical()

        # add buttons
        layout.BeginVertical()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        # set content
        self.Content = layout
        
        RHINO_UI.apply_dark_style(self)



    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Pick layer(s) to export content over to Revit side with Rhino2Revit toolbox.\nContents inside blocks will be processed as well.\n\nOnly process objects that is not hidden."
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left


    def CreateExpander(self):
        self.expander = Eto.Forms.Expander ()
        self.expander.Header = "Quick Help"
        self.expander.Expanded = False
        msg = Eto.Forms.Label()
        msg.Text = "<.3dm Files>\nPros:\n\tStable, feel more similar to native Revit elements.\n\tIndividual control on Boolean, Subc, Visibility, Dimension Control\nCons:\n\tRequire Higer Standard of Cleaness in model.\n\tCannot handle curves.\n\n<.DWG Files>\nPros:\n\tMore tolerance on imperfection in models\n\tCan deal with lines, arcs and circle. Can also deal with Nurbs if all control points on same CPlane.\nCons:\n\tNo individual control for multiple elements, each import from same source file is glued.\n\tIntroduce Import SubC (which can be fixed automatically if using Revit side of )"
        msg.Text += "\n\nWith the exception of curve elements, .3dm is always prefered format, if it fails to convert, try some fix source model as far as you can. Check for Non-manifold geometry, surface devidation etc.\nUse .dwg as your last resort."
        self.expander.Content = msg
        return self.expander


    def CreatePublicAddressCheckBox(self):
        """
        Creates a checkbox for using public address
        """
        self.chk_use_public_address = Eto.Forms.CheckBox()
        self.chk_use_public_address.Text = "Use Public Address for large file.(L drive connection is required)"
        self.chk_use_public_address.Checked = False
        return self.chk_use_public_address


    # create search bar function
    def CreateSearchBar(self):
        """
        Creates two controls for the search bar
        self.lbl_Search as a simple label
        self.tB_Search as a textBox to input search strings to
        """
        self.lbl_Search = Eto.Forms.Label()
        self.lbl_Search.Text = "Type Here to search layers name"
        self.lbl_Search.VerticalAlignment = Eto.Forms.VerticalAlignment.Center

        self.tB_Search = Eto.Forms.TextBox()
        self.tB_Search.TextChanged += self.tB_Search_TextChanged

        return [self.lbl_Search, self.tB_Search]



    def CreateScriptListBox(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.list_box = Eto.Forms.GridView()
        self.list_box.ShowHeader = True
        self.list_box.AllowMultipleSelection = True
        self.list_box.Height = self.height
        self.list_box.AllowColumnReordering = True

        self.list_box.DataStore = [[x, False, False] for x in sorted(self.ScriptList)]
        self.record = dict()
        for x in self.ScriptList:
            self.record[str(x)] = [False, False]
        #print sorted(self.ScriptList_B)
        #print self.list_box.DataStore

        self.list_box.SelectedRowsChanged += self.RowsChanged
        #self.list_box.CellClick  += self.event_cell_click

        # Create Gridview Column
        column0 = Eto.Forms.GridColumn()
        column0.Editable = False
        column0.Width = self.width
        column0.HeaderText = "Layers"
        column0.DataCell = Eto.Forms.TextBoxCell(0)
        self.list_box.Columns.Add(column0)

        column1 = Eto.Forms.GridColumn()
        column1.Editable = True
        column1.Width = 100
        column1.HeaderText = "Export as .3dm"
        column1.DataCell = Eto.Forms.CheckBoxCell(1)
        self.list_box.Columns.Add(column1)

        column2 = Eto.Forms.GridColumn()
        column2.Editable = True
        column2.Width = 100
        column2.HeaderText = "Export as .dwg"
        column2.DataCell = Eto.Forms.CheckBoxCell(2)
        self.list_box.Columns.Add(column2)

        return self.list_box



    def Create_Option_A_Buttons(self):

        buttons = []

        self.btn_check_A = Eto.Forms.Button()
        self.btn_check_A.Text = ".3dm Check Selected"
        self.btn_check_A.Click += self.btn_A_check_Clicked

        self.btn_uncheck_A = Eto.Forms.Button()
        self.btn_uncheck_A.Text = ".3dm UnCheck Selected"
        self.btn_uncheck_A.Click += self.btn_A_uncheck_Clicked


        buttons.extend([ None, self.btn_check_A, self.btn_uncheck_A])
        return buttons


    def Create_Option_B_Buttons(self):

        buttons = []



        self.btn_check_B = Eto.Forms.Button()
        self.btn_check_B.Text = ".dwg Check Selected"
        self.btn_check_B.Click += self.btn_B_check_Clicked

        self.btn_uncheck_B = Eto.Forms.Button()
        self.btn_uncheck_B.Text = ".dwg UnCheck Selected"
        self.btn_uncheck_B.Click += self.btn_B_uncheck_Clicked

        buttons.extend([ None, self.btn_check_B, self.btn_uncheck_B])
        return buttons


    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Export Layers"
        self.btn_Run.Click += self.btn_Run_Clicked
        user_buttons.append(self.btn_Run)

        self.btn_select_all = Eto.Forms.Button()
        self.btn_select_all.Text = "Select All"
        self.btn_select_all.Click += self.btn_select_all_Clicked
        user_buttons.append(self.btn_select_all)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked

        user_buttons.extend([ None, self.btn_Cancel])
        return user_buttons


    def update_ListBox_DataStore(self, source_list):
        self.list_box.DataStore = [[x, self.record[str(x)][0], self.record[str(x)][1]] for x in sorted(source_list)]
        #print "^^&^"
        #print self.list_box.DataStore




    # create a search function
    def search_action(self, text):
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        self.update_record()
        if text == "":
            #self.update_ListBox_DataStore(source_list = self.ScriptList)
            self.SearchedScriptList = self.ScriptList
        else:
            #print self.ScriptList
            temp = [ [str(x)] for x in self.ScriptList]
            #print "AAAAAA"
            #print self.ScriptList
            #print "BBBBBBB"
            #print temp

            #print flatten(temp)
            #print fnmatch.filter(flatten(temp), "*" + text + "*")
            #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
            #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            self.SearchedScriptList = [x[0] for x in self.SearchedScriptList]
            #print self.SearchedScriptList
            #self.SearchedScriptList = fnmatch.filter(flatten(temp), "*" + text + "*")


            #print "*******"
            #print self.SearchedScriptList
            #[('Default',), ('Layer 01',), ('Layer 02',), ('Layer 03',), ('Layer 04',), ('Layer 05',)]

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))

        self.update_ListBox_DataStore(source_list = self.SearchedScriptList)




    # Gridview SelectedRows Changed Event
    def RowsChanged (self,sender,e):
        return
        #print "aaa"
        if list(self.list_box.SelectedItems) != []:
            self.update_record(reset = False)
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print list(self.list_box.SelectedItems)
            #entry, check_3dm, check_dwg = list(self.list_box.SelectedItems)[0]
            #self.record[entry] = [check_3dm, check_dwg]
            self.update_ListBox_DataStore(source_list = self.SearchedScriptList)
        return self.list_box.SelectedRows



    def event_cell_click(self, sender, e):
        return

        """
        if list(self.list_box.SelectedItems) == []:
            return
        if e.Column == 0:
            print("column 0")
            for entry, check_3dm, check_dwg in list(self.list_box.SelectedItems):
                self.record[entry] = not list(self.list_box.SelectedItems)[0]
            self.update_ListBox_DataStore(source_list = self.SearchedScriptList)
        pass
        """


    def update_record(self, reset = False):

        #print list(self.list_box.DataStore)
        if list(self.list_box.DataStore) != []:
            for  entry, check_3dm, check_dwg in list(self.list_box.DataStore):
                #print checked , entry
                if reset:
                    self.record[str(entry)] = [False, False]
                else:
                    self.record[str(entry)] = [check_3dm, check_dwg]



    # function to run when call at button click
    def RunScript(self):
        # return selected items
        """
        for A, change to all cheked item only
        """
        #print self.list_box.DataStore

        selected_data = filter(lambda x: x[1] or x[2], self.list_box.DataStore)
        use_public_address = self.chk_use_public_address.Checked
        return selected_data, use_public_address



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged(self, sender, e):
        self.search_action(self.tB_Search.Text)



    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()


    def btn_select_all_Clicked(self, sender, e):
        # Select all items in the list box
        for i in range(len(self.list_box.DataStore)):
            self.list_box.SelectRow(i)

    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)




    def btn_A_check_Clicked(self, sender, e):
        self.unify_A_selection(target_boolean = True)


    def btn_A_uncheck_Clicked(self, sender, e):
        self.unify_A_selection(target_boolean = False)


    def unify_A_selection(self, target_boolean = True):
        for entry, check_3dm, check_dwg in list(self.list_box.SelectedItems):
            self.record[entry] = [target_boolean, check_dwg]
        self.update_ListBox_DataStore(source_list = self.SearchedScriptList)



    def btn_B_check_Clicked(self, sender, e):
        self.unify_B_selection(target_boolean = True)


    def btn_B_uncheck_Clicked(self, sender, e):
        self.unify_B_selection(target_boolean = False)


    def unify_B_selection(self, target_boolean = True):
        for entry, check_3dm, check_dwg in list(self.list_box.SelectedItems):
            self.record[entry] = [check_3dm, target_boolean]
        self.update_ListBox_DataStore(source_list = self.SearchedScriptList)



class ToggleSaveDocumentHandler:

    def __enter__(self):
        CONFIG.set_setting("is_update_dist_repo_enabled", False)
        print ("is_update_dist_repo_enabled set to False")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        CONFIG.set_setting("is_update_dist_repo_enabled", True)
        print ("is_update_dist_repo_enabled set to True")

def get_output_folder(use_public_address=False):

   
    try:
    
        doc_name = sc.doc.Name.split(".3dm")[0]

    except:
        doc_name = "Untitled"
    
    if use_public_address:
        temp_folder = ENVIRONMENT.PUBLIC_TEMP_FOLDER
        EA_export_folder = "{}\EnneadTab Export By Layer from [{}]".format(temp_folder, doc_name)
    else:
        EA_export_folder = "{}\EnneadTab Export By Layer from [{}]".format(ENVIRONMENT.ONE_DRIVE_DESKTOP_FOLDER, doc_name)
    
    if not os.path.exists(EA_export_folder):
        os.makedirs(EA_export_folder)


    return EA_export_folder


def export(output_folder, datas):
    rs.EnableRedraw(False)




    block_collection = []
    all_block_names = rs.BlockNames( sort = False )
    for block_name in all_block_names:
        """on second thought, link block is ok to process
        if not rs.IsBlockEmbedded(block_name):
            continue
        """
        if rs.IsBlockReference(block_name):
            continue
        try:
            blocks = rs. BlockInstances(block_name)
        except:
            print ("Bad block name: " + block_name)
            continue
        blocks = [x for x in blocks if not rs.IsObjectHidden(x) and not rs.IsObjectLocked(x)]
        block_collection.extend(blocks)

    block_collection_trash = rs.CopyObjects(block_collection)


    trash_geo = []
    if block_collection_trash is not None:
        for block in block_collection_trash:
            try:
                trash_geo.extend(rs.ExplodeBlockInstance(block, explode_nested_instances = True))
            except Exception as e:
                print (e)
                continue



    rs.StatusBarProgressMeterShow(label = "Exporting {} Layers to .3dm/.dwg".format(len(datas)),
                                lower = 0,
                                upper = len(datas),
                                embed_label = True,
                                show_percent = True)

    out_path_dict = {"3dm_out_paths": [], "dwg_out_paths": [], "layer_material_mapping": {}}
    for i, data in enumerate(datas):
        rs.StatusBarProgressMeterUpdate(position = i, absolute = True)
        entry, check_3dm, check_dwg = data
        layer = RHINO_LAYER.user_layer_to_rhino_layer(entry)
        if not rs.IsLayerVisible(layer):
            continue

        rs.UnselectAllObjects()
        raw_objs = rs.ObjectsByLayer(layer, select = False)
        filter = rs.filter.instance
        objs = [obj for obj in raw_objs if rs.ObjectType(obj)!= filter]


        if check_3dm or check_dwg:
            # avoid situation where there are only non solid geo, such as curve and text, in the final export
            objs = [x for x in objs if rs.IsSurface(x) or rs.IsPolysurface(x) or rs.IsMesh(x)]

        objs = [x for x in objs if not rs.IsObjectHidden(x) and not rs.IsObjectLocked(x)]
        if len(objs) == 0:
            continue
            
        rs.SelectObjects(objs)


        file_name_naked = FOLDER.secure_legal_file_name(layer)


        for ost_name in ["Generic Models_"]:
            if ost_name in file_name_naked:
                file_name_naked = file_name_naked.replace(ost_name, "")

        layer_name = file_name_naked
        material_index = rs.LayerMaterialIndex(layer)
        layer_mat_name = rs.MaterialName(material_index) if material_index != -1 else None
        
        # Get material color using the material object directly
        material_color = None
        if material_index != -1:
            try:
                material = sc.doc.Materials[material_index]
                if material:
                    diffuse = material.DiffuseColor
                    material_color = (diffuse.R, diffuse.G, diffuse.B)
            except:
                material_color = None
                
        out_path_dict["layer_material_mapping"][layer_name] = {"material_name": layer_mat_name, "material_color": material_color}


                
        if check_3dm:
            file = "{}.3dm".format(file_name_naked)
            filepath = "{}\{}".format(output_folder, file)
            out_path_dict["3dm_out_paths"].append(filepath)
            rs.Command("!_-Export \"{}\" -Enter -Enter".format(filepath), echo = False)
        if check_dwg:
            file = "{}.dwg".format(file_name_naked)
            filepath = "{}\{}".format(output_folder, file)
            out_path_dict["dwg_out_paths"].append(filepath)
            rs.Command("!_-Export \"{}\" Scheme  \"2007 Solids\" -Enter -Enter".format(filepath), echo = False)


    rs.StatusBarProgressMeterHide()


    rs.DeleteObjects(trash_geo)
    rs.UnselectAllObjects()

    DATA_FILE.set_data(out_path_dict, "rhino2revit_out_paths")
    NOTIFICATION.messenger(main_text = "{} layers exported!".format(len(datas)))
    announcement = "{} layers content exported".format(len(datas))
    SPEAK.speak(announcement)
    SOUND.play_sound()





@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def export_for_rhino2revit():
    dlg = Rhino2RevitExporterDialog()
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
    if (rc):
        result = dlg.RunScript()
        if result:
            datas, use_public_address = result
            EA_export_folder = get_output_folder(use_public_address)
            with ToggleSaveDocumentHandler():
                export(EA_export_folder, datas)
        return
    else:
        print ("Dialog did not run")
        return

if __name__ == "__main__":
    export_for_rhino2revit()