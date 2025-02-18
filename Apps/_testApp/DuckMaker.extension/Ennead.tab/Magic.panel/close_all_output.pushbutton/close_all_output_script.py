#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Close every output window."
__title__ = "Close All\nOutput"
__context__ = "zero-doc"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()
from pyrevit import script # pyright: ignore


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def close_all_output():
    output = script.get_output()
    output.close_others(True)


    # t = DB.Transaction(DOC, __title__)
    # t.Start()
    # pass
    # t.Commit()



################## main code below #####################
if __name__ == "__main__":
    close_all_output()







