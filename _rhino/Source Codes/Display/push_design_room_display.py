import rhinoscriptsyntax as rs
import scriptcontext as sc
import design_room as DR

import sys
sys.path.append("..\lib")
from EnneadTab.ENVIRONMENT import get_EnneadTab_For_Rhino_root
sys.path.append(r'{}\Source Codes\lib'.format(get_EnneadTab_For_Rhino_root()))
import EnneadTab

"""
### TO-DO:
- Right click to set desiged GFA for each layer name
  - Save to external text
  - Live compare how much is off from target
#### Assigned to: **{}**
"""

#@EnneadTab.ERROR_HANDLE.try_catch_error
def push_design_room_display():
    key = DR.IS_UPDATE_KEY
    sc.sticky[key] = True

    conduit = sc.sticky[DR.KEY]
    conduit.sync()

if __name__=="__main__":
    #showinscript()
    #showafterscript()
    push_design_room_display()
    #testing()
