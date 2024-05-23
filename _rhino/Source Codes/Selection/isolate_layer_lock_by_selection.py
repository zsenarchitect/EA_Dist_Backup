import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext

@EnneadTab.ERROR_HANDLE.try_catch_error
def isolate_layer():
    ids = rs.SelectedObjects(include_lights = True, include_grips = False)
    if not ids: return

    used_layers = set()
    obj_by_layers = []
    for id in ids:
        layer = rs.ObjectLayer(id)
        used_layers.add(layer)

    for layer in list(used_layers):
        obj_by_layers.extend(rs.ObjectsByLayer(layer, True))

    invert_objs = rs.InvertSelectedObjects(include_lights = True)
    rs.LockObjects(invert_objs)



    rs.UnselectObjects(obj_by_layers)


if __name__=="__main__":
    isolate_layer()
