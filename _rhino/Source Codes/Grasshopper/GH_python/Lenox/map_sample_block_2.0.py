"""this script was patched mutiple times to add new features during design phase, 
it is not a very clean stage.

To clean it up, i suggest prepare a dict that make a dict of deisgn option and class objs.
Those class all come from a abstract class that define what blocks names to use, what is the typ width and height, what is the layers needed to do mirror action and upper/lower action
By using abstract class you can make sub option by inherate a class and modify some prperty


also try to break some common action to EnneadTab CORE so other can use it later"""

import time

import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab
reload(EnneadTab)
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import scriptcontext as sc

from abc import ABCMeta, abstractmethod

class DesignOption(object):
    # Class-level dictionary to store instances
    _instances = {}
    typ_width = 16
    typ_height = 14.5

    is_symmetric_design = False
    # if is symetric deign, then query flip guide from this layer [xxxx],  that is layout in the ABABAB format
    # otherwise query mirror guide from this layer [yyyy] , that is layout in the AAAAAABBBBBB(it only mirror when turning the wall corner)
    @property
    def flipping_guide_crvs(cls):
        if cls.is_symmetric_design:
            crvs = rs.ObjectsByLayer("flip_guides_sym")
        else:
            crvs = rs.ObjectsByLayer("flip_guides")
        return [x for x in crvs if rs.IsCurve(x)]

    
    is_double_level_design = False
    # if is double level design, then query upper block from this layer [zzzz] and compare if srf.Z is close to those upper level guide crvs
    @property
    def upper_block_crvs(cls):
        if cls.is_double_level_design:
            crvs = rs.ObjectsByLayer("upper_ref")
        else:
            crvs = []
        return [x for x in crvs if rs.IsCurve(x)] 


    @property
    def block_reference(cls):
        return [[0,0,0], [cls.typ_width, 0,0], [0,1,0]]

    __metaclass__ = ABCMeta

    def __new__(cls, option_name, *args, **kwargs):

        # Check if the instance belongs to the base class
        if cls is DesignOption:
            instances = cls._instances
        else:
            # If it's a subclass, use the subclass-specific dictionary
            # or create a new one if it doesn't exist yet
            if not hasattr(cls, '_instances'):
                cls._instances = {}
            instances = cls._instances

        # Check if an instance with the same path exists in the dictionary
        if option_name in instances:
            return instances[option_name]
        else:
            # Create a new instance if it doesn't exist
            instance = object.__new__(cls)
            instances[option_name] = instance
            # Initialize the instance with additional arguments
            instance.__init__(option_name, *args, **kwargs)
            return instance

    def __init__(self, option_name):
        self.option_name = option_name
        

    # @abstractmethod
    # def as_json(self):
    #     pass

    # @abstractmethod
    def __repr__(self):
        return "EA {} Class Obj: {}".format(self.__class__, self.option_name)

#################################################################

class SampleBlock(DesignOption):
    default_block_name = "sample_block"
    
    

class AngledFrame(DesignOption):
    default_block_name = "angled_frame"
    

class SawTooth(DesignOption):
    default_block_name = "saw_tooth"

class SolarPanel(DesignOption):
    is_symmetric_design = True
    is_double_level_design = True    
    default_block_name = "solar_panel_lower"
    upper_block_name = "solar_panel_upper"
#################################################################

class Solution(object):


    
    def __init__(self):
        self.srfs = input_srfs
        self.option_name = design_option

        crvs = rs.ObjectsByLayer("sorting_crv")
        if not crvs or len(crvs) != 1 or not rs.IsCurve(crvs[0]):
            print ("There should be only 1 crv in <{}> layer".format("sorting_crv"))
            return
        self.sorting_crv = crvs[0]
        
        customized_class = globals().get(self.option_name, None)
        if not customized_class:
            print ("design option {} not found".format(self.option_name))
            return
        self.option = customized_class
        print (self.option)

        attr_list = ["typ_width",
                     "typ_height",
                     "is_symmetric_design",
                     "is_double_level_design",
                     "flipping_guide_crvs"]
        for attr in attr_list:
            print ("{} = {}".format(attr, getattr(self.option, attr)))






    # @property
    # def option_name(self):
    #     return self.option.option_name
        
    def pre_action(self):
        for group_name in rs.GroupNames():
            if self.option_name in group_name:
                rs.DeleteGroup(group_name)
        old_blocks = rs.ObjectsByName(self.option_name)
        if old_blocks:
            rs.DeleteObjects(old_blocks)

        self.collection = []
        self.temp_block = rs.InsertBlock(self.option.default_block_name, [0,0,0])
        rs.ObjectName(self.temp_block, self.option_name)
        if self.option.is_double_level_design:
            self.temp_upper_block = rs.InsertBlock(self.option.upper_block_name, [0,0,0])
            rs.ObjectName(self.temp_upper_block, self.option_name)

            
    def post_action(self):
        cleanup_list = ["temp_block",
                        "temp_upper_block"]
        for item in cleanup_list:
            if hasattr(self, item):
                rs.DeleteObject(getattr(self, item))


            
        rs.ObjectName(self.collection, self.option_name)
        rs.AddObjectsToGroup(self.collection, rs.AddGroup(self.option_name))
        primary_layer = "FinalBlocks::{}".format(self.option_name)
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
        # if len(corners) != 4:
        #     return
        
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

        if self.is_upper_srf(srf):
            temp_block = self.temp_upper_block
        else:
            temp_block = self.temp_block
        placed_block = rs.OrientObject( temp_block, self.option("Temp").block_reference, target_reference, flags = 1 + 2)
        scale_factor_hori = rs.Distance(pt0, pt1)/self.option.typ_width
        scale_factor_vert = h/self.option.typ_height
        scale_factor_vert *= -1 if is_mirrored else 1

        local_plane = Rhino.Geometry.Plane(pt0, pt1, directional_ref_temp)
        transform = Rhino.Geometry.Transform.Scale(local_plane, scale_factor_hori, 1,scale_factor_vert)

        rs.TransformObject( placed_block, transform, copy = False)

        self.collection.append(placed_block)
        



        
    def process_srfs(self):
        map(self.process_srf, self.srfs)
        



    def should_mirror_horitiontally(self, srf):
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)

        for flip_guide_crv in self.option("Default").flipping_guide_crvs:
            para = rs.CurveClosestPoint(flip_guide_crv, srf_center)
            closest_pt = rs.EvaluateCurve(flip_guide_crv, para)
            
            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False

    def is_upper_srf(self, srf):
        if not self.option.is_double_level_design:
            return False

        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        
        for upper_guide_crv in self.option("ttt").upper_block_crvs:
            upper_guide_crv =  rs.coercegeometry(upper_guide_crv)
            end_pt = upper_guide_crv.PointAtEnd
            if abs(end_pt.Z - srf_center.Z) < 3:
                return True
        return False


def main():
    print (time.time())
    start = time.time()

    
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    solution = Solution()
    rs.EnableRedraw(False)
    solution.pre_action()
    solution.process_srfs()
    solution.post_action()
    rs.EnableRedraw(True)
    sc.doc = ghdoc

    print ("done!")
    print (time.time())
    time_delta = EnneadTab.TIME.get_readable_time (time.time() - start)
    EnneadTab.NOTIFICATION.messenger("Script rerun after {}".format(time_delta))
    

main()