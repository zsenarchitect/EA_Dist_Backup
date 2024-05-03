#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Utility module for edit request monitor."
__title__ = "Urge Request"

# from pyrevit import forms #
try:
    from pyrevit import script #
    # from pyrevit import revit #
    import EA_UTILITY
    import EnneadTab
    import ENNEAD_LOG
    from Autodesk.Revit import DB 
    # from Autodesk.Revit import UI
    doc = __revit__.ActiveUIDocument.Document
except:
    #print "cannot import base module for Urgent Request main script"
    pass

@EnneadTab.ERROR_HANDLE.try_catch_error
def remover_repeating_item_in_list(collection):
    out = []
    for item in collection:
        if item not in out:
            out.append()


@EnneadTab.ERROR_HANDLE.try_catch_error
def urge_request():

    # after view actived

    for doc in EA_UTILITY.get_top_revit_docs():
        requester = set()
        elements = DB.FilteredElementCollector(doc).ToElements()
        for element in elements:
            info = DB.WorksharingUtils .GetWorksharingTooltipInfo (doc, element.Id)
            requester.update(info.GetRequesters ())
        requester = list(requester)

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
@EnneadTab.ERROR_HANDLE.try_catch_error
def run_exe():

    #exe_location = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Project Settings\Exe\LAST_SYNC_MONITOR\LAST_SYNC_MONITOR.exe - Shortcut"
    #exe_location = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Project Settings\Exe\SEARCH_EDIT_REQUEST\SEARCH_EDIT_REQUEST.exe - Shortcut"
    exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\SEARCH_EDIT_REQUEST\SEARCH_EDIT_REQUEST.exe - Shortcut"
    exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\temp_exe_to_be_merged_2\SEARCH_EDIT_REQUEST\SEARCH_EDIT_REQUEST.exe - Shortcut"


    """
    if not EA_UTILITY.is_SZ(additional_tester_ID = ["paula.gronda"]):
        return
    """
    try:
        EA_UTILITY.open_file_in_default_application(exe_location)
        return
    except Exception as e:
        EA_UTILITY.print_note(e.message)

    try:
        EA_UTILITY.open_file_in_default_application(exe_location.replace(" - Shortcut", ""))
        return
    except Exception as e:
        EA_UTILITY.print_note(e.message)



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    run_exe()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
