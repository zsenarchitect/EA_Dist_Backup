import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext as sc

@EnneadTab.ERROR_HANDLE.try_catch_error
def merge_layer():

    #objectId = rs.GetObject("Select objects")
    # Get all layer names
    
   
    
    layers_to_modify = rs.GetLayers(title="Select Layers to modify",  
                                    show_new_button = False)
    
    layer_target = rs.GetLayer(title = "Select target layer", show_new_button = True)
    
    
    print(layers_to_modify)
    print(layer_target)
    #print_list(layers_to_modify)
    
    
    block_names = rs.BlockNames(sort = True)
    #modify_block(block_names[0],layers_to_modify, layer_target)
    #return
    
    
    
    map(lambda x: modify_block(x,layers_to_modify, layer_target), block_names)
    
    #all_layer_names = rs.LayerNames()
    map(lambda x: modify_obj_on_layer(x, layer_target), layers_to_modify)
    
    map(lambda x: rs.DeleteLayer(x), layers_to_modify)
    return
    for layer in layers_to_modify:
        rs.DeleteLayer(layer)
    
    
    
def modify_obj_on_layer(current_layer, layer_target):
    
    objs =  rs.ObjectsByLayer(current_layer)
    rs.ObjectLayer(objs, layer_target)
    
    
    
def modify_block(block_name, layers_to_modify, layer_target):
    print(block_name)
    block_definition = sc.doc.InstanceDefinitions.Find(block_name)
    objs = block_definition.GetObjects()
    geos = []
    attrs = []
    for i , obj in enumerate(objs):
        geos.append(obj.Geometry)
        attrs.append(obj.Attributes)
        current_layer = rs.ObjectLayer(obj)
        if current_layer in layers_to_modify:
            rs.ObjectLayer(obj, layer_target)
    
    print(geos)
    print(attrs)
    return



def print_list(list):
    temp = ""
    for x in list:
        temp += str(x) + "\n"
    rs.TextOut(message = temp)
    


##########################################################################

if( __name__ == "__main__" ):

  merge_layer()