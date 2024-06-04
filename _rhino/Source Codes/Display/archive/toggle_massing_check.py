import re
import Rhino # pyright: ignore
import System # pyright: ignore
import scriptcontext as sc
import rhinoscriptsyntax as rs
import sys
sys.path.append("..\lib")
import EnneadTab
####################### below are new thing#######

class EA_GFA_Conduit(Rhino.Display.DisplayConduit):
    def DrawForeground(self, e):
        text = "Ennead GFA Schedule Mode"
        color = rs.CreateColor([87, 85, 83])
        #color = System.Drawing.Color.Red
        position_X_offset = 20
        position_Y_offset = 40
        size = 40
        bounds = e.Viewport.Bounds
        pt = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        e.Display.Draw2dText(text, color, pt, False, size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 30)
        e.Display.Draw2dText("Including bracket [GFA] in layer name to allow scheduling.", color, pt, False, 20)


        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 30)
        size = 20
        offset = 20

        for layer in get_schedule_layers():
            area, crv_geos = get_area_and_crv_geo_from_layer(layer)
            if area == 0:
                continue

            text = "{}: {}".format(layer, convert_area_to_good_unit(area))
            pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
            color = rs.LayerColor(layer)
            e.Display.Draw2dText(text, color, pt, False, size)
            # draw curve from crv geo




        #print "Done"
        #True = text center around thge define pt, Flase = lower-left


    def PostDrawObjects(self, e):
        #print "start post draw"
        for layer in get_schedule_layers():
            area, joined_crvs = get_area_and_crv_geo_from_layer(layer)
            color = rs.LayerColor(layer)
            thickness = 10
            #print crv_geos
            for crv_geo in joined_crvs:
                #print crv_geo
                #print color
                #print thickness

                for crv in crv_geo.DuplicateSegments():
                    #print crv
                    e.Display.DrawCurve(crv, color, thickness)

            #print "start to dot"
            #tolerance = sc.doc.ModelAbsoluteTolerance * 2.1
            #print tolerance
            #joined_crvs = Rhino.Geometry.Curve.JoinCurves(crv_geos, tolerance)
            #print joined_crvs
            for closed_crv in joined_crvs:
                #print closed_crv
                area = Rhino.Geometry.AreaMassProperties.Compute(closed_crv).Area
                #print area
                text = convert_area_to_good_unit(area)
                #print text
                pt3D = Rhino.Geometry.AreaMassProperties.Compute(closed_crv).Centroid
                #print pt3D
                e.Display.DrawDot(pt3D, text, color, System.Drawing.Color.White)# dot color and text color
                #print "dot finish"
        #print "finish post draw"


def get_schedule_layers():
    #print "geting good layers"
    layers = sorted(rs.LayerNames())
    good_layers = filter(lambda x:"[GFA]" in x, layers)
    #print good_layers
    return good_layers

    pass


def convert_area_to_good_unit(area):
    # only provide sqm or sqft, depeding on which system it is using. mm and m -->sqm, in, ft -->sqft

    unit = rs.UnitSystemName(capitalize=False, singular=True, abbreviate=False, model_units=True)

    def get_factor(unit):
        if unit == "millimeter":
            return 1.0/(1000 * 1000), " SQM"
        if unit == "meter":
            return 1.0, " SQM"
        if unit == "inch":
            return 1.0/(12 * 12), " SQFT"
        if unit == "foot":
            return 1.0, " SQFT"
        return -1, "{0}x{0}".format(unit)
    factor, unit_text = get_factor(unit)
    if factor < 0:
        return "{:.2f} {}".format(area, unit_text)


    area *= factor
    return "{:.2f} {}".format(area, unit_text)
    pass


def process_polysrf(obj):

    return

def get_area_and_crv_geo_from_layer(layer):
    objs = rs.ObjectsByLayer(layer)
    sum_area = 0
    crvs = []
    for obj in objs:
        """
        ideas: research corce breo so it can take polysurf and extrusion and surface seperately. Need its own version
        """
        if rs.IsPolysurface(obj):
            #print "is polysurf"
            """ prepare for the 2nd version to be faster
            faces = rs.coercebrep(obj).Faces


            brep = rhutil.coercebrep(id, True)
        if brep.Faces.Count>1:
            for i in range(brep.Faces.Count):
                copyface = brep.Faces[i].DuplicateFace(False)---->copy face



            for face in faces:
                if is_facing_down(face):
                    sum_area += Rhino.Geometry.AreaMassProperties.Compute(face).Area

                    #get crv geo but not add to doc
                    crv_geo = get_crv_geo_from_surface(face)
                    crvs.extend(crv_geo)
            continue
            """


            faces = rs.ExplodePolysurfaces(obj)
            for face in faces:
                if is_facing_down(face):
                    sum_area += rs.Area(face)

                    #get crv geo but not add to doc
                    crv_geo = get_crv_geo_from_surface(face)
                    crvs.extend(crv_geo)

            rs.DeleteObjects(faces)
            continue




        if rs.IsSurface(obj):
            #print "is surface"
            sum_area += rs.Area(obj)
            #get crv geo but not add to doc
            crv_geo = get_crv_geo_from_surface(face)
            crvs.extend(crv_geo)
            continue



    return sum_area, crvs
    pass


def get_crv_geo_from_surface(id):
    brep = rs.coercebrep(id)
    solo_crvs = brep.DuplicateNakedEdgeCurves(True, True)# both true for outer edge and inner edge

    tolerance = sc.doc.ModelAbsoluteTolerance * 2.1
    joined_crvs = Rhino.Geometry.Curve.JoinCurves(solo_crvs, tolerance)
    return  joined_crvs

def is_facing_down(face):
    param = rs.SurfaceClosestPoint(face, EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(face))
    normal = rs.SurfaceNormal(face, param)
    #print normal
    Z_down = [0,0,-1]
    #print rs.VectorAngle(normal, Z_down)
    #print rs.VectorCrossProduct(normal, Z_down)
    t = 0.001
    if -t < rs.VectorAngle(normal, Z_down) < t:
        return True
    #if rs.VectorCrossProduct(normal, Z_down) < 0:
        #return False
    return False

@EnneadTab.ERROR_HANDLE.try_catch_error
def toggle_GFA_display():


    conduit = None
    key = "EA_GFA_display_conduit"
    if sc.sticky.has_key(key):
        conduit = sc.sticky[key]
    else:
        # create a conduit and place it in sticky
        conduit = EA_GFA_Conduit()
        sc.sticky[key] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled: print "conduit enabled"
    else: print "conduit disabled"
    sc.doc.Views.Redraw()

    print("Tool Finished")






def testing():
    rs.EnableRedraw(False)
    for layer in  get_schedule_layers():
        area, crvs = get_area_and_crv_geo_from_layer(layer)
        if area == 0:
            continue
        print("#")
        text = convert_area_to_good_unit(area)

        color = rs.LayerColor(layer)
        print(text)
        print(color)


if __name__=="__main__":
    #showinscript()
    #showafterscript()
    toggle_GFA_display()
    #testing()




    """
    for block color , the text want to be many lines, each line is block name and display as the color


    need a way to keep setting in system after script finish, so the conduit keep
    """
