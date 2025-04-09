#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Powerful batch cutting utility that streamlines the process of creating multiple void cuts in curtain panels. Select curtain walls or individual panels and apply the same void geometry to all elements simultaneously. Perfect for creating consistent openings across curtain systems without tedious individual operations."
__title__ = "Batch Cut\nElements"
__is_popular__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()


from EnneadTab import ENVIRONMENT, ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_SYNC
from Autodesk.Revit import DB, UI # pyright: ignore 
from pyrevit import forms, script
import clr # pyright: ignore 
from pyrevit import forms
from pyrevit.revit import ErrorSwallower

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_cut():
    opts = ["Get CW panels by selection walls",
            "Use selected floors or CW panels"]
    res = forms.SelectFromList.show(opts, multiselect=False, title = "How do you want to collect CW panels")
    if not res:
        return


    if res == opts[0]:
        # get the wall
        walls = UIDOC.Selection.PickObjects(UI.Selection.ObjectType.Element, "Pick curtainwalls with panels to cut")
        walls = [DOC.GetElement(x) for x in walls]
        walls = filter(lambda x: isinstance(x, DB.Wall), walls)
        if len(walls) == 0:
            NOTIFICATION.messenger("No wall selected")
            return
        all_panels = []
        for wall in walls:
            all_panels.extend( [DOC.GetElement(x) for x in wall.CurtainGrid.GetPanelIds()])
    if res == opts[1]:
        all_panels = REVIT_SELECTION.get_selection(UIDOC)

    if len(all_panels) == 0:
        NOTIFICATION.messenger("No elements found")
        return



    masses = DB.FilteredElementCollector(DOC).OfCategory(DB.BuiltInCategory.OST_Mass).WhereElementIsNotElementType().ToElements()
    masses = filter(lambda x: x.Symbol.LookupParameter("Description").AsString() == "{} void".format(ENVIRONMENT.PLUGIN_NAME), list(masses))
    if len(masses) == 0:
        NOTIFICATION.messenger("No voids selected, please check description used. I expect it to be [{}] to be considered as a void".format("{} void".format(ENVIRONMENT.PLUGIN_NAME)))
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

    

    is_sync_and_close = REVIT_SYNC.do_you_want_to_sync_and_close_after_done()


    t = DB.Transaction(DOC, __title__)
    t.Start()
    with ErrorSwallower() as ES:
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

    if is_sync_and_close:
        REVIT_SYNC.sync_and_close()




################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    batch_cut()







