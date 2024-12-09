
__title__ = "RemoveStringInMaterialName"
__doc__ = "Remove the specific string in material name. Handy if trying to remove file name prefix."

import scriptcontext as sc
import rhinoscriptsyntax as rs
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def remove_string_in_material_name():
    try:    
 
        doc_name = sc.doc.Name.split(".3dm")[0]
    except:

        doc_name = "Untitled"

    search_text = rs.StringBox("string to search to remove, type your string or enter to use current file name", 
                               default_value= doc_name + "_",
                               title = "I hate this name...")
 
    mats = sc.doc.Materials


    print(mats)
    print("*******")
    for mat in mats:
        try:
            if search_text in mat.Name:
                old_name = mat.Name
                mat.Name = mat.Name.split(search_text)[1]
                print("{} --> {}".format(old_name, mat.Name))
                mat.CommitChanges()

        except:
            continue


if __name__ == "__main__":
    remove_string_in_material_name()