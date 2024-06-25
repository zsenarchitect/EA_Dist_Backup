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
def time_sheet_record_manually():
    rs.EnableRedraw(False)
    doc_name = rs.DocumentName()
    doc_path = rs.DocumentPath()
    if doc_path and doc_name:
        EnneadTab.LOG.update_time_sheet_rhino(doc_path + doc_name)
        EnneadTab.NOTIFICATION.messenger(main_text="Time Sheet Stampted!")
    


######################  main code below   #########
if __name__ == "__main__":

    time_sheet_record_manually()




