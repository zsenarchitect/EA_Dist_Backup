"""if iron python cannot decode 64 string, try uding stand alone?"""



import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import base64 # this used to decode 64base string that comme from Rhino toJSON method
import re

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

import logging
import os
import pprint
import json
# get current file folder
# folder = os.path.dirname(os.path.abspath(__file__))
# logging.basicConfig(level=logging.INFO,
#                     filemode="w",
#                     filename="{}\\json2rhino_log.txt".format(folder))
# print "{}\\json2rhino_log.txt".format(folder)

# configure the logger file to write to a text file in the current folder
logging.basicConfig(level=logging.INFO,
                    filemode="w",
                    filename=EnneadTab.get_EA_dump_folder_file("json2rhino_log.txt"),
                    format="%(asctime)s %(levelname)s %(message)s")



def OLD_decode_base64(data):
    """Decode a base64 string."""
    if not isinstance(data, str):
        return data
    
    bytes_data = data.encode('utf-8')  # convert string to bytes
    decoded_bytes = base64.b64decode(bytes_data)  # decode base64 bytes
    decoded_string = decoded_bytes.decode('utf-8')  # convert bytes back to string
    
    return decoded_string

def decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    # Ensure altchars is a string for Python 2.7
    altchars = "".join(c for c in altchars)
    
    # Ensure data is a byte string
    data = data if isinstance(data, str) else data.encode()
    
    # Normalize
    data = re.sub(r'[^a-zA-Z0-9%s]+' % altchars, '', data)  
    
    missing_padding = len(data) % 4
    if missing_padding:
        data += '='* (4 - missing_padding)
    
    # Ensure altchars is a byte string again for base64.b64decode
    altchars = altchars if isinstance(altchars, str) else altchars.encode()
    
    return base64.b64decode(data, altchars)


@EnneadTab.ERROR_HANDLE.try_catch_error
def json2rhino():
    print ("\n\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # read data from "rhino_data.json" as dict
    with open(EnneadTab.get_EA_dump_folder_file("rhino_transfer_data.json"), "r") as f:
        data = json.load(f)
    for id, info in data.items():
        #pprint.pprint(info)
        geo = info["geo_json"]
        #print geo
        #print type(geo)

        if 1> 2:
            geo_abstract = Rhino.Runtime.CommonObject.FromJSON(info["geo_json"])
            print (info["attr_json"])
            print (999)
            base_data = json.loads(info["attr_json"])
            print (base_data)

            print (int(base_data["archive3dm"]))
            print (int(base_data["opennurbs"]))
            print( type(base_data["data"]))
            attr_abstract = Rhino.Runtime.CommonObject.FromBase64String (int(base_data["archive3dm"]),
                                                                            int(base_data["opennurbs"]),
                                                                            base_data["data"])
            
            sc.doc.objects.add(geo_abstract, attr_abstract)

        # import System # pyright: ignore.Convert.ToBase64String


        geo_abstract = Rhino.Runtime.CommonObject.FromJSON(info["geo_json"])
        #print geo_abstract

        
        # coded_string = info["attr_json"]

        
        # formatted_json = base64.b64decode(coded_string)

        # attr_abstract = Rhino.Runtime.CommonObject.FromJSON(formatted_json)


        # sc.doc.objects.add(geo_abstract, attr_abstract)

        new_attr = Rhino.DocObjects.ObjectAttributes()
        layer = Rhino.Runtime.CommonObject.FromJSON(info["layer_json"])
        full_path = info["layer_fullpath"]

        if not rs.IsLayer(full_path):
            full_path = rs.AddLayer(full_path)
            new_layer_index = sc.doc.Layers.FindByFullPath(full_path, -1)
            new_layer = sc.doc.Layers[new_layer_index]
            new_layer.Color = layer.Color

        # for attr in dir(layer):
        #     try:
        #         print "{} = {}".format(attr, getattr(layer, attr))
        #     except:
        #         print "Error on {}".format(attr)
        # in_file_layer_index = sc.doc.Layers.FindByFullPath(info["layer_name"], -1)
        # print in_file_layer_index
        # if in_file_layer_index == -1:
        #     in_file_layer_index = sc.doc.Layers.Add()
        #     in_file_layer = sc.doc.Layers[in_file_layer_index]
        #     in_file_layer.Name = info["layer_name"]
        #     in_file_layer.Color = layer.Color
        #     print in_file_layer.Color
        #     print in_file_layer.Name
        #     print in_file_layer_index
        #     rs.LayerColor(in_file_layer.Name, in_file_layer.Color)
        #     sc.doc.Views.Redraw()


        # new_attr.LayerIndex = in_file_layer_index
        new_attr.LayerIndex = sc.doc.Layers.FindByFullPath(full_path, -1)

        if "instanceobject" in info["type"].lower():
            #definition = Rhino.Runtime.CommonObject.FromJSON(info["definition"])
            definition = sc.doc.InstanceDefinitions.Find(info["block_name"])
            xform_data = info["transform"]
            # print xform_data
            xform = Rhino.Geometry.Transform()
            # print xform
            xform.M00 = xform_data[0]
            xform.M01 = xform_data[1]
            xform.M02 = xform_data[2]
            xform.M03 = xform_data[3]
            xform.M10 = xform_data[4]
            xform.M11 = xform_data[5]
            xform.M12 = xform_data[6]
            xform.M12 = xform_data[6]
            xform.M13 = xform_data[7]
            xform.M20 = xform_data[8]
            xform.M21 = xform_data[9]
            xform.M22 = xform_data[10]
            xform.M23 = xform_data[11]
            xform.M30 = xform_data[12]
            xform.M31 = xform_data[13]
            xform.M32 = xform_data[14]
            xform.M33 = xform_data[15]
    
       
            # print xform
            """
            to figure out how to by pass sericalization of transform object. right now it is using a default transformation"""
            obj = sc.doc.Objects.AddInstanceObject(definition.Index, xform, new_attr )
        else:
            obj = sc.doc.Objects.Add(geo_abstract, new_attr)
        #rs.ObjectLayer(obj, info["layer_name"])
        
    
    rs.Redraw()
        



######################  main code below   #########
if __name__ == "__main__":

    json2rhino()



