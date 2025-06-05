#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Emergency code fix tool for remote debugging and editing using VS Code Dev"
__title__ = "Remote Fix Code"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, CODE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def remote_fix_code(doc):
    """Launch emergency code fix interface for remote debugging."""
    # No transaction needed for this operation
    CODE.emergency_fix_code()



################## main code below #####################
if __name__ == "__main__":
    remote_fix_code(DOC)







