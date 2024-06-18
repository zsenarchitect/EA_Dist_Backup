import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext
import random

"""
### TO-DO:
- Possible better way to illustrate clamp dist w/out pipe?
#### Assigned to: **CM**
"""


def get_block_dist_to_crv(block, crv):
    #rs.CurveClosestObject(crv, object_ids)
    pt = rs.BlockInstanceInsertPoint(block)
    param = rs.CurveClosestPoint(crv, pt, segment_index=-1 )
    closest_pt = rs.EvaluateCurve(crv, param, segment_index=-1)
    return rs.Distance(closest_pt, pt)

def map_num_linear(X, x0, x1, y0, y1):
    """
    x0, x1 ---> input range
    y0, y1 ---> output range
    """
    k = (y1 - y0) / (x1 - x0)
    b = y0 - k * x0
    #print k
    #print b
    Y = k * float(X) + b
    return Y

def ClampError():
    pass

def map_num_with_clamp(X, x0, x1, y0, y1, clamp0, clamp1):
    """
    if clamp0 < x0 or clamp1 > x1:
        #raise ClampError('clamps must be between input range')
        print("clamp error")
        return None
    """
    """
    X = max(X, clamp0)
    X = min(X, clamp1)
    """
    if X < clamp0:
        return y0
    if X > clamp1:
        return y1
    return map_num_linear(X, clamp0, clamp1, y0, y1)


def filter_by_mask(X, Y):
    """
    X ---> obj list
    Y ---> boolean list
    """
    OUT = []
    for a, b in zip(X, Y):
        if b:
            OUT.append(a)
    return OUT


@EnneadTab.ERROR_HANDLE.try_catch_error
def random_deselect_by_dist():


    blocks = rs.GetObjects(message = "pick blocks pool", filter = 4096, preselect = True)
    base_crv = rs.GetObject(message = "pick base crv as attractor, for attractor-point-like behaviour, make a tiny circle around point.", filter = rs.filter.curve, preselect = True)
    if not blocks: return
    if not base_crv: return

    dist_map = [get_block_dist_to_crv(x, base_crv) for x in blocks]
    sorted_map = sorted(dist_map)
    min_dist = float(sorted_map[0])
    max_dist = float(sorted_map[-1])
    min_factor = 0.0
    max_factor = 1.0

    clamp0, clamp1 = rs.PropertyListBox(items = ["near clamp", "far clamp"], values = [min_dist, max_dist], message = "Distance outside the bounds of near/far clamp will be clampped(file unit)", title = "Random De-Select by Crv")
    clamp0, clamp1 = float(clamp0), float(clamp1)

    circles = []
    center = rs.CurveEndPoint(base_crv)
    circles.append(rs.AddCircle(center, clamp0))
    circles.append(rs.AddCircle(center, clamp1))
    rs.AddObjectsToGroup(circles, rs.AddGroup())

    try:
        pipes = []
        pipes.append(rs.AddPipe(base_crv, parameters = 0, radii = clamp0, blend_type = 0, cap = 2, fit = False))
        pipes.append(rs.AddPipe(base_crv, parameters = 0, radii = clamp1, blend_type = 0, cap = 2, fit = False))
        rs.AddObjectsToGroup(pipes, rs.AddGroup())
    except:
        pass




    factor_map = [map_num_with_clamp(x, min_dist, max_dist, min_factor, max_factor, clamp0, clamp1) for x in dist_map]
    threshold = 0.5
    # random.random()
    #keep_map = [random.uniform(x, 1) > threshold  for x in factor_map]
    keep_map = [random.random() < x  for x in factor_map]

    """
    for factor in factor_map:
        print("***")
        print(factor)
        print(random.uniform(0, factor))
        print(random.uniform(factor, 1))
    """

    kept_blocks = filter_by_mask(blocks, keep_map)
    rs.UnselectAllObjects()
    rs.SelectObjects(kept_blocks)
    return


if __name__=="__main__":
    random_deselect_by_dist()

"""
import rhinoscriptsyntax as rs
filter = rs.filter.curve | rs.filter.pointcloud | rs.filter.surface | rs.filter.polysurface
objects = rs.GetObjects("Select target objects for closest point", filter)
if objects:
    curve = rs.GetObject("Select curve")
    if curve:
        results = rs.CurveClosestObject(curve, objects)
        if results:
            print("Curve id:", results[0])
            rs.AddPoint( results[1] )
            rs.AddPoint( results[2] )
"""
