
from Autodesk.Revit import DB 
from pyrevit import forms
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def enable_workshare(doc, is_cloud):
    if is_cloud:
        enable_cloud_worksharing(doc)
    else:
        enable_server_worksharing(doc)


@EnneadTab.ERROR_HANDLE.try_catch_error
def enable_server_worksharing(doc):
    if doc.IsWorkshared:
        
        EnneadTab.NOTIFICATION.messenger (main_text =  "Model is already workshared.")
        return
    
    try:
        doc.EnableWorksharing ('0_Shared Levels & Grids', "Everything Else")
        EnneadTab.NOTIFICATION.messenger (main_text =  "Model is now workshared on Server.")
    except Exception as e:
        EnneadTab.NOTIFICATION.messenger (main_text =  str(e))
        return


@EnneadTab.ERROR_HANDLE.try_catch_error
def enable_cloud_worksharing(doc):


    try:
        doc.EnableCloudWorksharing ()
        EnneadTab.NOTIFICATION.messenger (main_text =  "Model is now workshared on Cloud.")
    except Exception as e:
        EnneadTab.NOTIFICATION.messenger (main_text =  str(e))
        return



if __name__== "__main__":
    pass