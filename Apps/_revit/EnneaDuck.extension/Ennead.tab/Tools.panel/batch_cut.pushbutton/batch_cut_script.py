#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Good for batch cutting many curtain panels at once with same void."
__title__ = "Batch Cut Panels"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB, UI # pyright: ignore 
from pyrevit import forms, script
import clr


UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_cut():
    # get the wall
    walls = UIDOC.Selection.PickObjects(UI.Selection.ObjectType.Element, "Pick walls with panels to cut")
    walls = [DOC.GetElement(x) for x in walls]
    walls = filter(lambda x: isinstance(x, DB.Wall), walls)
    if len(walls) == 0:
        NOTIFICATION.messenger("No wall selected")
        return


    masses = DB.FilteredElementCollector(DOC).OfCategory(DB.BuiltInCategory.OST_Mass).WhereElementIsNotElementType().ToElements()
    masses = filter(lambda x: x.Symbol.LookupParameter("Description").AsString() == "enneadtab void", list(masses))
    if len(masses) == 0:
        NOTIFICATION.messenger("No voids selected, please check description used.")
        return


    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.Symbol.Family.Name)
    masses = [MyOption(x) for x in masses]
    select_void = forms.SelectFromList.show(masses, multiselect=False, title="Select voids to cut")

    if select_void is None:
        NOTIFICATION.messenger("No void selected")
        return

    




    t = DB.Transaction(DOC, __title__)
    t.Start()
    for wall in walls:
        all_panels = [DOC.GetElement(x) for x in wall.CurtainGrid.GetPanelIds()]
        for panel in all_panels:

            # reason = clr.StrongBox[DB.CutFailureReason](DB.CutFailureReason.CutAllowed)
            # DB.SolidSolidCutUtils.CanElementCutElement (panel, select_void, reason)
            # if reason != DB.CutFailureReason.CutAllowed:
                
            #     print (reason)
            #     continue
            try:
                DB.SolidSolidCutUtils.AddCutBetweenSolids(DOC, panel, select_void)
            except Exception as e:
                print ("Failed to cut panel: {}: {}".format(output.linkify(panel.Id), e))
            
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    batch_cut()







