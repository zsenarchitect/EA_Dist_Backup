"""Pins all viewports on selected Titleblocks.

Shift-Click:
Pin all viewports on active sheet.
"""

__title__ = "Pin/Unpin\nTitleblocks"

from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms


def do_Titleblocks(sheet_list, pin_option):
    with revit.Transaction('Fix Titleblocks pins'):
        for sheet in sheet_list:


            if sheet.Pinned != pin_option:
                sheet.Pinned = pin_option




res = forms.alert(options = ["Pin Titleblocks", "Un-Pin Titleblocks"], msg = "I want to [.....]")

if "Un-Pin" in res:
    pin_option = False
elif "Pin" in res:
    pin_option = True
else:
    script.exit()


sel_Titleblocks = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()

if sel_Titleblocks:
    do_Titleblocks(sel_Titleblocks, pin_option)
