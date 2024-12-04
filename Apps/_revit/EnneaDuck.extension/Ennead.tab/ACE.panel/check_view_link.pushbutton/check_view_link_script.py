#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Check all the linked_views in the project"
__title__ = "Check Linked-View\nRelationship"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 


import traceback

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def check_view_link(doc):
    REVIT_VIEW.check_linked_views(doc)


################## main code below #####################
if __name__ == "__main__":
    from pyrevit import script
    output = script.get_output()
    try:
        check_view_link(DOC)
    except Exception as e:
        print (traceback.format_exc())







