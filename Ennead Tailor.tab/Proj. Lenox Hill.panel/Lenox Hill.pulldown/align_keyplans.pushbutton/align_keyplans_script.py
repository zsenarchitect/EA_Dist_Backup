#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Align all keyplan to one source location viewpotty."
__title__ = "Align Key Plams"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SHEET, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


REF_VIEW = "PS 1_A115_1_L14 LACHMAN PENT ROOF"


@ERROR_HANDLE.try_catch_error
def align_key_plans():

    t = DB.Transaction(doc, __title__)
    t.Start()
    

    WORK_SHEET = REVIT_SHEET.get_sheet_by_sheet_num("PS 1_A115")



    # get the first first viewport as all data source
    for viewport_id in WORK_SHEET.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        if view.Name == REF_VIEW:
            position = viewport.GetBoxCenter()
            break



    all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).ToElements()
        
    for i, sheet in enumerate(all_sheets):
        
        for j, viewport_id in enumerate(sheet.GetAllViewports()):
            viewport = doc.GetElement(viewport_id)
            view = doc.GetElement(viewport.ViewId)

            if view.Scale == 1200:
                viewport.ViewportPositioning = DB.ViewportPositioning.ViewOrigin
                viewport.SetBoxCenter(position)

    t.Commit()

    NOTIFICATION.messenger("Finished")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    align_key_plans()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







