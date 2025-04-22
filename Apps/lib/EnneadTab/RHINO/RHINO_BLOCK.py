import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # type: ignore

def replace_block(block_name_old, block_name_new):
    """Replace all instances of block_name_old with block_name_new in the active document.
    
    Args:
        block_name_old (str): Name of the block to be replaced
        block_name_new (str): Name of the block to replace with
    """
    # Get the active document
    doc = Rhino.RhinoDoc.ActiveDoc
    
    # Access the instance definition through the document
    new_definition = doc.InstanceDefinitions.Find(block_name_new)
    if not new_definition:
        print ("Cannot find [{}] in current document".format(block_name_new))
        return
    
    instances = rs.BlockInstances(block_name_old)
    if instances:
        for instance in instances:
            doc.Objects.ReplaceInstanceObject(instance, new_definition.Index)
    else:
        print ("Cannot find [{}] in current document".format(block_name_old))
