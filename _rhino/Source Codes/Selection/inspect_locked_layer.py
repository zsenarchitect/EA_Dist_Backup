#import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
#import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def inspect_locked_layer():
    locked_layers, open_layers = get_force_selected_layer()
    if locked_layers is None and open_layers is None:
        EnneadTab.NOTIFICATION.toast(main_text = "Selection is not valid.")
        return


    #format the rhino layer to user layer
    output_text(locked_layers, they_are_locked = True)
    output_text(open_layers, they_are_locked = False)

def output_text(layers, they_are_locked):
    if len(layers) == 0:
        return

    display = ""
    for x in layers:
        display += "{}\n".format(EnneadTab.RHINO.RHINO_LAYER.rhino_layer_to_user_layer(x))
    rs.TextOut(message = "Within the selection, these layer(s) are currently {}:\n\n".format("LOCKED" if they_are_locked else "OPEN") + display)

def get_force_selected_layer():
    """
    this return the layer(s) of selected obj, if you want to activate them( unlock, or set as current), do those in the "activate locked layer by selection.py"
    """

    #remember all layers current lock status as STAGE_A
    all_layers = rs.LayerNames()
    layer_lock_status = dict()
    for layer in all_layers:
        print(layer, rs.IsLayerLocked(layer))
        layer_lock_status[layer] = rs.IsLayerLocked(layer)
    #the limitation right now is that if the sublayer is open but parent is locked,
    #after restore the lock stage, the sublayer will become true lock.

    #unlock all layers
    map(lambda x:rs.LayerLocked(x, locked = False), all_layers)

    #allow user to pick objs, record their layers
    objs = rs.GetObjects("Pick some objs")
    if not objs:
        return None, None
    selected_layers = set()
    for obj in objs:
        selected_layers.add(rs.ObjectLayer(obj))

    #restore all layer lock status by STAGE_A
    for layer in all_layers:
        rs.LayerLocked(layer, locked = layer_lock_status[layer])

    #return the layers user have selected but keep two outputs
    locked_layers = []
    open_layers = []
    for layer in list(selected_layers):
        if layer_lock_status[layer]:
            locked_layers.append(layer)
        else:
            open_layers.append(layer)

    locked_layers.sort()
    open_layers.sort()
    return locked_layers, open_layers


######################  main code below   #########
if __name__ == "__main__":
    inspect_locked_layer()
