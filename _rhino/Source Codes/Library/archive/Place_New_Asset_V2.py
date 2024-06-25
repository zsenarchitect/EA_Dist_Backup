import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import Place_New_Asset_V2_ETO_Forms
reload(Place_New_Asset_V2_ETO_Forms)


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
    Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)


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
        return True

    files = filter(is_good_file, files)


    block_names =  [("{}\{}".format(folder, file), file) for file in files]
    print(block_names)
    import traceback
    try:
        block_name, is_ref_block_method = Place_New_Asset_V2_ETO_Forms.ShowImageSelectionDialog(block_names,
                                                                                            title = "EnneadTab",
                                                                                            message = "Pick a asset to insert",
                                                                                            multi_select = False,
                                                                                            button_names = ["Place!"],
                                                                                            width = 400,
                                                                                            height = 600)
        print(block_name)
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
    EnneadTab.NOTIFICATION.toast(main_text = "I am V2 main")
    Place_New_Asset()

