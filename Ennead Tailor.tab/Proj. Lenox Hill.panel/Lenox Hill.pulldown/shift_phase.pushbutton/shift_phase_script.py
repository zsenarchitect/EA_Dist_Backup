#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "shift the created phase from 7 to 6"
__title__ = "shift_phase"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def shift_phase():
    
    # get all elelemtn in projct,  get phase 6 and 7
    #  for everyting that created on phase 87 , change it to 6

    all_phases = list(doc.Phases)


    phase_6 = all_phases[-2]
    phase_7 = all_phases[-1]
    
    t = DB.Transaction(doc, __title__)
    t.Start()

    for view in DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements():
        if view.IsTemplate:
            continue
        for element in DB.FilteredElementCollector(doc, view.Id).ToElements():
            if not hasattr(element, "CreatedPhaseId"):
                continue

            if not doc.GetElement(element.CreatedPhaseId):
                continue
            if element.CreatedPhaseId == phase_7.Id:
                try:
                    element.CreatedPhaseId = phase_6.Id
                except:
                    # print (output.linkify(element.Id))
                    pass
            

    t.Commit()
    


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    shift_phase()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







