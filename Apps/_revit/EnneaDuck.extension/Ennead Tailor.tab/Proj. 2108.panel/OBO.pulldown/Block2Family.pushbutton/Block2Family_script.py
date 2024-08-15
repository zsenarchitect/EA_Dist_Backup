#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "After getting all the block data from Rhino side, create/update family in Revit.If the edit is about moving/rotating in rhino, the revit side will remove old family instance and get a new one based on saved Rhino Id."
__title__ = "Block2Family"

import os
import math
import clr # pyright: ignore 
# from pyrevit import forms #
from pyrevit.revit import ErrorSwallower
from pyrevit import script #

from EnneadTab import ERROR_HANDLE, FOLDER, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_UNIT
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import ApplicationServices # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()



KEY_PREFIX = "BLOCKS2FAMILY"


@ERROR_HANDLE.try_catch_error()
def Block2Family():
    print ("Move to main")

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    Block2Family()
    







