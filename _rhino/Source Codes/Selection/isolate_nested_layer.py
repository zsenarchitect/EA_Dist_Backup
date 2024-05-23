import sys
sys.path.append("..\lib")
import EnneadTab
#import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
#import scriptcontext as sc

"""
### TO-DO:
- Only works for one parent layer, not multiple levels
- Does not work for nested layers
#### Assigned to: **CM**
"""

@EnneadTab.ERROR_HANDLE.try_catch_error
def isolate_nested_layer():


    objs = rs.GetObjects("Pick some objs", preselect  = True)
    if not objs:
        return
    selected_layers = set()
    for obj in objs:
        selected_layers.add(rs.ObjectLayer(obj))
    
    family_layers = set()
    for layer in list(selected_layers):
        immediate_parent_layer = rs.ParentLayer(layer)
        family_layers.add(immediate_parent_layer)
        cousin_layers = rs.LayerChildren(immediate_parent_layer)
        if cousin_layers is None:
            continue
        for cousin_layer in cousin_layers:
            family_layers.add(cousin_layer)
        
    all_involved_layers = selected_layers.union(family_layers)
    obj_by_layers = []
    for layer in list(all_involved_layers):
        obj_by_layers.extend(rs.ObjectsByLayer(layer, True))

    invert_objs = rs.InvertSelectedObjects(include_lights = True)
    rs.HideObjects(invert_objs)
    
    
    
    
    
    
    


######################  main code below   #########
if __name__ == "__main__":
    isolate_nested_layer()
