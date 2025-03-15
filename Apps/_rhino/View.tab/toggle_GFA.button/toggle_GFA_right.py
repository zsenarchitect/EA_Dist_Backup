
__title__ = "BakeGFADataToExcel"
__doc__ = """Export GFA (Gross Floor Area) data to Excel and manage area targets.

Features:
- Export area calculations to formatted Excel spreadsheet
- Generate checking surfaces for visual verification 
- Set and manage target areas for different GFA categories
- Compare actual vs target areas with variance analysis

Usage:
- Click to export current GFA data to Excel
- Right-click to access additional options:
  - Generate checking surfaces
  - Set target areas for GFA categories
  - Edit existing target values
"""



import Rhino # pyright: ignore
import rhinoscriptsyntax as rs # pyright: ignore
import scriptcontext as sc # pyright: ignore
from EnneadTab import ERROR_HANDLE, LOG, EXCEL, NOTIFICATION
from EnneadTab.RHINO import RHINO_PROJ_DATA



@ERROR_HANDLE.try_catch_error()
def bake_action(data):
    filename = "EnneadTab GFA Schedule"
    if sc.doc.Name is not None:
        filename = "{}_EnneadTab GFA Schedule".format(sc.doc.Name.replace(".3dm", ""))


    filepath = rs.SaveFileName(title = "Where to save the Excel?", filter = "Excel Files (*.xlsx)|*.xlsx||", filename = filename)
    if filepath is None:
        return
    EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab GFA")


def set_target_dict():
    data = RHINO_PROJ_DATA.get_enneadtab_data()
    gfa_dict = data.get(RHINO_PROJ_DATA.DocKeys.GFA_TARGET_DICT, {})

    while True:
        options = ["Add a new keyword", "Edit all existing keywords", "Delete a keyword", "Done"]
        result = rs.ListBox(options, "GFA Target Dictionary", "What do you want to do?")
        if result == "Done":
            break
        elif result == options[0]:
            keyword = rs.StringBox("Enter a new keyword:")
            if keyword:
                gfa_dict[keyword] = 0
        elif result == options[1]:
            sorted_keys = sorted(gfa_dict.keys())
            sorted_values = [str(gfa_dict[k]) for k in sorted_keys]
            updated_list = rs.PropertyListBox(sorted_keys, sorted_values, "Keywords and target area without unit.", "GFA Target Dictionary")
            if not updated_list:
                continue
            for k in sorted_keys:
                try:
                    gfa_dict[k] = float(updated_list[sorted_keys.index(k)])
                except:
                    print ("!!!!!!!!!!!!!!!!!! This value is not a number ....{}".format(sorted_values[sorted_keys.index(k)]))
                    gfa_dict[k] = 0
        elif result == options[2]:
            selected_keyword = rs.ListBox(sorted(gfa_dict.keys()), "Select a keyword to delete:", "GFA Target Dictionary")
            if selected_keyword:
                del gfa_dict[selected_keyword]


    data[RHINO_PROJ_DATA.DocKeys.GFA_TARGET_DICT] = gfa_dict
    RHINO_PROJ_DATA.set_enneadtab_data(data)
    return gfa_dict

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def toggle_GFA():
    
    """
    key = "EA_GFA_EXCEL_PATH"
    sc.sticky[key] = filepath
    """


    items  = [
        ("Export Current GFA Numbers To Excel.", True),
        ("Bake Current GFA Calc Surfaces.", False),
        ("Set Target Dict.", False)
        ]
    results  = rs.CheckListBox(items, "What do you want to do?", "Bake GFA Massing Data")
    if not results:
        return

    

    key = "EA_GFA_IS_BAKING_EXCEL"
    sc.sticky[key] = results[0][1]

    key = "EA_GFA_IS_BAKING_CRV"
    sc.sticky[key] = results[1][1]

    key = "EA_GFA_IS_SETTING_TARGET_DICT"
    sc.sticky[key] = results[2][1]


    
    NOTIFICATION.messenger(main_text = "Shake your Rhino viewport camera to trigger baking.")

    
if __name__ == "__main__":
    toggle_GFA()


