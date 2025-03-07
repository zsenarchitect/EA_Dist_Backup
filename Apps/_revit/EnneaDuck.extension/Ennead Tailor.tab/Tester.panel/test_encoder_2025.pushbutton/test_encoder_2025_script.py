#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Encoder 2025"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

import os
import os.path as op
import shutil
import math
from collections import defaultdict
from natsort import natsorted

from pyrevit import HOST_APP
from pyrevit import framework
from pyrevit.framework import System
from pyrevit import coreutils
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import script

from pyrevit.runtime.types import DocumentEventUtils

from pyrevit.interop import adc

import keynotesdb as kdb

HELP_URL = "https://www.notion.so/pyrevitlabs/Manage-Keynotes-6f083d6f66fe43d68dc5d5407c8e19da"

logger = script.get_logger()
output = script.get_output()
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def test_encoder_2025(doc):


    t = DB.Transaction(doc, __title__)
    t.Start()
    pass
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    test_encoder_2025(DOC)







