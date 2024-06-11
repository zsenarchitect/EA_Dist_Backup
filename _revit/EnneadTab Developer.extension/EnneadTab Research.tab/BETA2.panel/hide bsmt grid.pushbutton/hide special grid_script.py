"""plot 9 only
hide basement grid on views
"""

__title__ = "hide special grids"

from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
import System

def do_grids(sheet_list, hide_option, keyword):
    with revit.Transaction('hide special_grid'):
        for sheet in sheet_list:

            for viewid in sheet.GetAllPlacedViews():

                grids = DB.FilteredElementCollector(revit.doc, viewid).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
                special_grid = filter(lambda x: x.LookupParameter("MC_$BuildingID").AsString() == keyword, grids)
                if len(special_grid) == 0:
                    continue
                else:
                    for x in special_grid:
                        print("Found {} in view '{}'".format(x.Name, revit.doc.GetElement(viewid).Name ))
                special_grid_format = System.Collections.Generic.List[DB.ElementId]([x.Id for x in special_grid])
                revit.doc.GetElement(viewid).HideElements(special_grid_format)





res = forms.alert(options = ["Hide", "Show"], msg = "I want to [.....] special grids.")

if "Hide" in res:
    hide_option = True
elif "Show" in res:
    hide_option = False
else:
    script.exit()


if __shiftclick__:
    if isinstance(revit.active_view, DB.ViewSheet):
        sel_sheets = [revit.active_view]
    else:
        forms.alert('Active view must be a sheet.')
        script.exit()
else:
    sel_sheets = forms.select_sheets(title='Select Sheets', use_selection=True)

keyword = "BASEMENT"
if sel_sheets:
    do_grids(sel_sheets, hide_option, keyword)
