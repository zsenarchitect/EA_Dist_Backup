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
def time_sheet_show_record():
    EnneadTab.LOG.print_time_sheet_detail()
    


######################  main code below   #########
if __name__ == "__main__":

    time_sheet_show_record()




