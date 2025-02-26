__title__ = "RandomDeselect"
__doc__ = """Randomly deselects objects based on percentage.

Features:
- Deselects random subset of selected objects
- Percentage-based deselection (1-99%)
- Remembers last used percentage
- Maintains object relationships

Usage:
1. Select objects
2. Enter deselection percentage
3. Random subset will be deselected"""
__is_popular__ = True

import random
import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def random_deselect_left():
    ids = rs.SelectedObjects(False, False)
    if not ids: 
        NOTIFICATION.messenger  ("No objects selected, action cancelled.")
        return
    
    if len(ids) == 1: 
        NOTIFICATION.messenger  ("Only one object selected, action cancelled.")
        return
    
    percent = -1

    percent_default = DATA_FILE.get_sticky("RandomUnselectPercent", 50)

    while percent < 1 or percent > 99:
        input = rs.StringBox(message = "what percentage to de-select (1~99%)", 
                                        default_value = str(percent_default), 
                                        title = "random de-select")
        if not input:
            NOTIFICATION.messenger  ("No input, action cancelled.")
            return
        
        try:
            percent = int(input)
        except Exception as e:
            print (e)
            NOTIFICATION.messenger  ("Try another valid input number.")
            
    if not percent: return
    NOTIFICATION.messenger  ("{}% deslected.".format(percent))
    
    if not percent: return

    
    objs = random.sample(ids, int(percent*len(ids)/100))
    
    rs.UnselectObjects(objs)
    
    DATA_FILE.set_sticky("RandomUnselectPercent", percent)
    
if __name__ == "__main__":
    random_deselect_left()
