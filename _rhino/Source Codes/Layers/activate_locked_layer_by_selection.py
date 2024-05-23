#import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
#import scriptcontext as sc

import sys
sys.path.append("..\lib")
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Selection')
import EnneadTab
import inspect_locked_layer

@EnneadTab.ERROR_HANDLE.try_catch_error
def activate_locked_layer_by_selection():
    locked_layers, open_layers = inspect_locked_layer.get_force_selected_layer()
    for layer in locked_layers:
        rs.LayerLocked(layer, locked = False)
        set_parent_layer_unlock(layer)


def set_parent_layer_unlock(layer):
    parent_layer = rs.ParentLayer(layer)
    if parent_layer is None:
        return
    rs.LayerLocked(parent_layer, locked = False)
    set_parent_layer_unlock(parent_layer)


######################  main code below   #########
if __name__ == "__main__":
    activate_locked_layer_by_selection()
