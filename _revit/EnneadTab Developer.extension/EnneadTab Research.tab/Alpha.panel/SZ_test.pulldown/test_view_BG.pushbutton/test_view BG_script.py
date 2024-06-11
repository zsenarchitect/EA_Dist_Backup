from pyrevit import revit, DB
from pyrevit import ApplicationServices
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils

import Autodesk.Revit


__title__ = "View background"
__doc__ = 'I was trying to make the view background toggle between white and dark blue to protect Eye. But it did not work'

print(revit.doc)

print(Autodesk.Revit)
print(Autodesk.Revit.ApplicationServices)
print(Autodesk.Revit.ApplicationServices.Application)
print("00000000")
print(Autodesk.Revit.ApplicationServices.Application.BackgroundColor)
print(DB.Color(20, 70, 100))
print(DB.Color(20, 70, 100).GetType())
para = Autodesk.Revit.ApplicationServices.Application.BackgroundColor
print(para)

revit.para = DB.Color(50, 80, 90)
print(revit.para.Red,revit.para.Green, revit.para.Blue)


#print Autodesk.Revit.ApplicationServices.Application.BackgroundColor
