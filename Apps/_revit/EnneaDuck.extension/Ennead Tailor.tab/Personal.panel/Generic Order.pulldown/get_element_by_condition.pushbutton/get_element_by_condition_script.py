#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Pick a family or system cateogry, pick to copy instance parameter data from A to B."
__title__ = "Transfer\nParameter Data"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_element_by_condition():
    print("ASK SZ for update")
    pass


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    get_element_by_condition()
    










