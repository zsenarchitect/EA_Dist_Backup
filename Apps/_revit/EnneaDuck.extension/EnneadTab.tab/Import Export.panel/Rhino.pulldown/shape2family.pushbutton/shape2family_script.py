#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "This is to handle all the incoming geometry made from Rhino's shape2revit command."
__title__ = "Shape2Family"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

import os
import sys

# Add the block2family.button directory to sys.path
current_dir = os.path.dirname(__file__)
block2family_dir = os.path.abspath(os.path.join(current_dir, '..', 'block2family.pushbutton'))
if block2family_dir not in sys.path:
    sys.path.insert(0, block2family_dir)
import block2family_script as B2F

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def shape2family(doc):
    B2F.block2family(always_standing=True)





################## main code below #####################
if __name__ == "__main__":
    shape2family(DOC)







