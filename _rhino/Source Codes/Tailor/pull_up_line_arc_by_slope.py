import sys
sys.path.append("..\lib")
import EnneadTab
###calculate curve(Lines&Arcs) control point parameter
import rhinoscriptsyntax as rs

#return closest points on curve
def close_pt_on_polyline(polyline):
    closest_pts_on_crv = []
    polyline_control_pts = rs.CurvePoints(polyline)
    for i in range(len(polyline_control_pts)):
        closest_pt_para = rs.CurveClosestPoint(polyline, polyline_control_pts[i])
        closest_pt = rs.EvaluateCurve(polyline, closest_pt_para)
        closest_pts_on_crv.append(closest_pt)
        #print closest_pt
    return closest_pts_on_crv


#pts = close_pt_on_polyline(polyline)
#rs.AddPoints(pts)

#spolylineit curve by points and return the length of each segments
def split_polyline_by_closest_control_pts(polyline):
    polyline_control_pts = rs.CurvePoints(polyline)

    closest_pt_para = []
    for i in range(len(polyline_control_pts)):
        temp_para = rs.CurveClosestPoint(polyline, polyline_control_pts[i])
        closest_pt_para.append(temp_para)

    crv_segments = []
    crv_segments = rs.SplitCurve(polyline, closest_pt_para, False)
    crv_segment_length = []
    for i in range(len(crv_segments)):
        length = rs.CurveLength(crv_segments[i])
        #print length
        crv_segment_length.append(length)
    #print crv_segment_length
    rs.DeleteObjects(crv_segments)
    return crv_segment_length

#pull up curve by slope ratio, return curve
def pull_up_crv_by_ratio(polyline, ratio):
    pts = rs.CurvePoints(polyline)
    #polylineLength = rs.CurveLength(polyline)
    crv_segment_length = split_polyline_by_closest_control_pts(polyline)

    ###calculate new elevation for each control point
    new_pt_elevation_list = []
    temp_elevation = 0
    new_pt_elevation = 0
    for i in range(len(pts)):
        if i == 0:
            new_pt_elevation_list.append(0)
        else:
            #temp_elevation = new_pt_elevationParas[i]*crv_segment_length[i-1]
            temp_elevation = ratio * crv_segment_length[i-1]
            new_pt_elevation = new_pt_elevation + temp_elevation
            new_pt_elevation_list.append(new_pt_elevation)

    #pull up curve!!
    newPts = []
    for i in range(len(pts)):
        newPts.append(rs.PointAdd(pts[i],(0,0,new_pt_elevation_list[i])))
    rs.EnableObjectGrips(polyline, True)
    for i in range(len(newPts)):
        rs.ObjectGripLocation(polyline, i, newPts[i])
    rs.EnableObjectGrips(polyline, False)
    return polyline


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    polyline = rs.GetObjects("pick polyline", 4)
    ratio = rs.GetReal("Input Slope Ratio For New Curve", 0.125)
    segment_length = split_polyline_by_closest_control_pts(polyline)
    print(segment_length)

    newpolyline = pull_up_crv_by_ratio(polyline, ratio)

###############################
if __name__ == "__main__":
    main()
