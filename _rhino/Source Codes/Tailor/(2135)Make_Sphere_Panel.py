import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import time
import sys
sys.path.append("..\lib")
import EnneadTab

COUNTER = 0
TOTAL_COUNT = 0
def process_srf(srf, overall_thickness, open_joint_depth, open_joint_width):
    global COUNTER
    global TOTAL_COUNT
    global START_TIME
    COUNTER += 1
    if COUNTER % 20 == 0:
        used_time = time.time() - START_TIME
        EnneadTab.NOTIFICATION.toast(main_text = "{} of {} processed.".format(COUNTER, TOTAL_COUNT), message = "{} secs = {} mins has passed.".format(used_time, used_time/60))
    pass

    back_layer = rs.OffsetSurface(srf, -open_joint_depth)
    outter_layer = rs.OffsetSurface(srf, open_joint_depth)
    back_solid = rs.OffsetSurface(back_layer, -(overall_thickness - open_joint_depth), create_solid = True)



    border = rs.DuplicateSurfaceBorder(srf, type = 0)
    #pipe = rs.AddPipe(border, 0, 10)
    rs.UnselectAllObjects()
    rs.SelectObjects([srf, border])

    #border = rs.JoinCurves(rs.ExplodeCurves(border), delete_input = True)

    """
    if open_joint_width == 5:
        rs.Command("NoEcho OffsetCrvOnSrf  5 _enter")
    elif open_joint_width == 2:
        rs.Command("NoEcho OffsetCrvOnSrf  2 _enter")
    else:
        print("open_joint_width not defined well")
        return
    """
    rs.Command("NoEcho OffsetCrvOnSrf  {} _enter".format(open_joint_width))



    rs.UnselectAllObjects()
    offseted_border = rs.LastCreatedObjects()
    rs.SelectObject(srf)
    #rs.Command("split _enter")
    #return

    projected_offset_crv = rs.PullCurve(back_layer, offseted_border)
    if len(projected_offset_crv) != 1:
        projected_offset_crv = rs.JoinCurves(projected_offset_crv, delete_input = True)
    projected_offset_crv2 = rs.PullCurve(outter_layer, offseted_border)
    if len(projected_offset_crv2) != 1:
        projected_offset_crv2 = rs.JoinCurves(projected_offset_crv2, delete_input = True)
    rs.DeleteObject(back_layer)
    rs.DeleteObject(outter_layer)
    extruded_cut = rs.AddLoftSrf((projected_offset_crv, projected_offset_crv2))

    #print extruded_cut

    cuts = rs.SplitBrep(srf, extruded_cut, delete_input = False)
    if cuts:
        cuts.sort(key = lambda x: rs.Area(x))
        true_shape = cuts[1]
        rs.DeleteObject(cuts[0])
        rs.DeleteObject(extruded_cut)
        rs.DeleteObjects([projected_offset_crv, projected_offset_crv2, offseted_border, border])
    else:
        rs.ObjectColor(extruded_cut, color = rs.CreateColor(250,10,10))
        EnneadTab.NOTIFICATION.toast(main_text = "failed process color as red", sub_text = "")
        return

    outter_panel = rs.OffsetSurface(true_shape, -(open_joint_depth + 10), create_solid = True)
    rs.DeleteObject(true_shape)
    final = rs.BooleanUnion([outter_panel, back_solid])
    try:
        rs.ShrinkTrimmedSurface(final)
    except Exception as e:
        EnneadTab.NOTIFICATION.toast(main_text = "Cannot shrink surface", sub_text = "skip")
    return final

    #offset_crv = rs.OffsetCurveOnSurface(border, srf, 10)


@EnneadTab.ERROR_HANDLE.try_catch_error
def Run():

    srfs = rs.GetObjects("get base srfs", preselect = True)
    #print srfs

    options = ["Sphere", "Dome"]
    res = rs.ListBox(options, message = "Make surface panel, process Dome or Sphere?")
    if res is None:
        return
    if res == options[0]:
        overall_thickness = 200
        open_joint_depth = 20
        open_joint_width = 5
    else:
        overall_thickness = 50
        open_joint_depth = 10
        open_joint_width = 2.5

    global START_TIME
    START_TIME = time.time()
    rs.EnableRedraw(False)
    collection = []
    global TOTAL_COUNT
    TOTAL_COUNT = len(srfs)
    map(lambda x: collection.append(process_srf(x, overall_thickness, open_joint_depth, open_joint_width)), srfs)

    group = rs.AddGroup()
    rs.AddObjectsToGroup(collection, group)


    end = time.time()
    used_time = end - START_TIME
    rs.Command("savesmall")
    rs.MessageBox("time used = {} seconds = {}mins".format(used_time, used_time/60))




######################  main code below   #########
if __name__ == "__main__":

    Run()

