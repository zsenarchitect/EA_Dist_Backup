
import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs

@EnneadTab.ERROR_HANDLE.try_catch_error
def make_profile_sweep_along_srf_edge():
    edge = rs.GetObject("pick surf edge", filter = rs.filter.curve, subobjects = True).Curve()
    print(edge)
    
    profile_blocks = rs.GetObjects("select profile blocks", filter = rs.filter.instance)
    copied_profiles = rs.CopyObjects(profile_blocks)
    shapes = []
    trash = []
    for block in copied_profiles:
        temp_geos = rs.ExplodeBlockInstance(block)
        trash.extend(temp_geos)
        for content in temp_geos:
            if rs.IsCurveClosed(content):
                shapes.append(content)
        
        
        
        
    sweep = rs.AddSweep1(edge, shapes, closed = True)
    rs.CapPlanarHoles(sweep)
    rs.ObjectLayer(sweep, rs.ObjectLayer(shapes[0]))
    rs.DeleteObjects(trash)


if __name__ == "__main__":
    make_profile_sweep_along_srf_edge()
