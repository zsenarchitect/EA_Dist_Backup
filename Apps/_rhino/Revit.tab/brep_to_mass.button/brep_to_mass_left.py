
__title__ = "BrepToMass"
__doc__ = "Using faces of the brep to recreate a freeform mass in Revit."


import Rhino # pyright: ignore
import scriptcontext as sc
import rhinoscriptsyntax as rs

from EnneadTab import SOUND, DATA_FILE, NOTIFICATION, FOLDER
from EnneadTab import LOG, ERROR_HANDLE

def process_brep(brep):

    brep = sc.doc.Objects.Find(brep).Geometry

    faces = brep.Faces

    out = dict()
    for i, face in enumerate(faces):

        temp_brep = face.DuplicateFace (False)
       

        tol = sc.doc.ModelAbsoluteTolerance
        ang_tol = sc.doc.ModelAngleToleranceRadians

        joined_crvs = Rhino.Geometry.Curve.JoinCurves( temp_brep.Edges, tol)
        
        ##### this skipp any hole it might have
        outter_crv = sorted(joined_crvs, key = lambda x: x.GetLength())[-1]



        pts = outter_crv.Simplify (Rhino.Geometry.CurveSimplifyOptions.All, tol, ang_tol).ToNurbsCurve ().GrevillePoints()

        # pts = temp_brep.Vertices
        for pt in pts:
            print (pt)
        out[i] = [[x[0], x[1], x[2]] for x in pts]
        continue
    
    return out


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def brep_to_mass():
    breps = rs.GetObjects("Select object to export")
    if not breps:
        NOTIFICATION.messenger("No object selected")
        return
    rs.EnableRedraw(False)

    def good_brep(id):
        if rs.ObjectType(id) == 8:
            return True
        if rs.ObjectType(id) == 16:
            return True
        return False
        
    breps = filter(good_brep, breps)

    out = dict()
    for brep in breps:
        data = process_brep(brep)
        if data:
            out[brep.ToString()] = data
    

    file = FOLDER.get_EA_dump_folder_file("BREP2MASS_DATA.sexyDuck")
    DATA_FILE.set_data(out, file)

    SOUND.play_sound("sound_effect_mario_message.wav")




if __name__ == "__main__":
    brep_to_mass()