#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Change parameter keygroup of LifeSafetKey"
__title__ = "change_para_key_group"

# from pyrevit import forms #
from pyrevit import script #


from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error()
def change_para_key_group():
    sample_area = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).FirstElement()

    for para in sample_area.Parameters:
        if "LifeSafetyKey" == para.Definition.Name:
            break

    para_defintion = para.Definition
    print (para_defintion.ParameterGroup)
        


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    change_para_key_group()
    







