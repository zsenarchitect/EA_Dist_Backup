input_list = [("UnitBlockName", "String", "the design option name of the block"),
              ("LocationCrvs", "Curves", "The location crv for block to host on"),
              ("Spacing", "Number", "How far they are spaced")]
output_list = [("Blocks", "Block", "Inserted Blocks")]

basic_doc = """Assign patient room block along mutiple crvs"""

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

import Grasshopper
gh_doc = Grasshopper.Instances.ActiveCanvas.Document
print(gh_doc)
print(type(gh_doc))

import scriptcontext as sc
# # gh_doc.AssociateWithRhinoDocument ()
# print Grasshopper.Kernel.GH_Component.GH_InputParamManager
# print type(Grasshopper.Kernel.GH_Component.GH_InputParamManager)
# para_manager = Grasshopper.Kernel.GH_Component.GH_InputParamManager
# para_manager.AddNumberParameter("test","nickname","desc",Grasshopper.Kernel.Acess.Item)
# Grasshopper.Kernel.GH_Component.RegisterInputParams (para_manager)

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
################ input below ###########################

block_name = UnitBlockName
guide_crvs = LocationCrvs
spacing = Spacing
# print ("locationCrv = {}".format(LocationCrvs))
# print ("\n\n\n")

############## main design below #######################


# print ("the active doc is {}".format(Rhino.RhinoDoc.ActiveDoc))
# print ("the layers are as below:")
# for layer in Rhino.RhinoDoc.ActiveDoc.Layers:
#     print layer

def assign_block(block_name, crv, spacing):
    block_definition = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Find(block_name)
    # print Rhino.RhinoDoc.ActiveDoc
    # crv = rs.GetCurveObject("aaa")
    
    print( crv)
    pts = rs.DivideCurveLength(crv, spacing)
    print(pts)

    # paras = [rs.CurveClosestPoint(crv, pt) for pt in pts]
    paras = rs.DivideCurveLength(crv, spacing, return_points=False)
    tangents = [rs.CurveTangent(crv, para) for para in paras]
    side_vectors = [rs.VectorRotate(tangent, 90, [0,0,1]) for tangent in tangents]
    # planes = [rs.CurveFrame(crv, para) for para in paras]
    planes = [rs.PlaneFromFrame(pt, tangent, side_vector) for pt, tangent, side_vector in zip(pts, tangents, side_vectors)]
    return planes
    
    transforms = [Rhino.Geometry.Transform.ChangeBasis(rs.WorldXYPlane(), plane) for plane in planes]
    # print transforms
    # return rs.InsertBlock2(block_name, rs.XformIdentity())
    line = rs.AddLine((0,0,0), (10,0,0))
    blocks = [rs.TransformObject(line, transform, True) for transform in transforms]
    return blocks
    blocks = [gh_doc.Objects.AddInstanceObject(block_definition.Index, transform ) for transform in transforms]
    return blocks
# when running in GH this is not the namescape
# if __name__ == "__main__":

# print block_name
# print guide_crvs
# print spacing

blocks = [assign_block(block_name, guide_crv, spacing) for guide_crv in guide_crvs]
blocks = EnneadTab.RHINO.RHINO_CLEANUP.flatten_list(blocks)

################ output below ######################
Blocks = blocks