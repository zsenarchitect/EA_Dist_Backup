
__title__ = "2425ReplaceBlocks"
__doc__ = "This button does 2425ReplaceBlocks when left click"

import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG, EXCEL
from EnneadTab.RHINO import RHINO_BLOCK
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def replace_blocks():
    options = ["twinmotion block --> enscape block",
               "enscape block --> twinmotion block"]
    res = rs.ListBox(options, "How to handle block replacement?", "Select option")
    if res == options[0]:
        data = EXCEL.read_data_from_excel("J:\\2425\\0_3D\\03_Enscape\\enscape_twinmotion_block_mapping.xlsx",
                                            return_dict=False,
                                            worksheet="EnneadTab Helper")
    data = data[1:]
    for row in data:
        old_block = row[0].get("value")
        new_block = row[1].get("value")
        RHINO_BLOCK.replace_block(old_block, new_block)
    rs.Redraw()
    
if __name__ == "__main__":
    replace_blocks()
