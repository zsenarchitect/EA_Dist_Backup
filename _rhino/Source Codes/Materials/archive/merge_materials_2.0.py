import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")

import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def merge_material():
    # rs.Command("_Purge Material=Yes")
    # return

    all_mats = sc.doc.Materials # this is also the mateial table object

    #why looks like this: delteed material are kept in the documents for the UNDO fuinction, so it need to check IsDeleted propety; default matreial from system do not have user assigned name so they are out;  if one materrial is being used on multiple layer they are considered unique mat with same name, so do set() to remove duplicated names
    all_mat_names = list(set([x.Name for x in all_mats if (x.Name != None and not x.IsDeleted)]))
    all_mat_names.sort()


    mats_to_modify = EnneadTab.RHINO.RHINO_FORMS.select_from_list(all_mat_names,
                                                                title = "EnneadTab",
                                                                message = "Select Materials to modify, hold 'shift' to select multiple.",
                                                                multi_select = True,
                                                                button_names = ["Select Multiple Materials"],
                                                                width = 500,
                                                                height = 500)

    mat_target = EnneadTab.RHINO.RHINO_FORMS.select_from_list(all_mat_names,
                                                            title = "EnneadTab",
                                                            message = "Select Single Target Material",
                                                            multi_select = False,
                                                            button_names = ["Select Single Material"],
                                                            width = 500,
                                                            height = 500)[0]


    if not mat_target or not mats_to_modify:
        rs.MessageBox(message = "Cannot handle empty selection. No action taken.", buttons= 0 | 48, title = "ohh..")
        return

    # print mats_to_modify
    # print mat_target
    # print_list(mats_to_modify)

    target_mat = get_material_by_name(mat_target)
    print(target_mat.Name)
    print(target_mat.MaterialIndex)
    mat_target_index = target_mat.MaterialIndex


    block_names = rs.BlockNames(sort = True)
    all_layers = rs.LayerNames()
    all_objs = rs.AllObjects()
    global LOG

    LOG = "##Looking for objs in block definition...\n"
    LOG_length_increase = len(LOG)
    map(lambda x: modify_block(x, mats_to_modify, mat_target_index), block_names)
    LOG_length_increase = len(LOG) - LOG_length_increase
    if LOG_length_increase == 0:
        LOG += "\t\tNothing found.."
    else:
        pass

    LOG += "\n\n##Looking for objs in general...\n"
    LOG_length_increase = len(LOG)

    map(lambda x: modify_obj_material(x, mats_to_modify, mat_target_index, block_name = None), all_objs)
    LOG_length_increase = len(LOG) - LOG_length_increase
    if LOG_length_increase == 0:
        LOG += "\t\tNothing found.."
    else:
        pass

    LOG += "\n\n##Looking for layer materials...\n"
    LOG_length_increase = len(LOG)
    map(lambda x: modify_layer_material(x, mats_to_modify, mat_target_index), all_layers)
    map(delete_material_by_name, mats_to_modify)
    LOG_length_increase = len(LOG) - LOG_length_increase
    if LOG_length_increase == 0:
        LOG += "\t\tNothing found.."
    else:
        pass


    rs.Command("_Purge _Pause _Materials=_Yes _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

    rs.TextOut(message = LOG + "\n\n################\nThe tool will do a material-only purge by the end automatically.", title = "Summery of layer material changes.")
    # rs.MessageBox(message = "For deep cleaning, run purge material by the end.", buttons= 0 | 48, title = "Works are not done yet...")

def get_material_by_name(name):
    material_index = sc.doc.Materials.Find(name, ignoreDeletedMaterials = True)
    return get_material_by_index(material_index)

    # abondone below script, need to ignore deleted materials
    all_mats = sc.doc.Materials
    for mat in all_mats:
        if name == mat.Name:
            return mat
    # print Rhino.DocObjects.Table.MaterialTable
    # return Rhino.DocObjects.MaterialTable.Find(name, True)

def get_material_by_index(index):
    all_mats = sc.doc.Materials
    for mat in all_mats:
        if index == mat.MaterialIndex:
            return mat

def delete_material_by_name(name):
    #index = get_material_by_name(name).MaterialIndex
    #sc.doc.Materials.DeleteAt( index)
    result = sc.doc.Materials.Delete( get_material_by_name(name))
    print("delete {} success? {}".format(name, result))

    #sc.doc.Materials.Clear()

def modify_layer_material(current_layer, mats_to_modify, mat_target_index):
    global LOG
    current_material_index_on_layer = rs.LayerMaterialIndex(current_layer)
    if current_material_index_on_layer == -1:
        return
    layer_mat = get_material_by_index(current_material_index_on_layer)
    if layer_mat.Name in mats_to_modify:
        rs.LayerMaterialIndex(current_layer, index = mat_target_index)
        LOG += "\t\t[{}]    layer material changed from [{}] --> [{}]\n".format(current_layer,
                                                                        layer_mat.Name,
                                                                        get_material_by_index(mat_target_index).Name)
        return


def modify_block(block_name, mats_to_modify, mat_target_index):
    global LOG
    # print block_name
    block_definition = sc.doc.InstanceDefinitions.Find(block_name)
    objs = block_definition.GetObjects()
    #geos = []
    #attrs = []
    for i , obj in enumerate(objs):
        modify_obj_material(obj, mats_to_modify, mat_target_index, block_name = block_name)



    return


def modify_obj_material(obj, mats_to_modify, mat_target_index, block_name):

    if rs.ObjectMaterialSource(obj) != 1:
        return

    current_material_index_on_obj = rs.ObjectMaterialIndex(obj)
    if current_material_index_on_obj == -1:
        return
    obj_mat = get_material_by_index(current_material_index_on_obj)

    if obj_mat.Name in mats_to_modify:
        global LOG
        rs.ObjectMaterialIndex(obj, material_index = mat_target_index)
        if block_name:
            LOG += "\t\t[{}]    block obj-based material changed from [{}] --> [{}]\n".format(block_name,
                                                                                            obj_mat.Name,
                                                                                            get_material_by_index(mat_target_index).Name)
        else:
            LOG += "\t\t[{}]    obj-based material changed from [{}] --> [{}]\n".format(obj,
                                                                                    obj_mat.Name,
                                                                                    get_material_by_index(mat_target_index).Name)

    return

def OLD_log_entry(obj, old_mat_name, new_mat_name):
    global LOG
    LOG += "\n[{}] obj-based material changed from [{}] --> [{}]".format(obj,
                                                                        old_mat_name,
                                                                        new_mat_name)


def print_list(list):
    temp = ""
    for x in list:
        temp += str(x) + "\n"
    rs.TextOut(message = temp)

##########################################################################

if( __name__ == "__main__" ):

  merge_material()
