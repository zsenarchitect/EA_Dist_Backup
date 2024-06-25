
import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import math #Use this to get sine, cosine and radians.
import scriptcontext as sc

@EnneadTab.ERROR_HANDLE.try_catch_error
def test():
 
        #Assign variables to the sin and cos functions for use later.
    Sin = math.sin
    Cos = math.cos
 
 
    	# Acquire information for the garden path
 
    	# set default values for the distances
    default_hwidth = 1000
    default_trad = 100
    default_tspace = 100
 
 

 
        #get the path direction, length and location from two points entered by the user
    sp = rs.GetPoint("Start point of path centerline")
    if sp is None: return

    ep = rs.GetPoint("End point of path centerline", sp)
    if ep is None: return
 
        #now ask the user what the distances should be, offering the defaults arrived at above
 
    hwidth = default_hwidth
    if hwidth is None: return
 
        #Store the new value in sticky for use next time
    sc.sticky["GP_WIDTH"] = hwidth
 
    trad = default_trad
    if trad is None: return
 
        #Store  the new value in sticky for use next time
    sc.sticky["GP_RAD"] = trad
 
    tspace = default_tspace
    if tspace is None: return
 
        #Store  the new value in sticky for use next time
    sc.sticky["GP_SPACE"] = tspace
 
    	# Calculate angles
 
    temp = rs.Angle(sp, ep)
 
    pangle = temp[0]
 
    plength = rs.Distance(sp, ep)
 
    width = hwidth * 2
 
    angp90 = pangle + 90.0
 
    angm90 = pangle - 90.0
 
 
	# To increase speed, disable redrawing
 
    rs.EnableRedraw (True)
 
	# Draw the outline of the path
    #make an empty list
    pline = []
 
    #add points to the list
    pline.append(rs.Polar(sp, angm90, hwidth))
 
    pline.append(rs.Polar(pline[0], pangle, plength))
 
    pline.append(rs.Polar(pline[1], angp90, width))
 
    pline.append(rs.Polar(pline[2], pangle + 180.0, plength))
 
    #add the first point back on to the end of the list to close the pline
    pline.append (pline[0])
 
    #create the polyline from the lst of points.
    rs.AddPolyline (pline)
 
 
 
    # Draw the rows of tiles
 
    #define a plane -
    #using the WorldXY plane the reults will always be added parallel to that plane,
    #regardless of the active plane where the points are picked.
 
    plane = rs.WorldXYPlane()
 
    pdist = trad + tspace
 
    off = 0.0
 
    while (pdist <= plength - trad):
 
        #Place one row of tiles given distance along path
 
        # and possibly offset it
 
        pfirst = rs.Polar(sp, pangle, pdist)
 
        pctile = rs.Polar(pfirst, angp90, off)
 
        pltile = pctile
 
        while (rs.Distance(pfirst, pltile) < hwidth - trad):
 
            plane = rs.MovePlane(plane, pltile)
 
            rs.AddCircle (plane, trad)
 
            pltile = rs.Polar(pltile, angp90, tspace + trad + trad)
 
 
        pltile = rs.Polar(pctile, angm90, tspace + trad + trad)
 
        while (rs.Distance(pfirst, pltile) < hwidth - trad):
 
            plane = rs.MovePlane(plane, pltile)
 
            rs.AddCircle (plane, trad)
 
            pltile = rs.Polar(pltile, angm90, tspace + trad + trad)
 
        pdist = pdist + ((tspace + trad + trad) * Sin(math.radians(60)))
 
        if off == 0.0:
 
            off = (tspace + trad + trad) * Cos(math.radians(60))
 
        else:
 
            off = 0.0
 
 
 
 
 
 
if __name__ == "__main__":
 
    test()