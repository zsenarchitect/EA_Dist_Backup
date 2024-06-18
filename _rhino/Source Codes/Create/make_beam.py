import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")
import EnneadTab



@EnneadTab.ERROR_HANDLE.try_catch_error
def make_beam(profile = None, base_crv = None, use_profile_bounding = False,  use_rs = True):

    if base_crv is None:
        base_crv = rs.GetObject(message = "pick single base curve", custom_filter = rs.filter.curve)
        #print base_crv

    map_profile_at_begining = not(rs.IsCurveClosed(base_crv))
    if map_profile_at_begining:
        t = 0
    else:
        t = 0.5
    para = rs.CurveParameter(base_crv, t)
    target_plane = rs.CurvePerpFrame(base_crv, para)
    #rs.AddPlaneSurface(target_plane, 100,100)
    target = [rs.EvaluatePlane(target_plane, (0,0)),
            rs.EvaluatePlane(target_plane, (10,0)),
            rs.EvaluatePlane(target_plane, (0,10))]

    if profile is None:
        profile = rs.GetObject(message = "pick profile curves in block", custom_filter = rs.filter.instance)


    pt0 = rs.BlockInstanceInsertPoint(profile)
    pt1 = rs.CopyObject(pt0, [10,0,0])
    pt2 = rs.CopyObject(pt0, [0,10,0])
    reference = [pt0,
                pt1,
                pt2]
    profile_on_crv = rs.OrientObject(profile, reference, target, flags = 1)
    profile_on_crv = rs.ExplodeBlockInstance(profile_on_crv)


    if use_profile_bounding:
        corner_pts = rs.BoundingBox(profile_on_crv, target_plane)
        corner_pts = rs.CullDuplicatePoints(corner_pts)
        patch = rs.AddPatch(corner_pts)
        profile_on_crv = rs.DuplicateSurfaceBorder(patch, type = 1)
        rs.DeleteObjects(corner_pts)
        rs.DeleteObject(patch)

    beams = []
    for profile_element in profile_on_crv:

        if use_rs:
            beam = rs.AddSweep1(base_crv, [profile_element], closed = True)


        else:
            rs.UnselectAllObjects()
            #rs.SelectObjects([base_crv,profile_element])
            rs.SelectObjects([profile_element,base_crv])

            #.format(rs.coercegeometry(base_crv), rs.coercegeometry(profile_element))
            rs.Command("_NoEcho _Sweep1  _Style=_Roadlike _UntrimmedMiters=_Yes _EnterEnd", echo = False)
            beam = rs.LastCreatedObjects()
            #rs.UnselectAllObjects()
            #rs.SelectObject(beam)
            #rs.Command("_MergeAllCoplanarFaces")



        try:
            rs.ObjectLayer(beam, rs.ObjectLayer(profile_element))
        except:
            pass
            print("cannot assign beam layer")
        try:
            rs.CapPlanarHoles(beam)
        except:
            pass
            print("cannot cap beams")

        beams.append(beam)

    rs.DeleteObject(pt1)
    rs.DeleteObject(pt2)
    if profile_on_crv:
        rs.DeleteObjects(profile_on_crv)
    #print beam
    if len(beams) > 1:
        rs.AddObjectsToGroup(beams, rs.AddGroup())
    return beams


#####
if __name__ == "__main__":
    #make_beam(map_profile_at_begining = False)
    make_beam()
