import sys
sys.path.append("..\lib")
import EnneadTab
import scriptcontext as sc
import rhinoscriptsyntax as rs



@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    doc_name = sc.doc.Name.split(".3dm")[0]

    search_text = rs.GetString("string to search to remove, type your string or enter to use current file name", defaultString = doc_name + "_")
    #search_text = "2C - Bilibili_Isolated N6 Village_"

    mats = sc.doc.Materials
    mat_names = []

    print(mats)
    print("*******")
    for mat in mats:
        try:
            if search_text in mat.Name:
                old_name = mat.Name
                mat.Name = mat.Name.split(search_text)[1]
                print("{} --> {}".format(old_name, mat.Name))
                mat.CommitChanges()
                #mat_names.append(mat.Name)
        except:
            continue
        
##################################
if __name__ == "__main__":
    main()