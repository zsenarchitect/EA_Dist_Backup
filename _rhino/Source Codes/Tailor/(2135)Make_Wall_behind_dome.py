import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import time
import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab


def process_srf(srf, outter_layer_from_FOW, wall_thickness):
    pass
    rs.UnselectAllObjects()

    back_layer = rs.OffsetSurface(srf, -outter_layer_from_FOW)
    rs.SelectObject(back_layer)
    #back_solid = rs.OffsetSurface(back_layer, - wall_thickness, create_solid = True)
    back_solid = rs.Command("OffsetSrf _Pause {}  _DeleteInput=_Yes  _Enter _EnterEnd".format(-wall_thickness))

    return back_solid

    #offset_crv = rs.OffsetCurveOnSurface(border, srf, 10)


@EnneadTab.ERROR_HANDLE.try_catch_error
def Run():

    srfs = rs.GetObjects("get base srfs", preselect = True)
    #print srfs

    options = ["Sphere", "Dome"]
    res = rs.ListBox(options, message = "Make behind wall panels,,,,,,,,,,,,,process Dome or Sphere?")
    if res is None:
        return
    if res == options[0]:
        overall_thickness = 200
        open_joint_depth = 20
        open_joint_width = 5
    else:
        outter_layer_from_FOW = 50
        wall_thickness = 250


    start = time.time()
    rs.EnableRedraw(False)
    collection = []
    map(lambda x: collection.append(process_srf(x, outter_layer_from_FOW, wall_thickness)), srfs)

    group = rs.AddGroup()
    rs.AddObjectsToGroup(collection, group)


    end = time.time()
    used_time = end - start
    rs.MessageBox("time used = {} seconds = {}mins".format(used_time, used_time/60))




######################  main code below   #########
if __name__ == "__main__":

    Run()

