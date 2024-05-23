import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import Place_New_Asset_V3_ETO_Forms as NEW_ASSET_ETO_FORMS
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
    sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Blocks')
    import block_layer_packaging
    block_layer_packaging.pack_block_layers(blocks = [obj], flatten_layer = True)


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
        if ".rhl"  in name:
            return False
        if ".3dm_tmp"  in name:
            return False
        if ".3dmbak"  in name:
            return False
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
    except:
        print(traceback.format_exc())
        return

    #block_names =  files
    #block_name = EnneadTab.RHINO.RHINO_FORMS.select_from_list(block_names, multi_select = False, message = "Pick a asset to insert")[0]
    print("########", is_ref_block_method)
    insert_ref_block(block_name, is_ref_block_method)




######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    EnneadTab.NOTIFICATION.toast(main_text = "V3 main")
    Place_New_Asset()

