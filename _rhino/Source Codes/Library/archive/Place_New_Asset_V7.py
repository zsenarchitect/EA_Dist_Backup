import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import Place_New_Asset_V7_ETO_Forms as NEW_ASSET_ETO_FORMS
reload(NEW_ASSET_ETO_FORMS)


def insert_ref_block(block_name, is_ref_block_method):
    if rs.IsBlock(block_name):
        rs.InsertBlock(block_name, (0,0,0))
        return

    external_block_filepath = get_external_filepath(block_name)

    dummyInitialObjects = [Rhino.Geometry.Point(Rhino.Geometry.Plane.WorldXY.Origin)]
    dummyInitialAttributes = [Rhino.DocObjects.ObjectAttributes()]
    indexOfAddedBlock = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Add(block_name,
                                                                        "",
                                                                        Rhino.Geometry.Plane.WorldXY.Origin,
                                                                        dummyInitialObjects ,
                                                                        dummyInitialAttributes)


    if is_ref_block_method:
        block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Linked

    else:
        block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.LinkedAndEmbedded
        #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Static
        #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Embedded

    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(external_block_filepath),
                                                                                block_method,
                                                                                True)# bool for quite mode, no error msg shown
    obj = Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)

    if not is_ref_block_method:
        sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Blocks')
        import block_layer_packaging
        block_layer_packaging.pack_block_layers(blocks = [obj], flatten_layer = True)



        import imp
        MAKE_BLOCK_UNIQUE = imp.load_source('make block unique', r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Blocks\make block unique.py')
        #reload(MAKE_BLOCK_UNIQUE)
        MAKE_BLOCK_UNIQUE.make_block_unique(add_name_tag = False, original_blocks = [obj], treat_nesting = True)
        rs.DeleteBlock(block_name)
        rs.RenameBlock( "{}_new".format(block_name), block_name )


def get_external_filepath(block_name):

    folder = r"L:\4b_Applied Computing\00_Asset Library"
    if folder in block_name:
        return block_name


    files = EnneadTab.FOLDER.get_filenames_in_folder(folder)
    for file_name in files:
        if block_name in  file_name:
            return "{}\{}".format(folder, file_name)


@EnneadTab.ERROR_HANDLE.try_catch_error
def Place_New_Asset():

    folder = r"L:\4b_Applied Computing\00_Asset Library"
    files = EnneadTab.FOLDER.get_filenames_in_folder(folder)

    def is_good_file(name):
        if name.endswith(".3dm"):
            return True
        return False

    files = filter(is_good_file, files)


    block_names =  [("{}\{}".format(folder, file), file) for file in files]
    #print block_names
    import traceback
    try:
        block_name, is_ref_block_method = NEW_ASSET_ETO_FORMS.ShowImageSelectionDialog(block_names)
        #print block_name
        block_name = block_name[0]
        print("########", is_ref_block_method)
        insert_ref_block(block_name, is_ref_block_method)
    except:
        print(traceback.format_exc())
        return




######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    EnneadTab.NOTIFICATION.toast(main_text = "V7 main")
    Place_New_Asset()


"""
##The Search Paths options manage locations to search for bitmaps that used for render texture and bump maps.
rs.AddSearchPath(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EA_UTILITY.py')


import imp
ref_module = imp.load_source("sync_queue_monitor", r'L:\\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Revit\sync_queue_monitor.py')

rs.FindFile(filename)
Searches for a file using Rhino's search path. Rhino will look for a
    file in the following locations:
      1. The current document's folder.
      2. Folder's specified in Options dialog, File tab.
      3. Rhino's System folders
path = rs.FindFile("Rhino.exe")
print(path)


res = rs.StringBox(message = "type in text", default_value = "default", title = "EnneadTab")
print(res)

res = rs.RealBox(message="get a number", default_number = None, title = "EnneadTab", minimum = None, maximum = None)
print(res)

res = rs.GetString(message = "type in text or click options", strings = ["opt_1", "opt_2", "opt_3"])
print(res)

res = rs.EditBox(message = "type in text", default_string = "default string", title = "EnneadTab")
print(res)


rs.TextOut(message = "text to display\nLine 1\nLine 2", title = "EnneadTab")


rs.MessageBox(message = "text to display", buttons= 4 | 48, title = "EnneadTab")

layer = rs.GetLayer(title = "Select Layer", layer = None, show_new_button = True, show_set_current = True)


res = rs.ListBox(items = ["opt_1", "opt_2", "opt_3"], message =  "select one from below", title = "list box", default = None)
print(res)

res = rs.PopupMenu(items = ["opt_1", "opt_2", "opt_3", "opt_4"], modes = [0, 1, 2, 3])
print(res)


res = rs.MultiListBox(items = ["opt_1", "opt_2", "opt_3"], message = "select many from below", title = "mutil list box", defaults = None)
print(res)

res = rs.CheckListBox(items = [["opt_1", True], ["opt_2", False], ["opt_3", True]], message = "select options from below", title = "checklist box")
print(res)



res = rs.ComboListBox(items = ["opt_1", "opt_2", "opt_3"], message = "select options from below", title = "combo list box")
print(res)
for option, state in res:
    pass

res = rs.PropertyListBox(items = ["opt_1", "opt_2", "opt_3"], values = [1, 2, 3], message = "modify property", title = "propety list box")
print(res)









rhino read excel, and write
http://developer.rhino3d.com/guides/rhinoscript/reading-excel-files/


print(sc.doc ---> <Rhino.RhinoDoc object at 0x0000000000000084 [Rhino.RhinoDoc]>)
this is under Rhino Commons.   Rhino--->RHinoDoc


Rhino.RhinoObject.Select(True, True, True, False, True, False)

"""
