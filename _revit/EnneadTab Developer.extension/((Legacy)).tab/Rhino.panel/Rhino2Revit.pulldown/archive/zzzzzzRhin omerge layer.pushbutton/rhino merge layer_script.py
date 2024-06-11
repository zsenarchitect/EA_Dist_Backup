
import EA_UTILITY
import EnneadTab
from pyrevit import script
from rpw.extras.rhino import Rhino as rc
from Autodesk.Revit import DB # pyright: ignore

doc = __revit__.ActiveUIDocument.Document # pyright: ignore


__doc__ = "xxxx"
__title__ = "Rhino Merge Layer(Beta)"


if not EA_UTILITY.is_SZ():
    EA_UTILITY.dialogue(main_text = "this tool is not ready for general usage")
output = script.get_output()
output.close_others()
# output.self_destruct(160)

###########################################################################


"""
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
"""

"""
only rhino 5 is open-able, when you save checking file as rhino 7 it cannot read.
"""
filepath = r"C:\Users\szhang\Desktop\test_merge.3dm"
file3dm = f = rc.FileIO.File3dm()
rhino_file = file3dm.Read(filepath)
print(rhino_file)
all_layers = rhino_file.Layers
print(all_layers)
for layer in all_layers:
    print(layer.Name)
