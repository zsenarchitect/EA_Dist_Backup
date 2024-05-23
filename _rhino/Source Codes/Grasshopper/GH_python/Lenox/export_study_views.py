input_list = [("StudyNames", "Strings", "xxx."),
              ("CameraNames", "Strings", "xxx."),
              ("ImageFolder", "String", "xxx."),
              ("IsRun", "Boolean","xxxxxxxx")]
output_list = [("IsFinished", "Boolean", "xxxxx")]


basic_doc = """Use the study names and camera names, export high resolution image to a folder.
    
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

import load_study


############## main design below #######################

def set_active_view_to_saved_camera(camera_name):
    view_index = Rhino.RhinoDoc.ActiveDoc.NamedViews.FindByName(camera_name)
    view_info = Rhino.RhinoDoc.ActiveDoc.NamedViews[view_index]
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.MainViewport.PushViewInfo(view_info, False)
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()

def main(study_names, camera_names, output_folder, is_run):

    
    for study_name in study_names:
        load_study.main(study_name)
        for camera_name in camera_names:
            set_active_view_to_saved_camera(camera_name)
            
            
            file_path = "{}\{}_{}.png".format(output_folder, study_name, camera_name)
            
            rs.Command("-ViewCaptureToFile  \"{}\"  Enter".format(file_path))
   
    return True


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