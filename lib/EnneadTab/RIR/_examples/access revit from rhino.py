import clr
clr.AddReference("RhinoInside.Revit")
from RhinoInside.Revit import Revit

# application
uiapp = Revit.ActiveUIApplication
dbapp = Revit.ActiveDBApplication

# document
uidoc = Revit.ActiveUIDocument
doc = Revit.ActiveDBDocument



# adding references to the System, RhinoInside
import clr
clr.AddReference('System.Core')
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI')
clr.AddReference('RhinoInside.Revit')

# now we can import symbols from various APIs
from System import Enum

# rhinoscript
import rhinoscriptsyntax as rs

# rhino API
import Rhino

# grasshopper API
import Grasshopper

# revit API
from Autodesk.Revit import DB

# rhino.inside utilities
import RhinoInside
from RhinoInside.Revit import Revit, Convert
# add extensions methods as well
# this allows calling .ToXXX() convertor methods on Revit objects
clr.ImportExtensions(Convert.Geometry)

# getting active Revit document
doc = Revit.ActiveDBDocument