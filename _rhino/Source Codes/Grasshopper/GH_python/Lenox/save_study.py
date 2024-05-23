input_list = [("CumulativeRadiationHourOfYear", "Numbers", "xxxxxxxxx"),
              ("CumulativeRadiationMesh", "Mesh", "xxx."),
              ("CumulativeRadiationMeshDensity", "Number", "xxx."),
              ("CumulativeRadiationResult", "Numbers", "xxx."),
              ("CumulativeRadiationGraphic", "Generics", "xxxxxxxxx")]
output_list = [("IsSaved", "Boolean", "xxxxx")]


basic_doc = """Save all the important data in Ennead system so it can be retreived later.
    
"""


########################################### internal setup
import _utility

# reload(_utility)
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)

# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))

# print _utility.get_input_names(input_list)
para_inputs = _utility.generate_para_inputs(globals(),input_list)
# para_inputs = [globals()[x] for x in _utility.get_input_names(input_list)]
# print para_inputs
################ input below ###########################



import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Grasshopper
sc.doc = Grasshopper.Instances.ActiveCanvas.Document

try:
    import ladybug_rhino
except:
    print("ladybug is not installed properly.")

import os
import sys
import traceback
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)



############## main design below #######################

def rhino_geo_to_json(mesh_geos):
    if not isinstance(mesh_geos, list):
        mesh_geos = [mesh_geos]
    
    
    serialization_option = Rhino.FileIO.SerializationOptions ()

    
    
    data = dict()
    for i, mesh_geo in enumerate(mesh_geos):

        local_data = dict()
        
        # mesh_geo = rs.coercemesh(mesh_geo)
        if not isinstance(mesh_geo, Rhino.Geometry.Mesh):
            note = "Please set the CumulativeRadiationMesh type hint as Mesh or NoHint"
            EnneadTab.NOTIFICATION.messenger(main_text = note)
            print(note)
            continue
        
        # print Grasshopper.Instances.ActiveCanvas.Document
        # print type(Grasshopper.Instances.ActiveCanvas.Document)
        # mesh_geo = Grasshopper.Instances.ActiveCanvas.Document.FindObject(mesh_geo, False)
        # print mesh_geo
        local_data["geo_json"] = mesh_geo.ToJSON(serialization_option)
        data[i] = local_data
    return data



def text3d_to_json(text3d):
    # print type(text3d)
    json_text3d = {}
    text_entity = Rhino.Geometry.TextEntity()
    text_entity.PlainText = text3d.Text
    text_entity.Plane = text3d.TextPlane
    text_entity.TextHeight = text3d.Height
    serialization_option = Rhino.FileIO.SerializationOptions ()
    json_text3d["text_entity"] = text_entity.ToJSON(serialization_option)
    
    
    # temp_font = Rhino.DocObjects.Font("temp_font",
    #                                   weight = 7,# 7 is Bold enumnarete
    #                                 style = 2,
    #                                 underlined = False,
    #                                 strikethrough = False)
    # text.Font = 
    json_text3d["is_bold"] = text3d.Bold
    json_text3d["is_italic"] = text3d.Italic
    json_text3d["font_face"] = text3d.FontFace

    return json_text3d



def process_legend(legend_data):
    data = []
    for item in legend_data:
        # print item
        # print type(item)
        if isinstance(item, Rhino.Geometry.Mesh):
            data.append(rhino_geo_to_json(item)) 
        else:
            # print type(item)
            # text3d is a display object, not a geometry object
            text3d = item.m_value
            json_text3d = text3d_to_json(text3d)
            data.append(json_text3d)
    return data

def main(hour_of_year, mesh, mesh_density, simulation_data,  graphic):
    try:
        data = {}
        
        data["mesh"] = rhino_geo_to_json(mesh)
        data["mesh_density"] = mesh_density
        data["simulation_data"] = simulation_data
        
        data["hour_of_year"] = hour_of_year
        data["graphic"] = graphic.to_dict()
        data["creator"] = EnneadTab.USER.get_user_name()
        data["creation_date"] = EnneadTab.TIME.get_formatted_current_time()
        study_name = _utility.create_valid_study_name()
        if not study_name:
            return False
        _utility.save_study_data(study_name,
                                data)
        
        EnneadTab.NOTIFICATION.messenger(main_text = "Study saved successfully")
        return True
    except:
        EnneadTab.NOTIFICATION.messenger(main_text = "Study fail to save")
        print(traceback.format_exc())
        return False


if _utility.is_all_input_valid(globals(), input_list):
    
    result = main(*para_inputs)
    ################ output below ######################
    globals().update(_utility.generate_para_outputs(globals(), output_list, result))
    
    
else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc