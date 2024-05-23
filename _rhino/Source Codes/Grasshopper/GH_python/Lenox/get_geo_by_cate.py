input_list = []
output_list = [("ProjectNorth", "Crv", "One crv representing the project north so facade NWSE make sense."),
               ("Context", "Breps", "all content in design"),
               ("Receiver", "Breps", "Where anylis surfaces graphic is cast on"),
               ("Glazing","Breps","Define the glazing for window wall ratio")]


basic_doc = """This will try to get geos by looking up key word in layer names
to get the related geos, mark those in the layer name, it can be on the final layer, or the parent layer.
[] is important, the keywords are case sensitive

"""
PREFIX_KEY = "EA_Analysis"
for item in output_list:
    basic_doc += "layer name with [{0}_{1}] --> {1} Geos\n".format(PREFIX_KEY,item[0])


########################################### internal setup
import _utility
__doc__ = _utility.generate_doc_string(basic_doc, input_list, output_list)
# default_value_map = _utility.generate_default_value_map()

# print dir(_utility)
# use this to trick GH that all varibale is defined.
globals().update(_utility.validate_input_list(globals(), input_list))



################ input below ###########################


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Grasshopper
sc.doc = Grasshopper.Instances.ActiveCanvas.Document

import math
############## main design below #######################

def get_geos():
    out = []
    for item in output_list:
        search_key = "[{}_{}]".format(PREFIX_KEY, item[0])
        out.append(get_objs_by_layer_keyword(search_key))

    return out


def get_objs_by_layer_keyword(keyword):
    objs = []
    for layer in Rhino.RhinoDoc.ActiveDoc.Layers:
        if not layer.IsDeleted and keyword in layer.FullPath:
            temp = Rhino.RhinoDoc.ActiveDoc.Objects.FindByLayer(layer)
            if temp:
                temp = [x.Geometry for x in temp if hasattr(x, "Geometry")]
                objs.extend(temp)
            
    return objs

if _utility.is_all_input_valid(globals(), input_list):
    result = get_geos()



    ################ output below ######################
    for i,item in enumerate(output_list):
        output_name = item[0]
        globals()[output_name] = result[i]
    
    """
    Context = result[0]
    Receiver = result[1]
    """

else:
    print ("There are missing valid input")

sc.doc = Rhino.RhinoDoc.ActiveDoc