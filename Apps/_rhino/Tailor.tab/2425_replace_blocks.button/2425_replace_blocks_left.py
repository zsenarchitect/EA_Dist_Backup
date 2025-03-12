
__title__ = "2425ReplaceBlocks"
__doc__ = "This button does 2425ReplaceBlocks when left click"

import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG, EXCEL
from EnneadTab.RHINO import RHINO_BLOCK
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def replace_blocks():
    options = ["Twinmotion block --> Enscape block",
               "Enscape block --> Twinmotion block"]
    res = rs.ListBox(options, "How to handle block replacement?", "Select option")
    if res == options[0]:
        normal_direction = False
    elif res == options[1]:
        normal_direction = True
    else:
        return
        
    data = EXCEL.read_data_from_excel("J:\\2425\\0_3D\\03_Enscape\\enscape_twinmotion_block_mapping.xlsx",
                                            return_dict=False,
                                            worksheet="EnneadTab Helper")
    data = data[1:]
    for row in data:
        if normal_direction:
            old_block = row[0].get("value") # getting enscape block
            new_block = row[1].get("value") # getting twinmotion block
        else:
            old_block = row[1].get("value") # getting twinmotion block
            new_block = row[0].get("value") # getting enscape block
        RHINO_BLOCK.replace_block(old_block, new_block)
    rs.Redraw()
    
if __name__ == "__main__":
    replace_blocks()
