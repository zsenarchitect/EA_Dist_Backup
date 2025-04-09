#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Temp"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def temp(doc):
    pass


################## main code below #####################
if __name__ == "__main__":
    temp(DOC)







