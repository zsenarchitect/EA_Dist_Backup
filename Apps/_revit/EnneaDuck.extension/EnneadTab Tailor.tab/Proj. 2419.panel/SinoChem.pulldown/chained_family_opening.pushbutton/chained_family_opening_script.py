#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Chained Family Opening"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, FOLDER, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
import os

DOC = REVIT_APPLICATION.get_doc()
uiapp = REVIT_APPLICATION.get_uiapp()
proj_folder = os.path.dirname(os.path.dirname(__file__))
chain_loading_script_folder = os.path.join(proj_folder, "chained_family_loading.pushbutton")
import sys
sys.path.append(chain_loading_script_folder)
from chained_family_loading_script import ORDER


FAMILY_LIST = set()
for item in ORDER:
    FAMILY_LIST.add(item[0])
    FAMILY_LIST.add(item[1])
FAMILY_LIST = list(FAMILY_LIST)
print (FAMILY_LIST)
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def chained_family_opening(doc):

    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    for family in all_families:
        if family.Name in FAMILY_LIST:
            family_doc = doc.EditFamily(family)
            save_path = FOLDER.get_local_dump_folder_file(family.Name + ".rfa")
            option = DB.SaveAsOptions()
            option.OverwriteExistingFile = True
            family_doc.SaveAs(save_path, option)
            NOTIFICATION.messenger ("opening family: {}".format(family.Name))
            chained_family_opening(family_doc)
            uiapp.OpenAndActivateDocument(save_path)
            



################## main code below #####################
if __name__ == "__main__":
    chained_family_opening(DOC)







