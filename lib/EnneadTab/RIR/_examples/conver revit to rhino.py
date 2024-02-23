import clr
clr.AddReference('RevitAPI') 


from RhinoInside.Revit import Convert

from Autodesk.Revit import DB

clr.ImportExtensions(Convert.Geometry)

G = [x.ToBrep() for x in Element.Geometry[DB.Options()]]