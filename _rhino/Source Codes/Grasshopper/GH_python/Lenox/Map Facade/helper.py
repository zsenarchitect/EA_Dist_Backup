import os

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
try:
    import Grasshopper
except:
    pass
import scriptcontext as sc


def bake_brep(breps, layer, name=None):
    if not isinstance(breps, list):
        breps = [breps]

        
    if not name:
        name = layer
        
    if not rs.IsLayer(layer):
        rs.AddLayer(layer)
        
    old_objs = rs.ObjectsByName(name)
    if old_objs:
        rs.DeleteObjects(old_objs)

    objs = [Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(brep) for brep in breps]
    objs = [x for x in objs if rs.IsObject(x)]
    
    rs.ObjectLayer(objs, layer)
    rs.ObjectName(objs, name)

    rs.AddObjectsToGroup(objs, rs.AddGroup(name))
    rs.LayerVisible(layer, True)


class ExternalFile:
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            print ("File path not valid")
            return
        self.doc = Rhino.RhinoDoc.OpenHeadless(filepath)


    def get_external_objs_by_layer(self, layer):
        if not self.doc:
            raise "Doc is lost."
        layer_index = self.doc.Layers.FindByFullPath(layer, Rhino.RhinoMath.UnsetIntIndex)
        if layer_index == Rhino.RhinoMath.UnsetIntIndex:
            raise "Cannot find layer <{}>".format(layer)
            
        layer = self.doc.Layers[layer_index]
        return [x.Geometry for x in self.doc.Objects.FindByLayer(layer)]




if __name__ == "__main__":
    print (123)
    e_file = ExternalFile(r"J:\1643\0_3D\01_Envelope Sketch\_Facade Options\Sample_Mapping\Host.3dm")
    # print (e_file.doc.Layers)
    # for item in e_file.doc.Layers:
    #     print (item)
    print (e_file.get_external_objs_by_layer("facade layout::bldg_levels"))