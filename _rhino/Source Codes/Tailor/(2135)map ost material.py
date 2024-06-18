import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab

def select_key_layer(datas):

    options = [data.split("-->")[0] for data in datas]
    manual_key = "[...Do All Categories Below...]"
    options.insert(0, manual_key)
    selected_layer_keys = EnneadTab.RHINO.RHINO_FORMS.select_from_list(options,
                                title = "EnneadTab",
                                message = "Only process layer with those keywords",
                                multi_select = True)


    if manual_key in selected_layer_keys:
        process_all = True
    else:
        process_all = False

    OUT = []
    for data in datas:
        if data.split("-->")[0] in selected_layer_keys or process_all:
            OUT.append(data)

    return OUT


def map_material():
    #EnneadTab.RHINO.RHINO_CLEANUP.purge_material()
    options = ["N3", "N4", "N5", "N6", "Plot Connection"]
    res = EnneadTab.RHINO.RHINO_FORMS.select_from_list(options,
                            title = "EnneadTab",
                            message = "Use which OST mapping?",
                            multi_select = False,
                            button_names = ["Run"])[0]

    file_path = r"I:\2135\0_BIM\10_BIM Management\10_BIM Resources\ost material mapping\ost material mapping_2135_BiliBili SH HQ_{}.txt".format(res)
    #print file_path
    datas = EnneadTab.DATA_FILE.read_txt_as_list(file_path)
    datas = select_key_layer(datas)

    #sample_balls = []
    for data in datas:
        layer_name, revit_material_name, rhino_material_name = data.split("-->")
        #print "################"
        #print layer_name
        #print rhino_material_name

        if "glass" in rhino_material_name.lower():
            r, g, b, t, R = 137, 190, 220, 1, 255
        else:
            r, g, b, t, R = 200, 200, 200, 0, 0
        RGBAR = (r,g,b,t,R)
        existing_material = EnneadTab.RHINO.RHINO_MATERIAL.get_material_by_name(rhino_material_name)
        if existing_material is not None:
            mat_index = existing_material.MaterialIndex
            sample_ball = None
        else:
            mat_index, sample_ball = EnneadTab.RHINO.RHINO_MATERIAL.create_material(rhino_material_name, RGBAR, return_index = True)
        #print "*******"
        #print "new material created"
        temp_key = "STOP DEBUG_Railing Panel_Mullion Silicon"
        if temp_key.lower() in layer_name.lower():
            print("------")
            print("keyword = {}".format(layer_name))
            print("rhino material name = {}".format(rhino_material_name))
            print("did it create new material = {}".format(sample_ball is not None))
            print("material index = {}".format(mat_index))
        for layer in get_OST_layers(layer_name):
            current_res = rs.LayerMaterialIndex(layer)
            res = rs.LayerMaterialIndex(layer, mat_index)
            #sc.doc.Views.Redraw()
            #getlayer(layer, True).RenderMaterialIndex = mat_index
            after_res = rs.LayerMaterialIndex(layer)
            if temp_key.lower() in layer_name.lower():
                print("-assign to layer = {}".format(layer))
                print(current_res)
                print(res)
                print(after_res)
        if sample_ball is not None:
            pass
            rs.DeleteObject(sample_ball)


        #sample_balls.append(sample_ball)


    EnneadTab.RHINO.RHINO_CLEANUP.purge_material()
    return


def import_legend_material():
    return
    legend_file = r"C:\Users\szhang\Desktop\test Rhino material legend.3dm"

def get_OST_layers(OST):

    OST = OST.replace(".", "_")
    all_layer_names = rs.LayerNames()
    OUT = []
    for layer in all_layer_names:
        """
        note to self: here is a example of mistake, this version has issue thta cannot assign the actual layer becasue the checker layer name has been destroed in the split method.
        if "::" in layer:
            layer = layer.split("::")[-1]
        if OST in layer:
            OUT.append(layer)
        """
        if "::" in layer:
            layer_check = layer.split("::")[-1]
        else:
            layer_check = layer
        if OST in layer_check:
            OUT.append(layer)
    #print "&&&&&&"
    #print OUT
    return OUT

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    rs.EnableRedraw(False)
    import_legend_material()
    map_material()

######################  main code below   #########
if __name__ == "__main__":
    main()
