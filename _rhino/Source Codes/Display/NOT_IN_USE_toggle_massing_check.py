import re
import Rhino # pyright: ignore
import System # pyright: ignore.Drawing
import scriptcontext as sc
import rhinoscriptsyntax as rs
import sys
sys.path.append("..\lib")
import EA_UTILITY as EA
import EnneadTab
import traceback
####################### below are new thing#######
def try_catch_error(func):
    import traceback
    def wrapper(*args, **kwargs):

        
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
           
            return out
        except Exception as e:
            print ( str(e))
           
            error = traceback.format_exc()
            error_file = "{}\error_log.txt".format(EnneadTab.FOLDER.get_user_folder())
            with open(error_file, "w") as f:
                f.write(error)
            EnneadTab.EXE.open_file_in_default_application(error_file)
    return wrapper


class EA_GFA_Conduit(Rhino.Display.DisplayConduit):
    def __init__(self):

        self.data = []
        sc.sticky["EA_GFA_IS_BAKING"] = False

    #@try_catch_error
    def PostDrawObjects(self, e):
        #debug



        self.data = [(x, get_area_and_crv_geo_from_layer(x))   for x in get_schedule_layers()]
        #print "start post draw"

        for data in self.data:
            layer, values = data
            area, joined_crvs, faces = values
            #print values
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
            for face in faces:
                #print face
                area = Rhino.Geometry.AreaMassProperties.Compute(face).Area
                #print area
                text = convert_area_to_good_unit(area)
                #print text
                pt3D = Rhino.Geometry.AreaMassProperties.Compute(face).Centroid
                #print pt3D
                e.Display.DrawDot(pt3D, text, color, System.Drawing.Color.White)# dot color and text color
                #print "dot finish"
        #print "finish post draw"
        """
        ideas:
        get live length dimension on selected massing. e.display.DrawAnnotation
        """


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
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 35)
        e.Display.Draw2dText("Including bracket [GFA] in layer name to allow scheduling.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Right click toggle button to bake data to Excel.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Accepting single surface(Z+ or Z- normal) and polysurface(open or enclosed, only check the face with Z- normal). ", color, pt, False, 10)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 15)
        e.Display.Draw2dText("Area unit converted to SQM for mm unit. Area unit converted to SQFT for inches unit.", color, pt, False, 10)


        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 30)
        size = 20
        offset = 20

        grand_total = 0
        #sub_title = "X" * 10
        #sub_total = 0
        for data in self.data:

            layer, values = data

            """
            parent_layer = rs.ParentLayer(layer)
            if sub_title != parent_layer:
                if sub_title != "X" * 10:
                    text = "Sub Total for {}: {}".format(parent_layer, convert_area_to_good_unit(sub_total))
                    pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
                    color = rs.CreateColor([87, 85, 83])
                    e.Display.Draw2dText(text, color, pt, False, size)

                sub_total = 0
                sub_title = parent_layer
            """

            area = values[0]
            if area == 0:
                continue

            grand_total += area
            #sub_total += area

            text = "{}: {}".format(layer, convert_area_to_good_unit(area))
            pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
            color = rs.LayerColor(layer)
            e.Display.Draw2dText(text, color, pt, False, size)


            # draw curve from crv geo

        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 40)
        color = rs.CreateColor([87, 85, 83])
        #print "C"
        pt0 = System.Drawing.Point(pt[0], pt[1] )
        pt1 = System.Drawing.Point(pt[0] + 500, pt[1] )
        #print "A"
        e.Display.Draw2dLine(pt0, pt1, color, 5)
        #print "B"
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 10)
        text = "Grand Total Area: {}".format(convert_area_to_good_unit(grand_total))
        e.Display.Draw2dText(text, color, pt, False, 30)
        #print "drawingsssss finish"




        #print "Done"
        #True = text center around thge define pt, Flase = lower-left
        if sc.sticky["EA_GFA_IS_BAKING"]:
            import bake_toggle_massing_check
            data_collection = []
            for i, data in enumerate(self.data):
                layer, values = data
                area = convert_area_to_good_unit(values[0])
                #print area
                area_num, area_unit = area.split(" ", maxsplit = 1)
                #print area_num
                cell_layer = bake_toggle_massing_check.DataItem(layer, i, 0)
                cell_area = bake_toggle_massing_check.DataItem(float(area_num), i, 1)
                cell_unit = bake_toggle_massing_check.DataItem(area_unit, i, 2)
                data_collection.append(cell_layer)
                data_collection.append(cell_area)
                data_collection.append(cell_unit)
            bake_toggle_massing_check.bake_action(data_collection)
            sc.sticky["EA_GFA_IS_BAKING"] = False





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
            return 1.0/(1000 * 1000), "SQM"
        if unit == "meter":
            return 1.0, "SQM"
        if unit == "inch":
            return 1.0/(12 * 12), "SQFT"
        if unit == "foot":
            return 1.0, "SQFT"
        return -1, "{0} x {0}".format(unit)
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
    objs = filter(lambda x: rs.IsPolysurface(x) or rs.IsSurface(x), objs)
    #print objs
    sum_area = 0
    crvs = []
    out_faces = []
    for obj in objs:


        #print "is polysurf"
        #prepare for the 2nd version to be faster
        brep = rs.coercebrep(obj)
        faces = brep.Faces

        is_single_face = False
        if faces.Count == 1:
            is_single_face = True

        for face in faces:
            #print face
            if is_facing_down(face, allow_facing_up = is_single_face):
                #print "get down face"

                sum_area += Rhino.Geometry.AreaMassProperties.Compute(face).Area

                #get crv geo but not add to doc
                crv_geo = get_crv_geo_from_surface(brep, face)

                crvs.extend(crv_geo)

                #face_geo = get_face_geo_from_face(brep, face)
                #print 123
                #print face
                #print face_geo
                #print 321
                out_faces.append(face)





    return sum_area, crvs, out_faces

def get_face_geo_from_face(brep, face):
    face_id = face.SurfaceIndex
    #print face_id
    surf = brep.Faces.ExtractFace(face_id)
    #print surf
    return surf


def get_crv_geo_from_surface(brep, face):
    edge_ids = face.AdjacentEdges()
    #print edge_ids
    #print brep.Edges
    edges = [brep.Edges[x].EdgeCurve for x in list(edge_ids)]
    #print edges
    tolerance = sc.doc.ModelAbsoluteTolerance * 2.1
    joined_crvs = Rhino.Geometry.Curve.JoinCurves(edges, tolerance)
    return  joined_crvs

def is_facing_down(face, allow_facing_up = False):
    param = rs.SurfaceClosestPoint(face, EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(face))
    normal = rs.SurfaceNormal(face, param)
    #print normal
    Z_down = [0,0,-1]
    #print rs.VectorAngle(normal, Z_down)
    #print rs.VectorCrossProduct(normal, Z_down)
    t = 0.001

    # make quick check for upfacing single surface
    if allow_facing_up:
        Z_up = [0,0,1]
        if -t < rs.VectorAngle(normal, Z_up) < t:
            return True

    if -t < rs.VectorAngle(normal, Z_down) < t:
        return True
    #if rs.VectorCrossProduct(normal, Z_down) < 0:
        #return False
    return False


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
    ideas:
    right click to set desired GFA to each layer name, save to external text. and live compare how much is off from target.
    """
