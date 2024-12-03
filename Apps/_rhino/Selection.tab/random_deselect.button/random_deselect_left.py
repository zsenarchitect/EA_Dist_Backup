
__title__ = "RandomDeselect"
__doc__ = "This button does RandomDeselect when left click"


import random
import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def random_deselect():
    ids = rs.SelectedObjects(False, False)
    if not ids: return
    
    if len(ids) == 1: return 
    
    percent = -1

    percent_default = DATA_FILE.get_sticky("RandomUnselectPercent", 50)

    while percent < 1 or percent > 99:
        percent = int(rs.StringBox(message = "what percentage to de-select (1~99%)", 
                                    default_value = str(percent_default), 
                                    title = "random de-select"))
        
    
    if not percent: return

    
    objs = random.sample(ids, int(percent*len(ids)/100))
    
    rs.UnselectObjects(objs)
    
    DATA_FILE.set_sticky("RandomUnselectPercent", percent)
    
if __name__ == "__main__":
    random_deselect()
