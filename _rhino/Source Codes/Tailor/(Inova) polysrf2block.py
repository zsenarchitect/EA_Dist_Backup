"""
requested by Paula, 
this script does not have a button on the rui, this run directly in python editor

convert all polysrf to block with same transformation
"""

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

@EnneadTab.ERROR_HANDLE.try_catch_error
def run():
    ref_polysrfs = rs.GetObjects("get polysrfs")
    if not ref_polysrfs:
        return
    rs.EnableRedraw(False)
    total = len(ref_polysrfs)
    for i, polysrf_id in enumerate(ref_polysrfs):
        if i %100==0:
            print ("{}/{}".format(i + 1, total))
            rs.Redraw()
        process_polysrf(polysrf_id)
    
def process_polysrf(polysrf_id):
    if not rs.IsPolysurface(polysrf_id):
        return
    polysrf = sc.doc.Objects.Find(polysrf_id).Geometry
    for face in polysrf.Faces:
        # print face.NormalAt(0,0).Z
        if face.NormalAt(0,0).Z < -0.1:
            break

    
    center = Rhino.Geometry.AreaMassProperties.Compute(face).Centroid
    
    domain_U = face.Domain(0)
    domain_U = domain_U.T1 - domain_U.T0
    domain_V = face.Domain(1)
    domain_V = domain_V.T1 - domain_V.T0
    
    # rs.SurfaceFrame()
    # rs.PlaneFromFrame()
    res, plane = face.FrameAt(domain_U*0.5, domain_V*0.5)
    
    plane.Flip()
    x_axis = plane.XAxis
    # print x_axis
    y_axis = plane.YAxis
    face_plane = Rhino.Geometry.Plane(center, x_axis, y_axis)
    transform = Rhino.Geometry.Transform.ChangeBasis(face_plane,
                                                    Rhino.Geometry.Plane.WorldXY)
    
    
    rs.InsertBlock2("brick", transform)
    


######################  main code below   #########
if __name__ == "__main__":

    run()

