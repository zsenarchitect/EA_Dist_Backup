input_list = [("IsRun", "Boolean", "xxx.")]
output_list  = [("Creator", "String", "xxx."),
                ("CreationDate", "String", "xxx."),
                ("CumulativeRadiationHourOfYear", "Numbers", "xxxxxxxxx"),
                ("CumulativeRadiationMesh", "Mesh", "xxx."),
                ("CumulativeRadiationMeshDensity", "Number", "xxx."),
              ("CumulativeRadiationResult", "Numbers", "xxx."),
              ("CumulativeRadiationLegend", "Generics", "xxxxxxxxx"),
               ("CumulativeRadiationGraphic", "Generics", "xxxxxxxxx")]


basic_doc = """Load from previous study
    
"""


########################################### internal setup
import _utility


__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)

# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))


para_inputs = _utility.generate_para_inputs(globals(),input_list)

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

from ladybug.graphic import GraphicContainer
from ladybug_rhino.fromobjects import legend_objects
############## main design below #######################

def json_to_rhino_geo(mesh_data):
    if not mesh_data:
        return []
    
    
    # print type(mesh_data)
    out = []
    
    
    for value in mesh_data.values():
        # print value
        raw_json = value["geo_json"]
        geo_abstract = Rhino.Runtime.CommonObject.FromJSON(raw_json)
        # print geo_abstract
        out.append(geo_abstract)
        
    return out

def json_to_text3d(text3d_data):
    text_entity = Rhino.Runtime.CommonObject.FromJSON(text3d_data["text_entity"])
    text3d = Rhino.Display.Text3d(text_entity.PlainText, text_entity.Plane, text_entity.TextHeight)
    text3d.Bold = text3d_data["is_bold"]
    text3d.Italic = text3d_data["is_italic"]
    text3d.FontFace = text3d_data["font_face"]
    return text3d

def process_legend(legend_data):
    if not legend_data:
        return []
    
    out = []
    for i,item in enumerate(legend_data):
        # print item
        # print type(item)
        if i == 0:
            obj = json_to_rhino_geo(item)[0]
        else:
            
            text3d = json_to_text3d(item)
            obj = ladybug_rhino.text.TextGoo(text3d)
        out.append(obj)
    
    return out




def main(study_name = None):
    if study_name is None:
        study_list = [x.split(".json")[0] for x in os.listdir("L:\\4b_Applied Computing\\03_Rhino\\22_HB_Study")]
        
        
        selected_study = EnneadTab.RHINO.RHINO_FORMS.select_from_list(study_list,
                                                                message = "Pick from existing environment study",
                                                                multi_select = False)
        if not selected_study:
            return None, None, None, None, None
    
    else:
        selected_study = study_name
    
    data = _utility.load_study_data(selected_study)
    
    mesh = json_to_rhino_geo(data.get("mesh",None))
    mesh_density = data.get("mesh_density",None)
    simulation_data = data.get("simulation_data",None)
    # legend_data = process_legend(data.get("legend_data", None))
    # print mesh
    # print "################"
    # print len(simulation_data)
    # print "################"
    # print legend_data
    creator = data.get("creator", None)
    creation_date = data.get("creation_date", None)
    hour_of_year = data.get("hour_of_year", None)
    graphic_data = data.get("graphic", None)
    if graphic_data:
        graphic = GraphicContainer.from_dict(graphic_data)
        legend_data = legend_objects(graphic.legend)
    else:
        graphic = None
        legend_data = None
        
    return creator, creation_date, hour_of_year, mesh, mesh_density, simulation_data, legend_data, graphic
   


if _utility.is_all_input_valid(globals(), input_list) and IsRun:
    if IsRun:
        result = main()

        ################ output below ######################
        globals().update(_utility.generate_para_outputs(globals(), output_list, result))
        
    else:
        print ("This script is not running.")
else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc