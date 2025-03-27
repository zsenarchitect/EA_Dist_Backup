#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Show warnings in the active view."
__title__ = "Toggle\nWarnings"
__tip__ = True

from pyrevit import script
from pyrevit.coreutils.ribbon import ICON_LARGE

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, NOTIFICATION, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
from System import EventHandler # pyright: ignore
from Autodesk.Revit.UI.Events import ViewActivatedEventArgs # pyright: ignore


# icon_on_path = script.get_bundle_file('on.png')
# icon_off_path = script.get_bundle_file('off.png')
KEY_NAME = "WARNING_MODE"

def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    button_icon = script_cmp.get_bundle_file('off.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_LARGE)
    script.set_envvar(KEY_NAME, False)
    return True





@ERROR_HANDLE.try_catch_error(is_silent=True)
def show_warnings(sender, args):
    active_view = args.CurrentActiveView
    doc = args.Document
    from EnneadTab.REVIT import REVIT_VIEW
    REVIT_VIEW.show_warnings_in_view(active_view, doc)






@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def toggle_warning_mode():

    if doc.ActiveView.ViewType not in [DB.ViewType.AreaPlan, DB.ViewType.ThreeD, DB.ViewType.FloorPlan, DB.ViewType.Section, DB.ViewType.Elevation]:
        NOTIFICATION.messenger("Please toggle it in one of the following views:\nArea Plan, 3D, Floor Plan, Section, Elevation")
        return

    new_state = not script.get_envvar(KEY_NAME)

    if new_state:
        __revit__.ViewActivated += EventHandler[ViewActivatedEventArgs](show_warnings) # pyright: ignore
        NOTIFICATION.messenger("Warning mode activated!")
        REVIT_VIEW.show_warnings_in_view(doc.ActiveView, doc)
    else:
        __revit__.ViewActivated -= EventHandler[ViewActivatedEventArgs](show_warnings) # pyright: ignore
        NOTIFICATION.messenger("Warning mode De-activated!")
        manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(doc)
    
        manager.Clear()

    script.set_envvar(KEY_NAME, new_state)
    script.toggle_icon(new_state)




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    toggle_warning_mode()
    







