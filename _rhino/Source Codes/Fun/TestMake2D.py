
import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore

@EnneadTab.ERROR_HANDLE.try_catch_error
def TestMake2D():
    msg="Select objects to draw"
    #check object collections
    objIDs=rs.GetObjects(msg,8+16,preselect=True)
    if not objIDs: return

    objs=[sc.doc.Objects.Find(objID).Geometry for objID in objIDs]

#    #Artificially set a top view projection (no viewport needed)
#    bb=rs.BoundingBox(objIDs)
#    rot_pt=(bb[0]+bb[6])/2
#    ht=bb[4].Z-bb[0].Z
#    z_vec=Rhino.Geometry.Vector3d.ZAxis
#    vp=Rhino.Display.RhinoViewport()
#    vp.ChangeToParallelProjection(True)
#    vp.SetCameraTarget(rot_pt-(z_vec*ht),False)
#    vp.SetCameraLocation(rot_pt+z_vec*ht,False)

    #get Top viewport from standard Rhino views
    for view in sc.doc.Views.GetStandardRhinoViews():
        if view.MainViewport.Name=="Top":
            vp=view.MainViewport
            break

    #Create the Make2D drawing
    hdp=Rhino.Geometry.HiddenLineDrawingParameters()
    [hdp.AddGeometry(obj,"") for obj in objs]
    hdp.SetViewport(vp)
    hld=Rhino.Geometry.HiddenLineDrawing.Compute(hdp,True)
    if hld:
        crvs=[]
        vis=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Visible
        hid=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Hidden
        proj=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Projecting
        dup=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Duplicate
        clip=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Clipped
        uns=Rhino.Geometry.HiddenLineDrawingSegment.Visibility.Unset

        rs.EnableRedraw(False)
        for i,seg in enumerate(hld.Segments):
            print("Segment {} Type:{}".format(i,seg.SegmentVisibility))
            if not seg.SegmentVisibility == vis:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Visible")
            elif seg.SegmentVisibility == hid:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Hidden")
            elif seg.SegmentVisibility == proj:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Projecting")
            elif seg.SegmentVisibility == dup:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Duplicate")
            elif seg.SegmentVisibility == clip:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Clipped")
            elif seg.SegmentVisibility == uns:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Unset")
            else:
                crvID=sc.doc.Objects.AddCurve(seg.CurveGeometry)
                rs.ObjectLayer(crvID,"Unknown")
    sc.doc.Views.Redraw()
    
if __name__ == "__main__":
    TestMake2D()
