#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "List all ForgeId for units"
__title__ = "List All Unit Ids"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def list_all_unit_ids():

    REVIT_UNIT.list_all_unit_ids()
    print ("\n"*10)
    REVIT_UNIT.list_all_unit_specs()


################## main code below #####################
if __name__ == "__main__":
    list_all_unit_ids()







