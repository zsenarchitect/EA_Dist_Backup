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

        #print ("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            #print ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            print ( str(e))
            #print (  "Wrapper func for EA Log -- Error: " + str(e)  )
            error = traceback.format_exc()
            print(error)
            """
            error_file = "{}\error_log.txt".format(EnneadTab.FOLDER.get_user_folder())
            with open(error_file, "w") as f:
                f.write(error)
            EnneadTab.EXE.open_file_in_default_application(error_file)
            """
    return wrapper


class EA_GFA_Conduit(Rhino.Display.DisplayConduit):
    def __init__(self):

        self.data = []
        sc.sticky["EA_GFA_IS_BAKING"] = False

    @try_catch_error
    def PostDrawObjects(self, e):
        #debug



        self.data = [(x, get_area_and_crv_geo_from_layer(x))   for x in get_schedule_layers()]
        #print "start post draw"

        for data in self.data:
            layer, values = data
            area, edges, faces, note = values




            #print values
            color = rs.LayerColor(layer)
            thickness = 10
            #print crv_geos
            """
            for crv_geo in joined_crvs:
                #print crv_geo
                #print color
                #print thickness

                for crv in crv_geo.DuplicateSegments():
                    #print crv
                    e.Display.DrawCurve(crv, color, thickness)
            """

            for edge in edges:
                e.Display.DrawCurve(edge, color, thickness)
            #print "start to dot"
            #tolerance = sc.doc.ModelAbsoluteTolerance * 2.1
            #print tolerance
            #joined_crvs = Rhino.Geometry.Curve.JoinCurves(crv_geos, tolerance)
            #print joined_crvs
            for face in faces:
                #print face
                abstract_face = Rhino.Geometry.AreaMassProperties.Compute(face)
                if abstract_face:
                    area = abstract_face.Area
                    #print area
                    text = convert_area_to_good_unit(area)
                    
                    factor =  self.layer_factor(layer)
                    if factor != 1:
                        text = text + " x {} = {}".format(factor, convert_area_to_good_unit(area * factor))
                    
                    #print text
                    pt3D = Rhino.Geometry.AreaMassProperties.Compute(face).Centroid
                    #print pt3D
                    e.Display.DrawDot(pt3D, text, color, System.Drawing.Color.White)# dot color and text color
                    #print "dot finish"
                else:
                    print("!!! Check for geo cleanness in layer: " + layer)
        #print "finish post draw"
        """
        ideas:
        get live length dimension on selected massing. e.display.DrawAnnotation
        """

    def layer_factor(self, layer):
        # if layer name contain syntax such as 'abcd{0.5}' or 'xyz{0}', extract 0.5 and 0 as the factor.
        # if no curly bracket is found, return 1.
        pattern = re.compile(r".*{(.*)}")
        match = pattern.search(layer)
        if match:
            try:
                return float(match.group(1))
            except:
                return 1
        return 1
    
    @try_catch_error
    def DrawForeground(self, e):
        text = "Ennead GFA Schedule Mode"
        color = rs.CreateColor([87, 85, 83])
        color_hightlight = rs.CreateColor([150, 85, 83])
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
        e.Display.Draw2dText("Including curly bracket {factor} at end of layer name to allow factor multiply, such as {0.5} or {0}.", color_hightlight, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Right click toggle button to bake data to Excel and/or generate checking srf.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("The generated checking srf will also show area text dot but will not be exported to Excel.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("For clarity reason, the generated checking srf layer will be purged.", color, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 35)
        e.Display.Draw2dText("Area unit auto-mapped from your Rhino unit: mm--> SQM, m--> SQM, inch--> SQFT, ft--> SQFT", color_hightlight, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Areas from same layer will try to merge dynamically if on same elevation.", color_hightlight, pt, False, 20)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 25)
        e.Display.Draw2dText("Accepting single surface(Z+ or Z- normal) and polysurface(open or enclosed, only check the face with Z- normal). ", color, pt, False, 10)


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
            note = values[3]
            #print note
            if area == 0:
                continue
            
            factor =  self.layer_factor(layer)
            if factor != 1:
                area *= factor

            grand_total += area
            #sub_total += area

            text = "{}: {}".format(EnneadTab.RHINO.RHINO_LAYER.rhino_layer_to_user_layer(layer), convert_area_to_good_unit(area))
            if note:
                text += note
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

        root_layer = "GFA Internal Check Srfs"

        if "EA_GFA_IS_BAKING_EXCEL" not in sc.sticky:
            sc.sticky["EA_GFA_IS_BAKING_EXCEL"] = False
        
        if sc.sticky["EA_GFA_IS_BAKING_EXCEL"]:
            import bake_toggle_massing_check
            data_collection = []
            i = 0
            for data in self.data:
                layer, values = data
                if root_layer in layer:
                    continue
                area = values[0]
                if area == 0:
                    continue

                factor =  self.layer_factor(layer)
                if factor != 1:
                    area *= factor
                area = convert_area_to_good_unit(area, use_commas = False)
                #print area
                area_num, area_unit = area.split(" ", maxsplit = 1)
                #print area_num
                layer = EnneadTab.RHINO.RHINO_LAYER.rhino_layer_to_user_layer(layer)
                cell_layer = bake_toggle_massing_check.DataItem(layer, i, 0)
                cell_area = bake_toggle_massing_check.DataItem(float(area_num), i, 1)
                cell_unit = bake_toggle_massing_check.DataItem(area_unit, i, 2)
                data_collection.append(cell_layer)
                data_collection.append(cell_area)
                data_collection.append(cell_unit)
                i += 1

            bake_toggle_massing_check.bake_action(data_collection)
            sc.sticky["EA_GFA_IS_BAKING_EXCEL"] = False
            

        if "EA_GFA_IS_BAKING_CRV" not in sc.sticky:
            sc.sticky["EA_GFA_IS_BAKING_CRV"] = False
        if sc.sticky["EA_GFA_IS_BAKING_CRV"]:
            if rs.IsLayer(root_layer):
                purge_layer_and_sub_layers(root_layer)
            for data in self.data:
                layer, values = data
                if root_layer in layer:
                    continue
                if values[0] == 0:
                    continue


                area, edges, faces, note = values
                color = rs.LayerColor(layer)
            
                #attr = sc.doc.ObjectAttributes()
                #attr.LayerIndex

                
                
                data_layer = secure_layer("{}::{}".format(root_layer, layer))

                rs.LayerColor(data_layer, color)
                #rs.DeleteObjects(rs.ObjectsByLayer(data_layer))
                shapes = [sc.doc.Objects.AddBrep(face) for face in faces]
                rs.ObjectLayer(shapes, data_layer)



            sc.sticky["EA_GFA_IS_BAKING_CRV"] = False
            sc.doc.Views.Redraw()


def secure_layer(layer):
    if not rs.IsLayer(layer):
        rs.AddLayer(layer)
    return layer


def purge_layer_and_sub_layers(root_layer):
    if 0 != rs.LayerChildCount(root_layer):

        for layer in rs.LayerChildren(root_layer):
            purge_layer_and_sub_layers(layer)


    rs.PurgeLayer(root_layer)
    return
    

def merge_coplaner_srf(breps):
    #print breps
    for brep in breps:
        param = rs.SurfaceClosestPoint(brep, EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(brep))
        normal = rs.SurfaceNormal(brep, param)
        if normal[2] < 0:
            brep.Flip()

    union_breps = Rhino.Geometry.Brep.CreateBooleanUnion (breps, sc.doc.ModelAbsoluteTolerance * 1.5)
    if not union_breps:
        note = " #Warning! Check your geometry cleanness."
        return breps, note
    #print breps
    for brep in union_breps:
        brep.MergeCoplanarFaces (sc.doc.ModelAbsoluteTolerance ,
                                sc.doc.ModelAngleToleranceRadians * 1.5)
    return union_breps, None

def get_merged_data(faces):
    height_dict = dict()
    for face in faces:
        face = face.DuplicateFace (False)# this step turn brepface to brep
        z = rs.SurfaceAreaCentroid(face)[0][2]

        """
        need to put all 'similar' height to same key
        """
        for h_key in height_dict.keys():
            if abs(h_key - z) < sc.doc.ModelAbsoluteTolerance * 1.5:
                height_dict[h_key].append(face)
                break
        else:
            h_key = z
            height_dict[h_key] = [face]

        """
        if height_dict.has_key(h_key):
            height_dict[h_key].append(face)
        else:
            height_dict[h_key] = [face]
        """
    main_note = None
    for h_key, faces in height_dict.items():
        #faces = [brepface_to_brep(x) for x in faces]
        #height_dict[h_key] = merge_coplaner_srf(rs.BooleanUnion(faces, delete_input = False))
        faces, note = merge_coplaner_srf(faces)
        if note:
            main_note = note
        height_dict[h_key] = faces

    out_faces = []
    for faces in height_dict.values():
        out_faces.extend(faces)
    sum = 0
    out_crvs = []
    for face in out_faces:
        abstract_face = Rhino.Geometry.AreaMassProperties.Compute(face)
        if abstract_face:
            sum += abstract_face.Area
        else:
            main_note = " #Warning!! Check your geometry cleanness."
        out_crvs.extend(face.Edges )


    return sum, out_crvs, out_faces, main_note


def get_schedule_layers():
    #print "geting good layers"
    layers = sorted(rs.LayerNames())

    def is_good_layer(x):
        
        if not "[GFA]" in x:
            return False
        if not rs.IsLayerVisible(x):
            return False
        return True
    good_layers = filter(is_good_layer, layers)

    #print good_layers
    return good_layers

    pass


#"{:,}".format(total_amount)
# "Total cost is: ${:,.2f}".format(total_amount)
# Total cost is: $10,000.00
def convert_area_to_good_unit(area, use_commas = True):
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
        return 1, "{0} x {0}".format(unit)
    factor, unit_text = get_factor(unit)

    area *= factor
    if use_commas:
        return "{:,.2f} {}".format(area, unit_text)
    else:
        return "{:.2f} {}".format(area, unit_text)
    pass


def process_polysrf(obj):

    return

def get_area_and_crv_geo_from_layer(layer):
    def is_good_obj(x):
        if not (rs.IsPolysurface(x) or rs.IsSurface(x)):
            return False
        if rs.IsObjectHidden(x):
            return False
        return True
    objs = rs.ObjectsByLayer(layer)
    objs = filter(is_good_obj , objs)

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




    sum_area, edges, faces, note = get_merged_data(out_faces)

    return sum_area, edges, faces, note


def brepface_to_brep(face):
    face_id = face.SurfaceIndex
    #print face_id
    brep = face.Brep
    surf = brep.Faces.ExtractFace(face_id)
    #print surf
    return surf

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
    ideas:
    right click to set desired GFA to each layer name, save to external text. and live compare how much is off from target.
    """
