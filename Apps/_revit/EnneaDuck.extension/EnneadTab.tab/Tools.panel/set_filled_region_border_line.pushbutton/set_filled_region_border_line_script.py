#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Specialized filled region styling tool that allows precise control over border line appearance. Quickly apply consistent line styles to multiple filled regions simultaneously, enhancing drawing clarity and graphical standards. Works with individual selections even when regions are nested within groups by using tab-selection technique."
__title__ = "Set FilledRegion\nBorder Style"


from pyrevit import script # pyright: ignore
from pyrevit.revit import ErrorSwallower # pyright: ignore

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_SELECTION
from EnneadTab import ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument # pyright: ignore




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def set_filled_region_border_line():
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    selection = filter(lambda x: type(x) == DB.FilledRegion, selection)

    if len(selection) == 0:
        print ("There is not any FilledRegion in the selection")
        return
    


    line_style = REVIT_SELECTION.pick_linestyle(doc, filledregion_friendly = True)
    if not line_style:
        print ("There is no line style selected")
        return
    


    t = DB.Transaction(doc, __title__)
    t.Start()
    with ErrorSwallower() as swallower:
        for filled_region in selection:
            filled_region.SetLineStyleId(line_style.Id)

    t.Commit()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    set_filled_region_border_line()
    











