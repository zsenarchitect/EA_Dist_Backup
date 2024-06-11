#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE"
__title__ = "Replace Parameter(NOT IN USE)"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


################## main code below #####################
output = script.get_output()
output.close_others()
