#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Jump to the ecosystem folder where you can inspect all the magic."
__title__ = "Open\nEcosystem Folder"
__context__ = "zero-doc"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()


import os
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_ecosystem_folder():
    os.startfile(ENVIRONMENT.ECO_SYS_FOLDER)




################## main code below #####################
if __name__ == "__main__":
    open_ecosystem_folder()







