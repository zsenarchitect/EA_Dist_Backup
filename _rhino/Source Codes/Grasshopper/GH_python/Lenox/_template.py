input_list = [("Input_1", "Mesh", "xxx.")]
output_list = [("Output_1", "Boolean", "xxxxx")]


basic_doc = """xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
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


############## main design below #######################



def main(arg):
    print(arg)
    return True


if _utility.is_all_input_valid(globals(), input_list):
    result = main(*para_inputs)
    ################ output below ######################
    globals().update(_utility.generate_para_outputs(globals(), output_list, result))
    
    
else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc