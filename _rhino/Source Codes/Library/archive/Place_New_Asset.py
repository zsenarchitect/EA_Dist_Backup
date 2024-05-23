import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab


def insert_ref_block(block_name):
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


    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(external_block_filepath),
                                                                                Rhino.DocObjects.InstanceDefinitionUpdateType.	Linked,
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
    """
    folder = r"L:\4b_Applied Computing\00_Asset Library"     
    files = EnneadTab.FOLDER.get_filenames_in_folder(folder)
    image_list = [("{}\{}".format(folder, file_name), file_name) for file_name in files]
    print(image_list)
    image_path = EA.select_from_image_list(image_list,
                                            title = "EnneadTab",
                                            message = "test message",
                                            multi_select = True,
                                            button_names = ["Run Me"],
                                            width = 500,
                                            height = 500)


    return
    """

    """
    below can work for sure
    """
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
    block_names = ["Furn-Desk-L-42x42x30",
                    "Furn-Desk-I-42x24-Privacy"]

    block_names =  [("{}\{}".format(folder, file), file) for file in files]
    print(block_names)
    import traceback
    try:
        block_name = EA.select_from_image_list(block_names, multi_select = False, message = "Pick a asset to insert")
        print(block_name)
        block_name = block_name[0]
    except:
        print(traceback.format_exc())
        return

    #block_names =  files
    #block_name = EnneadTab.RHINO.RHINO_FORMS.select_from_list(block_names, multi_select = False, message = "Pick a asset to insert")[0]
    insert_ref_block(block_name)

    


######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    Place_New_Asset()


