
from pyrevit import forms
from pyrevit import script

import EA_UTILITY
import EnneadTab 
from rpw.extras.rhino import Rhino as rc
from Autodesk.Revit import DB # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


"""import clr
clr.AddReference('System.Core')
clr.AddReference('RhinoInside.Revit')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from System import Enum

import rhinoscriptsyntax as rs
import Rhino
import RhinoInside
import Grasshopper # pyright: ignore as GH
from RhinoInside.Revit import Revit
clr.ImportExtensions(RhinoInside.Revit.Convert.Geometry)
"""
__doc__ = "try to save revit 3D view as new rhino file"
__title__ = "Revit2Rhino Converter(Beta)"


if not EA_UTILITY.is_SZ():
    EA_UTILITY.dialogue(main_text = "this tool is not ready for general usage")
output = script.get_output()
output.close_others()



def get_object_from_revit_element(element):
    """
    geo_element = element.Geometry[geo_opt]
    if geo_element is None:
        return None
    for geo_instance in geo_element:
        instance_geo = geo_instance.GetInstanceGeometry()
        print(instance_geo)
    """


    geo_element = element.get_Geometry(geo_opt)
    if geo_element is None:
        return None


    # print geo_element.GetEnumerator()
    temp = []
    for geo_obj in geo_element.GetEnumerator():
        print(geo_obj)
        temp.append(geo_obj)
    # geo = element.Geometry(geo_opt)
    return temp

def brep_from_geo(geo):
    DB.BRepBuilder(DB.BRepType.Solid)
###########################################################################

active_view = doc.ActiveView
if active_view.ViewType != DB.ViewType.ThreeD:
    EA_UTILITY.dialogue(main_text = "Do it in 3D view")
    script.exit()

# get all geo in current 3d view
elements = DB.FilteredElementCollector(doc, active_view.Id).WhereElementIsNotElementType().ToElements()


geo_opt = DB.Options()
geo_opt.IncludeNonVisibleObjects = False
geo_opt.ComputeReferences = True
# for each , get geo, geo subC info, expand to layer mapping, parent layer = parent category
revit_objects = []
for x in elements:
    if get_object_from_revit_element(x) is not None:
        revit_objects.extend(get_object_from_revit_element(x))
print("*"*20)
print(revit_objects)

# prepare object table




# write





pt1 = rc.Geometry.Point3d(0,0,0)
pt2 = rc.Geometry.Point3d(10,10,0)
line1 = rc.Geometry.Line(pt1, pt2)
print(line1.Length)

pt1 = rc.Geometry.Point3d(10,0,0)
pt2 = rc.Geometry.Point3d(0,10,0)
line2 = rc.Geometry.Line(pt1, pt2)

print(rc.Geometry.Intersect.Intersection.LineLine(line1, line2))


file3dm = f = rc.FileIO.File3dm()
file3md_options = rc.FileIO.File3dmWriteOptions()
file3dm.Objects.AddLine(line1)
for x in revit_objects:
    try:

        file3dm.Objects.Add(x)
    except Exception as e:
        print (e)
for x in revit_objects:
    try:
        brep = rc.Geometry.Brep.TryConvertBrep(x)
        file3dm.Objects.AddBrep(brep)
    except Exception as e:
        print (e)
filepath = r"C:\Users\szhang\Desktop\temp1.3dm"
print(file3dm.Write(filepath, file3md_options))


"""
revit element geo get transform and face from solid,
rhino object AddSurface(brep, face)
"""
"""
https://github.com/mcneel/rhino.inside-revit/blob/5264c27f66c603645bb301904d36d20a59650969/src/RhinoInside.Revit/Convert/Geometry/Raw/RawDecoder.cs

in the source code, the convert have a method for each geo type. Surface, polycurve, curve etc.
"""

"""
    public static Transform AsTransform(ARDB.Transform transform)
    {
      var value = new Transform
      {
        M00 = transform.BasisX.X,
        M10 = transform.BasisX.Y,
        M20 = transform.BasisX.Z,
        M30 = 0.0,

        M01 = transform.BasisY.X,
        M11 = transform.BasisY.Y,
        M21 = transform.BasisY.Z,
        M31 = 0.0,

        M02 = transform.BasisZ.X,
        M12 = transform.BasisZ.Y,
        M22 = transform.BasisZ.Z,
        M32 = 0.0,

        M03 = transform.Origin.X,
        M13 = transform.Origin.Y,
        M23 = transform.Origin.Z,
        M33 = 1.0
      };

      return value;
    }
"""
