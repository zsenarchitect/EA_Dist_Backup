input_list = [("LocationCrvs", "Curves", "The location crv for block to host on"),
              ("UnitWidth", "Number", "The unit width of the patteint room block")]
output_list = [("BlockTransforms", "Transforms", "The list of transforms for Inserted Blocks")]

basic_doc = """get block transforms along mutiple crvs. This method will try to map by having two pts touching the input crv. The effect is similar to the Rhino version create sample layout block."""

########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)

# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))

import sys
import os
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Grasshopper
sc.doc = Grasshopper.Instances.ActiveCanvas.Document
################ input below ###########################


guide_crvs = LocationCrvs
spacing = UnitWidth

############## main design below #######################


def get_transforms(crv, spacing):
 
    pts_on_seg = rs.DivideCurveEquidistant(crv, spacing)

    out_blocks = []

    
    for i in range(len(pts_on_seg) - 1):
        x0 = pts_on_seg[i]
        x1 = pts_on_seg[i + 1]
        param = rs.CurveClosestPoint(crv, x0)
        tangent = rs.CurveTangent(crv, param)
     
        side_vector = rs.VectorRotate(tangent, 90, [0,0,1])
       
        directional_ref_temp = x0 + side_vector
       
       
  
      
        local_plane = Rhino.Geometry.Plane(x0, x1, directional_ref_temp)
        out_blocks.append(local_plane)
        
        

    return out_blocks
   
    
  
transforms = [get_transforms(guide_crv, spacing) for guide_crv in guide_crvs]
transforms = EnneadTab.RHINO.RHINO_CLEANUP.flatten_list(transforms)

################ output below ######################
BlockTransforms = transforms


sc.doc = Rhino.RhinoDoc.ActiveDoc