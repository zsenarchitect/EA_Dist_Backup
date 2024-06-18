import rhinoscriptsyntax as rs
import scriptcontext as sc
import toggle_seating_display as TSD

import sys
sys.path.append("..\lib")
import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def bake_seating_display():


    layers = TSD.get_seat_crv_layers()
    layers = EnneadTab.RHINO.RHINO_LAYER.get_layers(multi_select = True, message = "Which crv(s) layer to bake? Multiple select supported.", layers = layers)
    #layers = rs.MultiListBox(layers, message = "Which crv(s) layer to bake? Multiple select supported.", title = "bake seats preview")
    key = "EA_SEATING_BAKING_LAYERS"
    sc.sticky[key] = layers


    key = "EA_SEATING_IS_BAKING"
    sc.sticky[key] = True

if __name__=="__main__":
    #showinscript()
    #showafterscript()
    bake_seating_display()
    #testing()




    """
    ideas:
    right click to set desired GFA to each layer name, save to external text. and live compare how much is off from target.
    """
