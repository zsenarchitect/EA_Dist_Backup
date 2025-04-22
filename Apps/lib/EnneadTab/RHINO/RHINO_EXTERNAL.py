

import os


import Rhino # pyright: ignore

    
class ExternalRhino:
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            print ("File path not valid")
            return
        self.doc = Rhino.RhinoDoc.OpenHeadless(filepath)


    def get_external_geos_by_layer(self, layer):
        if not self.doc:
            raise "Doc is lost."
        layer_index = self.doc.Layers.FindByFullPath(layer, Rhino.RhinoMath.UnsetIntIndex)
        if layer_index == Rhino.RhinoMath.UnsetIntIndex:
            raise "Cannot find layer <{}>".format(layer)
            
        layer = self.doc.Layers[layer_index]
        return [x.Geometry for x in self.doc.Objects.FindByLayer(layer)]

