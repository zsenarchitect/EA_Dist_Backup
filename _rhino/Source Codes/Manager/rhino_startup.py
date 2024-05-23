import rhinoscriptsyntax as rs
import sys
import os
import Rhino # pyright: ignore
import traceback

sys.path.append("..\lib")
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    add_timesheet_hook()
    
    if not EnneadTab.USER.is_SZ():
        return
    EnneadTab.RHINO.RHINO_RUI.update_my_rui()
    EnneadTab.RHINO.RHINO_RUI.publish_rui()
    EnneadTab.NOTIFICATION.messenger(main_text = "Startup Script Completed")

    
    
def record_time_sheet(sender, e):
    doc = e.Document
    if doc.Path:
        EnneadTab.LOG.update_time_sheet_rhino(doc.Path)
    if "1643.old" in doc.Path:
        EnneadTab.NOTIFICATION.duck_pop(main_text="STOP! DO NOT WORK IN OLD FOLDER")
        
def add_timesheet_hook(): 
    # first record current file
    doc_path = Rhino.RhinoDoc.ActiveDoc.Path
    if doc_path:
        EnneadTab.LOG.update_time_sheet_rhino(doc_path)
        
    # then add hook for future file in this session
    # add two event hook
    Rhino.RhinoDoc.BeginOpenDocument += record_time_sheet
    Rhino.RhinoDoc.CloseDocument += record_time_sheet

def copy_working_to_main():
    original = r"{}\Working\EnneadTab.rui".format(EnneadTab.ENVIRONMENT.WORKING_FOLDER_FOR_RHINO)
    target = r"{}\EnneadTab for Rhino\EnneadTab.rui".format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)

    #copy rui file from working folder to L drive
    EnneadTab.FOLDER.copy_file(original, target)
    
    
def purge_bad_rui_baks():
    folder = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadTab for Rhino"
    for file in os.listdir(folder):
        if not file.endswith(".rui"):
            os.remove(os.path.join(folder, file))

if __name__ == "__main__":
    main()