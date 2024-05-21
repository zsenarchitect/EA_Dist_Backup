import clr # pyright: ignore
clr.AddReference('RevitAPI') 


from RhinoInside.Revit import Convert

from Autodesk.Revit import DB # pyright: ignore

clr.ImportExtensions(Convert.Geometry)

G = [x.ToBrep() for x in Element.Geometry[DB.Options()]]