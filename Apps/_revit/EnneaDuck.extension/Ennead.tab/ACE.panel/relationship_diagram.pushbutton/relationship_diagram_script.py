#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Interactive convas to draw relationship diagram."
__title__ = "Relationship Diagram"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def relationship_diagram(doc):


    EXE.try_open_app("RelationshipTree")


################## main code below #####################
if __name__ == "__main__":
    relationship_diagram(DOC)







