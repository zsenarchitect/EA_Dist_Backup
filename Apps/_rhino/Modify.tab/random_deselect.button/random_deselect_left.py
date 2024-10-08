
__title__ = "RandomDeselect"
__doc__ = "Ramdonly deselect objs by percentage"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import random


from EnneadTab import NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def random_deselect():
    ids = rs.GetObjects("pick objs",  preselect=True)
    if not ids: 
        NOTIFICATION.messenger ("Currently selecting no elements.")
        return
    
    if len(ids) == 1: 
        NOTIFICATION.messenger  ("Please select at least 2+ elements.")

        return 
    
    percent = -1

    if sc.sticky.has_key("RandomUnselect_percent"):
        percent_default = sc.sticky["RandomUnselect_percent"]
    else:
        percent_default = 50

    # percent = rs.GetInteger("Percent to deselect", percent_default, 1, 99)
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
    NOTIFICATION.messenger  ("{}\% deslected.".format(percent))
    
    objs = random.sample(ids, int(percent*len(ids)/100))
    
    rs.UnselectObjects(objs)
    
    sc.sticky["RandomUnselect_percent"] = percent



if __name__ == "__main__":
    random_deselect()