
__title__ = "FallGeosOnGeo"
__doc__ = "Drop selected objs to a receiver geo. If it is block, drop using the insertion point. Otherwise using the center of buttom face of the boundingbox."

import rhinoscriptsyntax as rs
from EnneadTab.RHINO import RHINO_OBJ_DATA
from EnneadTab import ERROR_HANDLE, LOG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def fall_geos_on_geo():
    
    # get the blocks
    #blocks = rs.GetObjects("Pick blocks to project.", rs.filter.instance)
    objs = rs.GetObjects("Pick objs to project.", preselect=True)
    if not objs:
        return

    # get surf or poly surf, 8 and 16 are internal defined object type enum
    landing_geo = rs.GetObject("Pick surface or polysurface to fall onto.", filter = 8 + 16)
    if not landing_geo:
        return

    face_opts = ["Top face", "Bottom face"]
    face_pick = rs.ListBox(items = face_opts, 
                           message = "Project them to the top surfacec or bm surface?",
                           title="EnneadTab Fall Objs Magic")
    if not face_pick: return
    is_top_face = face_pick == face_opts[0]

    
    # disable viewport refreshing to save time.
    rs.EnableRedraw(False)


    # process each block from the block selection
    map(lambda x: process_obj(x, landing_geo, is_top_face), objs)

def process_obj(obj, landing_geo,is_top_face):
    # get block point insertion
    if rs.IsBlockInstance(obj):
        pt = rs.BlockInstanceInsertPoint(obj)
    else:
        pt = RHINO_OBJ_DATA.get_obj_min_center_pt(obj)
        


    # get project to landing_geo pt
    try:
        #proejct block pt to the geometry
        project_pts = list(rs.ProjectPointToSurface(pt, landing_geo, (0,0,-1)))

        # sort result intersection pts by Z value from highest to lowest
        project_pts.sort(key = lambda x: x[2], reverse = is_top_face)

        # only get the highest pt
        project_pt = project_pts[0]
    except Exception as e:
        print (e)
        print ("Cannot project this block over. Skipping.")
        # terminate this action early.
        return

    # move block over
    vector = project_pt - pt
    rs.MoveObject(obj, vector)


if __name__ == "__main__":
    fall_geos_on_geo()