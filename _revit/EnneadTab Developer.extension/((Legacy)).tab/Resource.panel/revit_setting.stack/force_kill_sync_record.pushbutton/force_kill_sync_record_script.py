#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Force remove selected record from the LAST SYNC MONITOR window."
__title__ = "Force Kill\nLast Sync Record"
__context__ = "zero-doc"
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore


def force_kill_sync_record():
    import imp
    full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\LAST_SYNC_MONITOR.pushbutton\update_last_sync_datafile_script.py'
    if not EnneadTab.USER.is_SZ():
        full_file_path = EnneadTab.FOLDER.remap_filepath_to_folder(full_file_path)
    ref_module = imp.load_source("update_last_sync_datafile_script", full_file_path)

    ref_module.kill_record()

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
"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    force_kill_sync_record()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
