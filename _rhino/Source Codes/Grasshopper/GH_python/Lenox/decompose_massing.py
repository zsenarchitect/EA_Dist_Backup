input_list = [("Massings", "Breps", "Maasings as rooms or whole building"),
              ("ProjectNorth", "Vector", "a vector representing project north so facade NWSE makes sense")]
output_list = [("RoofsOrCeilings", "Srfs", "Roof or ceiling of the massing"),
               ("Floors", "Srfs", "Floors of the massing"),
               ("FacadeNorth", "Srfs", "North facade of the project"),
               ("FacadeWest", "Srfs", "West facade of the project"),
               ("FacadeSouth", "Srfs", "South facade of the project"),
               ("FacadeEast", "Srfs", "East facade of the project")]

basic_doc = """This will try to decompose input mass brep into roofs/ceilings, floors, walls facing NWSE direction in relation to a north vector"""

########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)
# default_value_map = _utility.generate_default_value_map()

# print dir(_utility)
# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))



################ input below ###########################

massings = Massings
north_vector = ProjectNorth

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Grasshopper
sc.doc = Grasshopper.Instances.ActiveCanvas.Document
import math
############## main design below #######################


def decompose(massing, north_vector):
    faces = massing.Faces
    z_vector = Rhino.Geometry.Vector3d(0,0,1)
    roof = None
    floor = None
    facade_w = None
    facade_e = None
    facade_s = None
    facade_n = None
    threshold = 10
    
    for face in faces:
        normal = face.NormalAt(0,0)
        if rs.VectorAngle(z_vector, normal) < threshold:
            roof = face.DuplicateFace(False)
        if rs.VectorAngle(z_vector, normal) > 180- threshold:
            floor = face.DuplicateFace(False)
            
            
        angle_NS =  rs.VectorAngle(normal, north_vector)
        angle_WE =  rs.VectorAngle(normal, rs.VectorRotate(north_vector, 90, [0,0,1]))
 
        
        # dot = vector1 * vector2
        # dot = rhutil.clamp(-1,1,dot)
        # radians = math.acos(dot)
        # angle =  math.degrees(radians)
        if 0-threshold < angle_NS < 0+threshold:
            facade_n = face.DuplicateFace(False)
        if 180-threshold< angle_NS < 180+threshold:
            facade_s = face.DuplicateFace(False)
            
            
        if 0-threshold< angle_WE < 0+threshold:
            facade_w = face.DuplicateFace(False)
        if 180-threshold< angle_WE < 180+threshold:
            facade_e = face.DuplicateFace(False)
        
    if roof == None:
        print ("cannot find top facing face.")
    if floor == None:
        print ("cannot find bottom facing face.")
    if facade_n == None:
        print ("cannot find north facing face.")
    if facade_w == None:
        print ("cannot find west facing face.")
    if facade_s == None:
        print("cannot find south facing face.")
    if facade_e == None:
        print("cannot find east facing face.")

    return roof, floor, facade_n, facade_w, facade_s, facade_e


if _utility.is_all_input_valid(globals(), input_list):
    results = [decompose(massing, north_vector) for massing in massings]
    # title = str(__file__)[-20:]
    # print rs.StringBox(title)

    # print results

    # when running in GH this is not the namescape
    # if __name__ == "__main__":


    ################ output below ######################
    RoofsOrCeilings = [result[0] for result in results]
    Floors = [result[1] for result in results]
    FacadeNorth = [result[2] for result in results]
    FacadeWest = [result[3] for result in results]
    FacadeSouth = [result[4] for result in results]
    FacadeEast = [result[5] for result in results]
else:
    print ("There are missing valid input")



sc.doc = Rhino.RhinoDoc.ActiveDoc