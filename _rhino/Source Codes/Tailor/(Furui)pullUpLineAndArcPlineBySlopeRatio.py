import sys
sys.path.append("..\lib")
import EnneadTab
###calculate curve(Lines&Arcs) control point parameter 
import rhinoscriptsyntax as rs

#return closest points on curve
def ClosestPtsOnLineAndArcPline(pl):
    ClosestPtsOnCrv = []
    plCtrlPts = rs.CurvePoints(pl)
    for i in range(len(plCtrlPts)):
        ClosestPtPara = rs.CurveClosestPoint(pl, plCtrlPts[i])
        ClosestPt = rs.EvaluateCurve(pl, ClosestPtPara)
        ClosestPtsOnCrv.append(ClosestPt)
        #print ClosestPt
    return ClosestPtsOnCrv

pl = rs.GetObjects("pick polyline", 4)
ratio = rs.GetReal("Input Slope Ratio For New Curve", 0.125)
#pts = ClosestPtsOnLineAndArcPline(pl)
#rs.AddPoints(pts)

#split curve by points and return the length of each segments
def SplitLineAndArcPlineByClosestCtrlPts(pl):
    plCtrlPts = rs.CurvePoints(pl)
    
    ClosestPtParas = []
    for i in range(len(plCtrlPts)):
        tempPara = rs.CurveClosestPoint(pl, plCtrlPts[i])
        ClosestPtParas.append(tempPara)
    
    crvSegments = []
    crvSegments = rs.SplitCurve(pl, ClosestPtParas, False)
    crvSegmentLength = []
    for i in range(len(crvSegments)):
        length = rs.CurveLength(crvSegments[i])
        #print length
        crvSegmentLength.append(length)
    #print crvSegmentLength
    rs.DeleteObjects(crvSegments)
    return crvSegmentLength

#pull up curve by slope ratio, return curve
def PullUpCrvByRatio(pl, ratio):
    pts = rs.CurvePoints(pl)
    plLength = rs.CurveLength(pl)
    crvSegmentLength = SplitLineAndArcPlineByClosestCtrlPts(pl)
    
    ###calculate new elevation for each control point
    newPtElevationList = []
    tempElevation = 0
    newPtElevation = 0
    for i in range(len(pts)):
        if i == 0:
            newPtElevationList.append(0)
        else:
            #tempElevation = newPtElevationParas[i]*crvSegmentLength[i-1]
            tempElevation = ratio*crvSegmentLength[i-1]
            newPtElevation = newPtElevation + tempElevation
            newPtElevationList.append(newPtElevation)
    
    #pull up curve!!
    newPts = []
    for i in range(len(pts)):
        newPts.append(rs.PointAdd(pts[i],(0,0,newPtElevationList[i])))
    rs.EnableObjectGrips(pl, True)
    for i in range(len(newPts)):
        rs.ObjectGripLocation(pl, i, newPts[i])
    rs.EnableObjectGrips(pl, False)
    return pl

segmentLength = SplitLineAndArcPlineByClosestCtrlPts(pl)
print(segmentLength)

newPl = PullUpCrvByRatio(pl, ratio)