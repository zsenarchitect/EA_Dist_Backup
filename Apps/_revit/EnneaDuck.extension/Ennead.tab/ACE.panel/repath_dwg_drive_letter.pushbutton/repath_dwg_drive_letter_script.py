#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Repath Dwg\nDrive Letter"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

import os

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import forms


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def repath_dwg_drive_letter(doc):


    dwg_type_list = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType ).ToElements()

    old_drive_letter = forms.ask_for_string(prompt="Enter the old drive letter (e.g., 'J') to fix",
                                            default="J")

    new_drive_letter = forms.ask_for_string(prompt="Enter the new drive letter (e.g., 'X') to assign",
                                            default="X")
    
    t = DB.Transaction(doc, "Repath All Linked Dwgs")
    t.Start()
    changed_count = 0
    for dwg_type in dwg_type_list:
        try:
            file_ref = dwg_type.GetExternalFileReference ()
            file_path = file_ref.GetPath()

            file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(file_path)
            current_drive_letter = file_path[0]
            if current_drive_letter != old_drive_letter:
                print("The current drive letter {} in {} does not need to repath.".format(current_drive_letter, file_path))
                continue
            new_path = file_path.replace(file_path[0], new_drive_letter)
            if not os.path.exists(new_path):
                print("The new path {} does not exist.".format(new_path))
                continue
            dwg_type.LoadFrom(new_path)
            print ("[{}] ---> [{}]".format(file_path, new_path))
            changed_count += 1
        except Exception as e:
            print("Skip this dwg: {}\nBecasue: {}\n\n".format( dwg_type.LookupParameter("Type Name").AsString() , e ))
            continue
    t.Commit()

    if changed_count == 0:
        NOTIFICATION.messenger("No DWG to repath.")
    else:
        NOTIFICATION.messenger("Repathed {} DWGs.".format(changed_count))


################## main code below #####################
if __name__ == "__main__":
    repath_dwg_drive_letter(DOC)







