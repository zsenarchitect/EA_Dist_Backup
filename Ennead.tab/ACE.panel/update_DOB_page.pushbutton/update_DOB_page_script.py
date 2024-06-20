#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Update DOB Page Number"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def update_DOB_page(doc, show_log = True):
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements()
    for sheet in all_sheets:
        if not sheet.LookupParameter("Sheet_$Issue_DOB"):
            if show_log:
                NOTIFICATION.messenger("Need proper parameter for your DOB marking. Ask Gayatri for detail.")
            return

        if not sheet.LookupParameter("Sheet No.") or not sheet.LookupParameter("Total Sheets"):
            NOTIFICATION.messenger("Need proper parameter for your DOB numbering. Ask Gayatri for detail.")
            return

    good_sheets = [s for s in all_sheets if s.LookupParameter("Sheet_$Issue_DOB").AsString() != ""]
    good_sheets.sort(key = lambda x: "{}_{}_{}".format(x.LookupParameter("Sheet_$Group").AsString(),
                                                       x.LookupParameter("Sheet_$Series").AsString(),
                                                       x.SheetNumber))

    t = DB.Transaction(doc, __title__)
    t.Start()
    for i, sheet in enumerate(good_sheets):
        sheet.LookupParameter("Sheet No.").Set(i+1)
        sheet.LookupParameter("Total Sheets").Set(len(good_sheets))
    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_DOB_page(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







