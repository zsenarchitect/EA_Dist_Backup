#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Show warnings in the active view."
__title__ = "Toggle\nWarnings"

from pyrevit.userconfig import user_config
from pyrevit import script
from pyrevit.coreutils.ribbon import ICON_LARGE


import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
from System import EventHandler, Uri # pyright: ignore
from Autodesk.Revit.UI.Events import ViewActivatedEventArgs # pyright: ignore


# icon_on_path = script.get_bundle_file('on.png')
# icon_off_path = script.get_bundle_file('off.png')
KEY_NAME = "WARNING_MODE"

def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    button_icon = script_cmp.get_bundle_file('off.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_LARGE)
    script.set_envvar(KEY_NAME, False)
    return True


@ERROR_HANDLE.try_catch_error_silently
def show_warnings(sender, args):
    active_view = args.CurrentActiveView
    doc = args.Document

    # redo inmport becasue the isolated func need structure.....
    from EnneadTab import NOTIFICATION
    from EnneadTab.REVIT import REVIT_VIEW
    from Autodesk.Revit import DB # pyright: ignore 


    all_warnings = doc.GetWarnings()
    all_view_element_ids = DB.FilteredElementCollector(doc, active_view.Id).ToElementIds()

    bad_element_ids = set()
    for warning in all_warnings:
        bad_element_ids.add( warning.GetFailingElements())
    in_view_bad_element_ids = bad_element_ids.intersection(all_view_element_ids)

    if not in_view_bad_element_ids:
        return
    for element_id in in_view_bad_element_ids:
        element = doc.GetElement(element_id)
        print (element)
    # REVIT_VIEW.show_in_convas_graphic(DB.XYZ(400,150,0), additional_info={"description":"Hello"})


    
    # if active view is a sheet view, show warning for all placed view
    

@ERROR_HANDLE.try_catch_error
def toggle_warning_mode():
    new_state = not script.get_envvar(KEY_NAME)
    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
    if new_state:
        __revit__.ViewActivated += EventHandler[ViewActivatedEventArgs](show_warnings) # pyright: ignore
        NOTIFICATION.messenger("Warning mode activated!")
    else:
        __revit__.ViewActivated -= EventHandler[ViewActivatedEventArgs](show_warnings) # pyright: ignore
        NOTIFICATION.messenger("Warning mode De-activated!")

    script.set_envvar(KEY_NAME, new_state)
    script.toggle_icon(new_state)




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    toggle_warning_mode()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







