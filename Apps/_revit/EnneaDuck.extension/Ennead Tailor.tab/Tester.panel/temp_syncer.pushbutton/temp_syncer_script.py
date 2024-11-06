#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Temp Syncer"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

import time

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SYNC
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


# @LOG.log(__file__, __title__)
# @ERROR_HANDLE.try_catch_error()
def temp_syncer():
    REVIT_SYNC.update_last_sync_data_file(DOC)
    REVIT_SYNC.start_monitor()
################## main code below #####################
if __name__ == "__main__":
    temp_syncer()







