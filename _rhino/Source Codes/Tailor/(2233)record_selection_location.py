import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys


sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)




@EnneadTab.ERROR_HANDLE.try_catch_error
def record_selection_location():
    rs.EnableRedraw(False)
    layer = rs.StringBox("Layer of the special selection", default_value= "Frit Glass 5847sm 8%")
    objs = rs.ObjectsByLayer(layer)
    if not objs:
        rs.MessageBox("No objects in the layer")
        return

    data = dict()
    for obj in objs:
        pt = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(obj)
        data[obj.ToString()] = [pt.X, pt.Y, pt.Z]
        
 
    EnneadTab.DATA_FILE.save_dict_to_json_in_dump_folder(data, "temp_selection_location.json", use_encode = False)
    print(data)

######################  main code below   #########
if __name__ == "__main__":

    record_selection_location()

