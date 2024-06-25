#import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
#import scriptcontext as sc
import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab

@EnneadTab.ERROR_HANDLE.try_catch_error
def delete_poly_srf():
    srfs = rs.ObjectsByType(8)
    rs.ObjectColor(srfs, color = rs.CreateColor([255, 0, 0]))
    rs.UnselectAllObjects()
    polysrfs = rs.ObjectsByType(16)
    rs.DeleteObjects(polysrfs)

################################

if __name__ == "__main__":
    rs.EnableRedraw(False)
    delete_poly_srf()