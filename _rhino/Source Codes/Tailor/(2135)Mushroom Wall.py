import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore


@EnneadTab.ERROR_HANDLE.try_catch_error
def run():
    pass
    
    base_brep = rs.GetObject("pick guide polysurf", preselect = True)
    
    outter_face = Rhino.Geometry.Brep.CreateOffsetBrep(brep = base_brep, 
                                                        distance = 50, 
                                                        solid = False, 
                                                        extend = True,
                                                        shrink = True)
    OUT = Rhino.Geometry.Brep.CreateOffsetBrep(outter_face, 250, solid = True, extend = True)
    #outter_face = rs.OffsetSurface(srf, 50)
    #inner_face = rs.OffsetSurface(srf, 300)
    print(outter_face)
    
    
    
if __name__ == "__main__":
    run()