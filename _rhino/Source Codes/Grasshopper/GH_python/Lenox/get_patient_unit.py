import os
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
import sys
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab

__doc__ = """Get the patient unit rhino file by rhino file name"""

input_list = [("OptionName", "String", "name of the rhinoi file, without extension")]
output_list = [("FilePath", "String", "Full path of the file"),
               ("BlockDefinition", "InstanceDefinition", "The rhino link definition of the rhino file"),]

basic_doc = """Get the patient unit rhino file by rhino file name"""

########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)

# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))
#############  input below  ########################

option_name = OptionName

############## main design below #########

folder = "J:\\1643\\0_3D\\00_Analysis\\patient unit"
file_path = "{}\\{}.3dm".format(folder, option_name)
print ("the final rhinoi path is \n{}".format(file_path))


import Rhino # pyright: ignore

def insert_block_as_link(file_path):
    exisiting_definition = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Find(option_name)
    if exisiting_definition is not None:
        EnneadTab.NOTIFICATION.messenger(main_text = "<{}> block already exist. Refreshing...".format(option_name))
        Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.RefreshLinkedBlock(exisiting_definition)
        return exisiting_definition
    
    dummyInitialObjects = [Rhino.Geometry.Point(Rhino.Geometry.Plane.WorldXY.Origin)]
    dummyInitialAttributes = [Rhino.DocObjects.ObjectAttributes()]
    indexOfAddedBlock = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Add(option_name,
                                                                        "",
                                                                        Rhino.Geometry.Plane.WorldXY.Origin,
                                                                        dummyInitialObjects ,
                                                                        dummyInitialAttributes)



    # block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Linked
    #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Static
    #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Embedded
    block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.LinkedAndEmbedded

    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(file_path),
                                                                                block_method,
                                                                                True)# bool for quite mode, no error msg shown
    if modified:
        EnneadTab.NOTIFICATION.messenger(main_text = "{} block added successfully as {}".format(option_name, block_method))
    obj = Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)
    
    exisiting_definition = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Find(option_name)
    return exisiting_definition

if option_name not in [None, ""]:

    block_definition = insert_block_as_link(file_path)
else:
    block_definition = None

############## output below   #################
FilePath = file_path
BlockDefinition = block_definition