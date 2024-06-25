import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

"""
### TO-DO:
- Main task
    - Sub-task
#### Assigned to: **{}**
"""

@EnneadTab.ERROR_HANDLE.try_catch_error
def run():
    rs.EnableRedraw(False)
    


######################  main code below   #########
if __name__ == "__main__":

    run()




