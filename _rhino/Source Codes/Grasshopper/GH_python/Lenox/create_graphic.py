input_list = [("SkyMatrix", "Generic", "xxx."),
              ("CumulativeRadiationResult", "Numbers", "xxx."),
              ("CumulativeRadiationMesh", "Meshs", "xxx."),
              ("CumulativeRadiationMeshDensity", "Number", "xxx."),
              ("IsRun", "Boolean","xxxxxxxx")]
output_list = [("CumulativeRadiationGraphic", "Generics", "xxxxx"),
               ("CumulativeRadiationGraphicTitle", "Text", "xxxxx"),
               ("CumulativeRadiationLegend", "Generics", "xxxxx")]


basic_doc = """Create a EA standard graphic after the study is done
    
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

import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


from ladybug.graphic import GraphicContainer
from ladybug.legend import LegendParameters
from ladybug.color import Colorset
from ladybug_rhino.togeometry import to_joined_gridded_mesh3d
from ladybug_rhino.text import text_objects
from ladybug_rhino.fromobjects import legend_objects
############## main design below #######################

def create_legend_parameters(sky_matrix,result):
    legend_paras = LegendParameters()
   
    if hasattr(sky_matrix, 'benefit_matrix') and sky_matrix.benefit_matrix is not None:
        study_name = '{} Benefit/Harm'.format('Incident Radiation')
        if legend_paras.are_colors_default:
            legend_paras.colors = reversed(Colorset.benefit_harm())
        if legend_paras.min is None:
            legend_paras.min = min((min(result), -max(result)))
        if legend_paras.max is None:
            legend_paras.max = max((-min(result), max(result)))
            
    return legend_paras

def create_title(result):
    title = "Annual Solar Radiation Benefit\n"
    total = int(sum(result))
    title += "Net Solar Benefit Score = {} kWh/m2".format(total)
    return title
    
def main(sky_matrix, result, mesh, mesh_density, is_run):
    study_mesh = to_joined_gridded_mesh3d(mesh, mesh_density)
    graphic = GraphicContainer(result, study_mesh.min, study_mesh.max, create_legend_parameters(sky_matrix, result))
    graphic.legend_parameters.title = 'kWh/m2'
    
    
    title = text_objects(
        create_title(result), graphic.lower_title_location,
        graphic.legend_parameters.text_height * 1.5,
        graphic.legend_parameters.font)
    
    legend = legend_objects(graphic.legend)
    return graphic, title, legend


if _utility.is_all_input_valid(globals(), input_list):
    if IsRun:
        result = main(*para_inputs)
        ################ output below ######################
        globals().update(_utility.generate_para_outputs(globals(), output_list, result))
    else:
        print ("This script is not running.")
        
else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc