"""Pins all viewports on selected sheets.

Shift-Click:
Pin all viewports on active sheet.
"""

__title__ = "Pin/Unpin\nViewports"

from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms


def do_viewports(sheet_list, pin_option):
    with revit.Transaction('Fix viewports pins'):
        for sheet in sheet_list:
            count = 0
            already_fixed_count = 0
            for vportid in sheet.GetAllViewports():
                vport = revit.doc.GetElement(vportid)
                if vport.Pinned != pin_option:
                    vport.Pinned = pin_option
                    count += 1
                else:
                    already_fixed_count += 1

            action = "Pin" if pin_option else "Un-pin"
            action_2 = "Pinned" if pin_option else "Un-pinned"
            text = '{} {} viewports on sheet: {} - {}'.format(action, count,sheet.SheetNumber,sheet.Name)
            if already_fixed_count > 0:
                text += '\t({} viewports were already {})'.format(already_fixed_count,action_2)
            print(text)



res = forms.alert(options = ["Pin Viewports", "Un-Pin Viewports"], msg = "I want to [.....]")

if "Un-Pin" in res:
    pin_option = False
elif "Pin" in res:
    pin_option = True
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


if sel_sheets:
    do_viewports(sel_sheets, pin_option)
