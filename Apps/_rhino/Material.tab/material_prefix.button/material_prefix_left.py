__title__ = "MaterialPrefix"
__doc__ = """Add file-specific prefixes to materials.

Key Features:
- Automatic prefix generation
- Session compatibility
- Name conflict resolution
- Batch processing
- Material tracking"""

import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def material_prefix():
    mats = sc.doc.Materials
    mat_names = []
    try:    
        doc_name = sc.doc.Name.split(".3dm")[0]
    except:
        doc_name = "Untitled"
    print (doc_name)
    print (mats)
    print ("*******")
    for mat in mats:
        try:
            if mat.Name not in mat_names:
                if doc_name in mat.Name:
                    continue
                old_name =  mat.Name
                mat.Name = doc_name + "_" + old_name
                print ("{} --> {}".format(old_name, mat.Name))
                mat.CommitChanges()
                mat_names.append(mat.Name)
        except:
            continue


if __name__ == "__main__":
    material_prefix()