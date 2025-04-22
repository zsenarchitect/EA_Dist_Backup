import clr # pyright: ignore
clr.AddReference("RhinoInside.Revit")
from RhinoInside.Revit import Revit  # pyright: ignore

# application
uiapp = Revit.ActiveUIApplication
dbapp = Revit.ActiveDBApplication

# document
uidoc = Revit.ActiveUIDocument
doc = Revit.ActiveDBDocument



# adding references to the System, RhinoInside
import clr # pyright: ignore
clr.AddReference('System.Core')
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI')
clr.AddReference('RhinoInside.Revit')

# now we can import symbols from various APIs
from System import Enum # pyright: ignore

# rhinoscript
import rhinoscriptsyntax as rs

# rhino API
import Rhino # pyright: ignore

# grasshopper API
import Grasshopper # pyright: ignore

# revit API
from Autodesk.Revit import DB # pyright: ignore

# rhino.inside utilities
import RhinoInside # pyright: ignore
from RhinoInside.Revit import Revit, Convert # pyright: ignore
# add extensions methods as well
# this allows calling .ToXXX() convertor methods on Revit objects
clr.ImportExtensions(Convert.Geometry)

# getting active Revit document
doc = Revit.ActiveDBDocument