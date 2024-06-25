import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
try:
    import Grasshopper
except:
    pass
import scriptcontext as sc


import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


sys.path.append(os.path.dirname(__file__))
import design_definition
reload(design_definition)
from design_definition import *


import helper

class BlockSolution(object):


    
    def __init__(self, panels, edges, design_option_raw, mode):




        self.mode = mode
        self.srf_center_map = {}
        
        e_file = helper.ExternalFile(r"J:\1643\0_3D\01_Envelope Sketch\_Facade Options\Sample_Mapping\Host.3dm")
             
        self.upper_block_crvs = e_file.get_external_objs_by_layer("facade layout::GH control::upper_ref")


        pts = rs.ObjectsByLayer("facade layout::GH control::flip_guides_{}".format(mode))
        self.flipping_guide_crvs = []
        pts = [rs.coerce3dpoint(x) for x in pts]
        for pt in pts:
            pt1 = pt + Rhino.Geometry.Vector3d(0,0,500)
            pt2 = pt + Rhino.Geometry.Vector3d(0,0,-500)
            line = Rhino.Geometry.Line(pt1, pt2)
            self.flipping_guide_crvs.append(line)
 

        self.srfs = panels
        self.edges = edges
        self.design_option_raw = design_option_raw
        self.option_name_formatted = "{}_{}".format(design_option_raw, mode)
        
        e_file = helper.ExternalFile(r"J:\1643\0_3D\01_Envelope Sketch\_Facade Options\Sample_Mapping\Host.3dm")
        self.sorting_crv = e_file.get_external_objs_by_layer("facade layout::GH control::sorting_crv")[0]
        
        customized_class = globals().get(self.design_option_raw, None)
        if not customized_class:
            print ("design option {} not found".format(self.design_option_raw))
            return

        customized_class.mode = mode
        self.option = customized_class
        print (self.option)

        # attr_list = ["typ_width",
        #              "typ_height",
        #              "is_symmetric_design",
        #              "is_double_level_design",
        #              "flipping_guide_crvs"]
        # for attr in attr_list:
        #     print ("{} = {}".format(attr, getattr(self.option, attr)))

        



    def bake_edges(self):
        temp = []
        for edge in self.edges:
            shape = Rhino.Geometry.Brep.CreateFromOffsetFace(edge.Faces[0], 
                                                                    -self.option.edge_offset, 
                                                                    rs.UnitAbsoluteTolerance(), 
                                                                    False, 
                                                                    True)

            if shape:
                temp.append(shape)
        helper.bake_brep(temp, "Massing::Small Framer", "{}_EDGES".format(self.mode))

    # @property
    # def option_name(self):
    #     return self.option.option_name
        
    def pre_action(self):
        for group_name in rs.GroupNames():
            if self.option_name_formatted in group_name:
                rs.DeleteGroup(group_name)
        old_blocks = rs.ObjectsByName(self.option_name_formatted)
        if old_blocks:
            rs.DeleteObjects(old_blocks)

        self.collection = []
        self.temp_block = rs.InsertBlock(self.option.default_block_name, [0,0,0])
        rs.ObjectName(self.temp_block, self.option_name_formatted)
        if self.option.is_double_level_design:
            self.temp_upper_block = rs.InsertBlock(self.option.upper_block_name, [0,0,0])
            rs.ObjectName(self.temp_upper_block, self.option_name_formatted)


        if hasattr(self.option, "parapet_block_name"):
            self.temp_parepet_block = rs.InsertBlock(self.option.parapet_block_name, [0,0,0])
            rs.ObjectName(self.temp_parepet_block, self.option_name_formatted)

            crvs = rs.ObjectsByLayer("facade layout::GH control::parapet_guides_{}".format(self.mode))
            self.parapet_guide_crvs = [rs.coerceline(x) for x in crvs]

        if hasattr(self.option, "alter_block_name"):
            self.temp_alter_block = rs.InsertBlock(self.option.alter_block_name, [0,0,0])
            rs.ObjectName(self.temp_alter_block, self.option_name_formatted)
            self.temp_alter_upper_block = rs.InsertBlock(self.option.alter_upper_block_name, [0,0,0])
            rs.ObjectName(self.temp_alter_upper_block, self.option_name_formatted)
            
            pts = rs.ObjectsByLayer("facade layout::GH control::alter_guides_{}".format(self.mode))

            self.alter_guide_crvs = []
            pts = [rs.coerce3dpoint(x) for x in pts]
            for pt in pts:
                pt1 = pt + Rhino.Geometry.Vector3d(0,0,500)
                pt2 = pt + Rhino.Geometry.Vector3d(0,0,-500)
                line = Rhino.Geometry.Line(pt1, pt2)
                self.alter_guide_crvs.append(line)

            
    def post_action(self):

        self.bake_edges()
        

        
        cleanup_list = ["temp_block",
                        "temp_upper_block",
                        "temp_parepet_block",
                        "temp_alter_block",
                        "temp_alter_upper_block"]
        for item in cleanup_list:
            if hasattr(self, item):
                rs.DeleteObject(getattr(self, item))


            
        rs.ObjectName(self.collection, self.option_name_formatted)
        rs.AddObjectsToGroup(self.collection, rs.AddGroup(self.option_name_formatted))
        primary_layer = "FinalBlocks::{}".format(self.design_option_raw)
        if not rs.IsLayer(primary_layer):
            rs.AddLayer(primary_layer)
        rs.ObjectLayer(self.collection, primary_layer)
        for layer_name in rs.LayerNames():
            if layer_name == "FinalBlocks":
                rs.LayerVisible(layer_name, True)
                continue
            if layer_name.startswith("FinalBlocks"):
                rs.LayerVisible(layer_name, layer_name == primary_layer)

        
    def process_srf(self, srf):

        corners = [x.Location for x in srf.Vertices]
        

        pts = EnneadTab.RHINO.RHINO_OBJ_DATA.sort_pts_by_Z(corners)

        pt0 = pts[0]
        pt1 = pts[1]
        pt0, pt1 = EnneadTab.RHINO.RHINO_OBJ_DATA.sort_AB_along_crv(pt0, pt1, self.sorting_crv)

        is_mirrored = self.should_mirror_horitiontally(srf)
        if is_mirrored:
            pt0, pt1 = pt1, pt0








        h = EnneadTab.RHINO.RHINO_OBJ_DATA.get_obj_h(srf)
        tangent = Rhino.Geometry.Vector3d(pt1 - pt0)

        angle = -90 if is_mirrored else 90
        side_vector = rs.VectorRotate(tangent, angle, [0,0,1])
        directional_ref_temp = pt0 + side_vector
        target_reference = [pt0, pt1, directional_ref_temp]



        is_upper = self.is_upper_srf(srf)
        is_alter = self.is_alter_srf(srf)

        if is_upper == False and is_alter == False:
            temp_block = self.temp_block
        elif is_upper == True and is_alter == False:
            temp_block = self.temp_upper_block
        elif is_upper == False and is_alter == True:
            temp_block = self.temp_alter_block
        elif is_upper == True and is_alter == True:
            temp_block = self.temp_alter_upper_block
        


        if self.is_parapet_srf(srf):
            temp_block = self.temp_parepet_block  
            height = self.option.parapet_height
        else:
            height = self.option.typ_height


             
        placed_block = rs.OrientObject( temp_block, self.option("Temp").block_reference, target_reference, flags = 1 + 2)
        scale_factor_hori = rs.Distance(pt0, pt1)/self.option.typ_width
        scale_factor_vert = h/height
        scale_factor_vert *= -1 if is_mirrored else 1

        local_plane = Rhino.Geometry.Plane(pt0, pt1, directional_ref_temp)
        transform = Rhino.Geometry.Transform.Scale(local_plane, scale_factor_hori, 1,scale_factor_vert)

        rs.TransformObject( placed_block, transform, copy = False)

        self.collection.append(placed_block)
        



        
    def process_srfs(self):
        map(self.process_srf, self.srfs)
        

        # print (sorted(self.logger)[0:10])
        # print (sorted(self.logger)[-10:-1])



    def should_mirror_horitiontally(self, srf):
        
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        srf_center = rs.coerce3dpoint(srf_center, True)

        
        for flip_guide_crv in self.flipping_guide_crvs:
            # print ("a:{}".format(type(flip_guide_crv)))
            closest_pt = flip_guide_crv.ClosestPoint(srf_center, False)# False means using infinite line

            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False

    def is_alter_srf(self, srf):
        if not hasattr(self.option, "alter_block_name"):
            return False
        
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        srf_center = rs.coerce3dpoint(srf_center, True)

        
        for alter_guide_crv in self.alter_guide_crvs:
  
            closest_pt = alter_guide_crv.ClosestPoint(srf_center, False)# False means using infinite line

            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False
        

    def is_upper_srf(self, srf):
        if not self.option.is_double_level_design:
            return False

 

        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        srf_center = rs.coerce3dpoint(srf_center, True)
        # print (srf_center)


        for upper_guide_crv in self.upper_block_crvs:
            # upper_guide_crv =  rs.coercegeometry(upper_guide_crv)
            end_pt = upper_guide_crv.PointAtEnd
            if abs(end_pt.Z - srf_center.Z) < 3:
                return True
        return False

    def is_parapet_srf(self, srf):
        if not hasattr(self.option, "parapet_block_name"):
            return False
        
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        srf_center = rs.coerce3dpoint(srf_center, True)
        for parapet_guide_crv in self.parapet_guide_crvs:
            closest_pt = parapet_guide_crv.ClosestPoint(srf_center, True)# True means using limitd line

            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False




    def log(self, x):
        if not hasattr(self, "logger"):
            self.logger = []

        self.logger.append(x)