import rhinoscriptsyntax as rs
import scriptcontext as sc
import sys
sys.path.append("..\lib")


import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def merge_layer():

    layers_to_modify = rs.GetLayers(title="Select Layers to modify, use select button to get extra from Rhino viewport",
                                    show_new_button = False)

    layer_target = rs.GetLayer(title = "Select target layer", show_new_button = True)

    # print layers_to_modify
    # print layer_target
    #print_list(layers_to_modify)

    block_names = rs.BlockNames(sort = True)



    try:
        map(lambda x: modify_block(x,layers_to_modify, layer_target), block_names)
        map(lambda x: modify_obj_on_layer(x, layer_target), layers_to_modify)
        map(lambda x: rs.DeleteLayer(x), layers_to_modify)
    except Exception as e:
        display = "Sometime merging parent layer while containing child can raise error saying some of the child layer structure cannot be found. This is becasue thier parent have changed name.\n\nThe best way to avoid this is to start merging from the inner side and moveup the hierarchy one parent at a time.\n\n(If the error message below DOES NOT sound like the description above, please report to SenZhang, you might have discovered a bug. Thank you in advance!)\n\nError Message Below:\n\n" + str(e)
        rs.MessageBox(message = display, buttons= 0 | 48, title = "Too aggresive merging...")



def modify_obj_on_layer(current_layer, layer_target):

    objs =  rs.ObjectsByLayer(current_layer)
    rs.ObjectLayer(objs, layer_target)



def modify_block(block_name, layers_to_modify, layer_target):
    # print block_name
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

    # print geos
    # print attrs
    return


def print_list(list):
    temp = ""
    for x in list:
        temp += str(x) + "\n"
    rs.TextOut(message = temp)

##########################################################################

if( __name__ == "__main__" ):

  merge_layer()
