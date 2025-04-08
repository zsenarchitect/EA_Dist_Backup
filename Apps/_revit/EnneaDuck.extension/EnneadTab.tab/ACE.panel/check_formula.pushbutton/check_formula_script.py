#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Excel formula validation tool that reveals hidden calculation relationships. This quality control utility inspects spreadsheets for embedded formulas, highlighting cells with dependencies to help verify calculation accuracy. Perfect for validating critical data before importing into Revit or when reviewing calculations from external sources to prevent errors in your documentation."
__title__ = "Inspect Excel\nFormula"
__tip__ = True
__is_popular__ = True
from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, EXCEL, NOTIFICATION, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

doc = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def check_formula():

    excel = forms.pick_excel_file()
    if not excel:
        return
    # if excel.endswith(".xlsx"):
    #     NOTIFICATION.messenger("Please saveas .xls")
    sheets = EXCEL.get_all_worksheets(excel)
    sheet = forms.SelectFromList.show(sheets, button_name="Select WorkSheet", multiselect=False, title="Which worksheet to check??")
    EXCEL.check_formula(excel, sheet)
    pass


    NOTIFICATION.messenger("Done! All formula printed!\nAll formula cell are highlighted in dash border in a local copy.")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    check_formula()
    







