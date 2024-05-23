import rhinoscriptsyntax as rs
import scriptcontext as sc
import sys
sys.path.append("..\lib")

import EA_UTILITY as EA
import EnneadTab


def add_parent_to_layer(original_layer, parent_prefix):
    desired_layer = parent_prefix + "::" + original_layer
    rs.AddLayer(name = desired_layer)
    return desired_layer

def rhino_layer_to_user_layer(name):
    return "[{}]".format(name.replace("::", "] - ["))

def user_layer_to_rhino_layer(name):
    return name[1:-1].replace("] - [", "::")


@EnneadTab.ERROR_HANDLE.try_catch_error
def migrate_layer():

    all_layers = rs.LayerNames()
    all_layers_user = [rhino_layer_to_user_layer(x) for x in all_layers]
    """
    print(all_layers[10])
    temp = rhino_layer_to_user_layer(all_layers[10])
    print(temp)
    print(user_layer_to_rhino_layer(temp))
    """


    layers_to_modify = EnneadTab.RHINO.RHINO_FORMS.select_from_list(all_layers_user,
                                        title = "EnneadTab",
                                        message = "Select Layers to modify, hold 'shift' to select multiple.",
                                        multi_select = True,
                                        button_names = ["Select Multiple Layers"],
                                        width = 500,
                                        height = 500)

    parent_layer_prefix = rs.EditBox(default_string = None, message = "Enter text for the name of the parent layer", title = "Migrate Layers under another parent")
    """
    parent_layer_prefix = EnneadTab.RHINO.RHINO_FORMS.select_from_list(all_layers_user,
                                            title = "Migrate Layers under another parent",
                                            message = "Enter text for the name of the parent layer",
                                            multi_select = False,
                                            button_names = ["Select Single Layer as Parent"],
                                            width = 500,
                                            height = 500)[0]
    
    print(parent_layer_prefix)
    """
    layers_to_modify = [user_layer_to_rhino_layer(x) for x in layers_to_modify]
    layers_to_modify.sort(reverse = True)
    #layer_target = user_layer_to_rhino_layer(layer_target)
    # print layers_to_modify
    # print layer_target
    #print_list(layers_to_modify)

    block_names = rs.BlockNames(sort = True)



    try:
        map(lambda x: modify_block(x,layers_to_modify, parent_layer_prefix), block_names)
        map(lambda x: modify_obj_on_layer(x, parent_layer_prefix), layers_to_modify)
        map(lambda x: rs.DeleteLayer(x), layers_to_modify)
        temp = ""
        for x in layers_to_modify:
            temp += "{}\n".format(rhino_layer_to_user_layer(x))
        display = "Layers below have been merged under parental layer {}\n\n{}".format(rhino_layer_to_user_layer(parent_layer_prefix), temp)
        rs.MessageBox(message = display, buttons= 0 | 48, title = "Done")
    except Exception as e:
        display = "Sometime merging parent layer while containing child can raise error saying some of the child layer structure cannot be found. This is becasue thier parent have changed name.\n\nThe best way to avoid this is to start merging from the inner side and moveup the hierarchy one parent at a time.\n\n(If the error message below DOES NOT sound like the description above, please report to SenZhang, you might have discovered a bug. Thank you in advance!)\n\nError Message Below:\n\n" + str(e)
        rs.MessageBox(message = display, buttons= 0 | 48, title = "Too aggresive merging...")



def modify_obj_on_layer(current_layer, parent_layer_prefix):

    objs =  rs.ObjectsByLayer(current_layer)
    layer_target = add_parent_to_layer(current_layer, parent_layer_prefix)
    rs.ObjectLayer(objs, layer_target)



def modify_block(block_name, layers_to_modify, parent_layer_prefix):
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
            layer_target = add_parent_to_layer(current_layer, parent_layer_prefix)
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

  migrate_layer()
