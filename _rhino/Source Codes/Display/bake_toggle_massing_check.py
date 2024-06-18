import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)



class DataItem():
    def __init__(self, item, row, column):
        self.item = item
        self.row = row
        self.column = column

def bake_action(data):
    filename = "EnneadTab GFA Schedule"
    if sc.doc.Name is not None:
        filename = "{}_EnneadTab GFA Schedule".format(sc.doc.Name.replace(".3dm", ""))


    filepath = rs.SaveFileName(title = "Where to save the Excel?", filter = "Excel Files (*.xlsx)|*.xlsx||", filename = filename)
    if filepath is None:
        return
    EnneadTab.EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab GFA")


@EnneadTab.ERROR_HANDLE.try_catch_error
def bake_toggle_massing_check():


    """
    key = "EA_GFA_EXCEL_PATH"
    sc.sticky[key] = filepath
    """

    items  = [("Export Current GFA Numbers To Excel.", True),
             ("Bake Current GFA Calc Surfaces.", False)   ]
    results  = rs.CheckListBox(items, "What do you want to do?", "Bake GFA Massing Data")
    if not results:
        return

    

    key = "EA_GFA_IS_BAKING_EXCEL"
    sc.sticky[key] = results[0][1]

    key = "EA_GFA_IS_BAKING_CRV"
    sc.sticky[key] = results[1][1]
    
    EnneadTab.NOTIFICATION.messenger(main_text = "Shake your Rhino viewport camera to trigger baking.")

######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    bake_toggle_massing_check()


