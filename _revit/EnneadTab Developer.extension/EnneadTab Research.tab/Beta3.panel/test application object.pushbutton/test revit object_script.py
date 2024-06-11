#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "quick test on revit object"

from pyrevit import script
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
################## main code below #####################
output = script.get_output()
output.close_others()

uiapp = __revit__
print(uiapp)
uiapp = UI.UIApplication
print(uiapp)
uidoc = UI.UIApplication.ActiveUIDocument
print(uidoc)
uidoc = UI.UIDocument
print(uidoc)
doc = UI.UIDocument.Document
print(doc)
uidoc = __revit__.ActiveUIDocument
print(uidoc)
# selection_ids = UI.Selection.Selection.GetElementIds (doc)
selection_ids = uidoc.Selection.GetElementIds ()
selection = [doc.GetElement(x) for x in selection_ids]
print(selection)
