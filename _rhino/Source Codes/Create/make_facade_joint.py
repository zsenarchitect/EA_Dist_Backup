import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore
import sys
sys.path.append("..\lib")

import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def make_facade_joint(joint_block = None, base_srf = None, at_corner = True, spacing_along_edge = -1):





    if base_srf is None:
        base_srf = rs.GetObject(message = "pick single base srf", custom_filter = rs.filter.surface)
        #print base_crv
    if joint_block is None:
        joint_block = rs.GetObject(message = "pick joint block", custom_filter = rs.filter.instance)


    base_crv = rs.DuplicateSurfaceBorder(base_srf, type = 1)
    offset_srf = rs.OffsetSurface(base_srf, 100)


    #base_pts = rs.CurveDiscontinuity(base_crv, style = 3)
    #base_pts = rs.CurveKnots(base_crv)
    base_pts = []
    if at_corner:
        base_pts.extend( get_crv_corner_pts(base_crv))
    if spacing_along_edge > 0:
        base_pts.extend( get_crv_distributed_pts(base_crv, spacing_along_edge))
    #print base_pts
    ref_pts = rs.PullPoints(offset_srf, base_pts)
    #print ref_pts
    z_vecs = [rs.CreateVector(y - x) for x,y in zip(base_pts, ref_pts)]
    y_vecs = [rs.CurveTangent(base_crv, rs.CurveClosestPoint(base_crv, pt)) 
                for pt in base_pts]
    x_vecs = [rs.VectorCrossProduct(y, z) for y, z in zip(y_vecs, z_vecs)]

    blocks = [orient_block(rs.BlockInstanceName(joint_block),
                            pt, X, Y, 
                            rs.ObjectLayer(joint_block)) 
                            for pt, X, Y in zip(base_pts, x_vecs, y_vecs)]




    rs.DeleteObject(base_crv)
    rs.DeleteObject(offset_srf)
    #rs.DeleteObjects(rs.coerce3dpointlist(base_pts + ref_pts))



    if len(blocks) > 1:
        rs.AddObjectsToGroup(blocks, rs.AddGroup())
    return blocks


def get_crv_distributed_pts(crv, spacing_along_edge):
    OUT = []
    for seg in rs.ExplodeCurves(crv):
        length = rs.CurveLength(seg)
        count = int(length / spacing_along_edge)
        temp = rs.DivideCurve(seg, count + 1)
        OUT.extend(temp[1:-1])
        rs.DeleteObject(seg)
    return OUT
    
    
def get_crv_corner_pts(crv):
    OUT = []
    for seg in rs.ExplodeCurves(crv):
        OUT.append(rs.CurveStartPoint(seg))
        rs.DeleteObject(seg)
    return OUT
    #return [rs.CurveStartPoint(seg) for seg in rs.ExplodeCurves(crv)]



def orient_block(block_name, 
                insert_pt, insert_X_axis, insert_Y_axis, 
                target_layer = None):
    initial_plane = rs.CreatePlane([0,0,0], x_axis = [1,0,0], y_axis = [0,1,0], ignored = None)
    final_plane = rs.CreatePlane(insert_pt, x_axis = insert_X_axis, y_axis = insert_Y_axis, ignored = None)

    transform = rs.XformChangeBasis(final_plane, initial_plane)
    #print transform
    #rs.InsertBlock2(stair_name, transform)
    temp_block = rs.InsertBlock(block_name, [0,0,0])
    rs.TransformObject(temp_block, transform)
    if target_layer is not None:
        rs.ObjectLayer(temp_block, target_layer)
    
    return temp_block
#####
if __name__ == "__main__":
    #make_beam(map_profile_at_begining = False)
    make_facade_joint()
