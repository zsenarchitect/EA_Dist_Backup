"""
THis is a good idea to hook to document change event for when to sending new json out

https://github.com/mcneel/rhino-developer-samples/blob/7/rhinopython/SampleEtoModelessForm.py"""



# also can use thread timer to repeatively send out data to L drive.





import io
import json
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)



import logging
import os
import pprint
# get current file folder
# folder = os.path.dirname(os.path.abspath(__file__))
# logging.basicConfig(level=logging.INFO,
#                     filemode="w",
#                     filename="{}\\rhino2json_log.txt".format(folder))
# print "{}\\rhino2json_log.txt".format(folder)

# configure the logger file to write to a text file in the current folder
logging.basicConfig(level=logging.INFO,
                    filemode="w",
                    filename=EnneadTab.get_EA_dump_folder_file("rhino2json_log.txt"),
                    format="%(asctime)s %(levelname)s %(message)s")



@EnneadTab.ERROR_HANDLE.try_catch_error
def rhino2json():
    print ("################# New Serical Begin\n\n\n")
    good_layers = [x for x in rs.LayerNames() if "[Sharing]" in x]
    all_ids = []
    for layer in good_layers:
        all_ids.append(rs.LayerObjects(layer))

    # all_ids = rs.AllObjects( include_lights=True,
                            # include_references=True)
    serialization_option = Rhino.FileIO.SerializationOptions ()
    #serialization_option.WriteUserData  = False

    data = dict()
    for id in all_ids:

        
        
        local_data = dict()
        obj = sc.doc.Objects.Find(id)
        #local_data["id"] = id
        local_data["type"] = str(type(obj))
        #local_data["geometry"] = obj.Geometry
        #local_data["attributes"] = obj.Attributes



        for attr in dir(obj):
            try:
                print ("{} = {}".format(attr, getattr(obj, attr)))
            except:
                print ("Error on {}".format(attr))

        if "instanceobject" in local_data["type"].lower():
            local_data["block_name"] = rs.BlockInstanceName(id)
            # print obj.InstanceXform.ToString()
            # print obj.InstanceXform.ToFloatArray(True)
            # print obj.InstanceXform.M03
            # x_data = []
            # for i in range(3):
            #     for j in range(3):
            #         x_data.append(getattr(obj.InstanceXform, "M{}{}".format(i, j)))
            # print x_data
            x_data = [obj.InstanceXform.M00,
                      obj.InstanceXform.M01,
                      obj.InstanceXform.M02,
                      obj.InstanceXform.M03,
                      obj.InstanceXform.M10,
                      obj.InstanceXform.M11,
                      obj.InstanceXform.M12,
                      obj.InstanceXform.M13,
                      obj.InstanceXform.M20,
                      obj.InstanceXform.M21,
                      obj.InstanceXform.M22,
                      obj.InstanceXform.M23,
                      obj.InstanceXform.M30,
                      obj.InstanceXform.M31,
                      obj.InstanceXform.M32,
                      obj.InstanceXform.M33]
            # print x_data
            local_data["transform"] = x_data



            #local_data["transform"] = obj.InstanceXform .ToJSON(serialization_option)
            local_data["definition"] = obj.InstanceDefinition.ToJSON(serialization_option)

            definition = sc.doc.InstanceDefinitions.Find(obj.InstanceDefinition.Name)
            
            rhobjs = definition.GetObjects()

            """
            next:
            research into those two class, and how to get them from current instance. Can cast obj.geometry?
            +INstanceDefinitionGeometry --->Represents a block definition in a File3dm. This is the same as Rhino.DocObjects.InstanceDefinition, but not associated with a RhinoDoc.
            +InstanceReferenceGeometry --->Represents a reference to the geometry in a block definition.

            those might be or not be able to make to /from json.
            If good, can be used to add new instance to rhino without manually mapping transformation.
            """


        #print obj.Attributes.LayerIndex
        layer = sc.doc.Layers[obj.Attributes.LayerIndex]

        # print all attribute of layer object
        # for attr in dir(layer):
        #     try:
        #         print "{} = {}".format(attr, getattr(layer, attr))
        #     except:
        #         print "Error on {}".format(attr)

        local_data["layer_json"] = layer.ToJSON(serialization_option)
        local_data["layer_fullpath"] = layer.FullPath

        local_data["geo_json"] = obj.Geometry.ToJSON(serialization_option)
        local_data["attr_json"] = obj.Attributes.ToJSON(serialization_option)

        # local print
        print ("\n\n-------{}: {}".format(id, type(obj)))
        keys = [x for x in local_data.keys() if "_json" in x]
        for key in keys:
            print ("+{}".format(key))
            temp = json.loads(local_data[key])
            pprint.pprint(temp)
        data[str(id)] = local_data

        
        
    # geo_abstract = Rhino.Runtime.CommonObject.FromJSON(local_data["geo_json"])
    # attr_abstract = Rhino.Runtime.CommonObject.FromJSON(local_data["attr_json"])
    # sc.doc.objects.add(geo_abstract, attr_abstract)


    # pretty print json dict
    print( "\n\n$$$$$$$$$$$$$$$$$ Final PPrint")
    pprint.pprint(data)

    logging.info(data)

    # saving json to a file
    with open(EnneadTab.get_EA_dump_folder_file("rhino_transfer_data.json"), "w") as outfile:
        json.dump(data, outfile)
    return
    with io.open("rhino_data.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile)


######################  main code below   #########
if __name__ == "__main__":

    rhino2json()



