#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "test_temp_graphic"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
import os
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def test_temp_graphic():
    manager = DB.TemporaryGraphicsManager  .GetTemporaryGraphicsManager(doc)
    manager.Clear()

    path = "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\images\\surprised_face.bmp"
    if os.path.exists(path):
        pass
        data = DB.InCanvasControlData (path, DB.XYZ(0,0,0))
        manager.AddControl(data, doc.ActiveView.Id)

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    test_temp_graphic()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







