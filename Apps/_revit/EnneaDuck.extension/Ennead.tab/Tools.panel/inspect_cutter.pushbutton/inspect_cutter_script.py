#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Reset Join/Cut"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import script
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def inspect_cutter():
    selections = REVIT_SELECTION.get_selection()
    if len(selections) == 0:
        NOTIFICATION.messenger("Please select elements to reset join/cut")
        return
    t = DB.Transaction(DOC, __title__)
    t.Start()
    output = script.get_output()
    for selection in selections:
        cutter_ids = DB.SolidSolidCutUtils.GetCuttingSolids(selection)
        for cutter_id in cutter_ids:
            cutter = DOC.GetElement(cutter_id)
            print ("Removing Cutter: ", output.linkify(cutter_id))
            DB.SolidSolidCutUtils.RemoveCutBetweenSolids(DOC, selection, cutter )
        joined_ids = DB.JoinGeometryUtils.GetJoinedElements(DOC, selection)
        for joined_id in joined_ids:
            joined = DOC.GetElement(joined_id)
            print ("Removing Joined: ", output.linkify(joined_id))
            DB.JoinGeometryUtils.UnjoinGeometry(DOC, selection, joined)
            
    t.Commit()

    # t = DB.Transaction(doc, __title__)
    # t.Start()
    # pass
    # t.Commit()



################## main code below #####################
if __name__ == "__main__":
    inspect_cutter()







