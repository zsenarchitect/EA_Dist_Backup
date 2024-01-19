
from pyrevit import  EXEC_PARAMS

import EnneadTab
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 



@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    # ethan say he has learned his lesson. OK, diabling...
    return

    if doc.IsFamilyDocument:
        return
    if EnneadTab.USER.get_user_name() not in [ "eshaw", "szhang"]:
        return
    
    EnneadTab.NOTIFICATION.duck_pop(main_text = "Only for Ethan tool:\nMind your align auto-lock status")
    # from Autodesk.Revit.DB import ParameterTypeId, BuiltInParameter
    # print ParameterTypeId.LockAlignmentUiToggle
    # print BuiltInParameter.LOCK_ALIGNMENT_UI_TOGGLE
    args.Cancel = False

                                        
############################

if __name__ == '__main__':
    main()