__title__ = "RandomDeselectByDist"
__doc__ = """Randomly deselects blocks based on their distance from a curve.

The probability of keeping a block is proportional to its distance from the curve.
Blocks closer to the curve have higher chance of being kept.
Distance clamping is available to control the influence range.

Usage:
1. Pre-select blocks or select when prompted
2. Select a base curve as attractor
3. Adjust distance clamps in the dialog
"""

import rhinoscriptsyntax as rs
import scriptcontext
import random
from EnneadTab import ERROR_HANDLE, LOG


def map_num_linear(X, x0, x1, y0, y1):
    """Maps a number from one range to another linearly.
    
    Args:
        X (float): Input value to map
        x0 (float): Input range start
        x1 (float): Input range end
        y0 (float): Output range start
        y1 (float): Output range end
    
    Returns:
        float: Mapped value in output range
    """
    k = (y1 - y0) / (x1 - x0)
    b = y0 - k * x0
    return k * float(X) + b


def map_num_with_clamp(X, x0, x1, y0, y1, clamp0, clamp1):
    """Maps a number with clamping at boundaries.
    
    Args:
        X (float): Input value to map
        x0, x1 (float): Input range
        y0, y1 (float): Output range
        clamp0 (float): Lower clamp threshold
        clamp1 (float): Upper clamp threshold
    
    Returns:
        float: Mapped and clamped value
    """
    if X < clamp0:
        return y0
    if X > clamp1:
        return y1
    return map_num_linear(X, clamp0, clamp1, y0, y1)


def get_block_dist_to_crv(block, crv):
    """Calculates distance from block insertion point to closest point on curve.
    
    Args:
        block: Block instance ID
        crv: Curve ID
    
    Returns:
        float: Distance between block and curve
    """
    pt = rs.BlockInstanceInsertPoint(block)
    param = rs.CurveClosestPoint(crv, pt, segment_index=-1)
    closest_pt = rs.EvaluateCurve(crv, param, segment_index=-1)
    return rs.Distance(closest_pt, pt)


def filter_by_mask(obj_list, bool_mask):
    """Filters a list of objects using a boolean mask.
    
    Args:
        obj_list (list): Objects to filter
        bool_mask (list): Boolean values determining which objects to keep
    
    Returns:
        list: Filtered objects where mask is True
    """
    return [obj for obj, keep in zip(obj_list, bool_mask) if keep]


def create_visualization(base_crv, clamp0, clamp1):
    """Creates visual guides showing the clamping distances.
    
    Args:
        base_crv: Curve ID
        clamp0 (float): Near clamp distance
        clamp1 (float): Far clamp distance
    """
    # Create circles if curve is short/point-like
    circles = []
    center = rs.CurveEndPoint(base_crv)
    circles.append(rs.AddCircle(center, clamp0))
    circles.append(rs.AddCircle(center, clamp1))
    rs.AddObjectsToGroup(circles, rs.AddGroup())

    # Try creating pipes for longer curves
    try:
        pipes = []
        pipes.append(rs.AddPipe(base_crv, parameters=0, radii=clamp0, blend_type=0, cap=2, fit=False))
        pipes.append(rs.AddPipe(base_crv, parameters=0, radii=clamp1, blend_type=0, cap=2, fit=False))
        rs.AddObjectsToGroup(pipes, rs.AddGroup())
    except:
        pass


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def random_deselect_by_dist():
    """Main function to randomly deselect blocks based on distance from curve."""
    
    # Get input geometry
    blocks = rs.GetObjects(message="Pick blocks pool", filter=4096, preselect=True)
    base_crv = rs.GetObject(message="Pick base curve as attractor (use small circle for point-like behavior)", 
                           filter=rs.filter.curve, preselect=True)
    if not blocks or not base_crv:
        return

    # Calculate distance range
    dist_map = [get_block_dist_to_crv(x, base_crv) for x in blocks]
    sorted_map = sorted(dist_map)
    min_dist = float(sorted_map[0])
    max_dist = float(sorted_map[-1])

    # Get user input for clamping
    clamp0, clamp1 = rs.PropertyListBox(
        items=["near clamp", "far clamp"],
        values=[min_dist, max_dist],
        message="Distance outside bounds will be clamped (file unit)",
        title="Random De-Select by Curve"
    )
    clamp0, clamp1 = float(clamp0), float(clamp1)

    # Create visual guides
    create_visualization(base_crv, clamp0, clamp1)

    # Calculate probabilities and filter
    factor_map = [map_num_with_clamp(x, min_dist, max_dist, 1.0, 0.0, clamp0, clamp1) for x in dist_map]
    keep_map = [random.random() < x for x in factor_map]
    kept_blocks = filter_by_mask(blocks, keep_map)

    # Update selection
    rs.UnselectAllObjects()
    rs.SelectObjects(kept_blocks)


if __name__ == "__main__":
    random_deselect_by_dist()
