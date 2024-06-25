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

class DividerSolution:
    def __init__(self, srfs, level_crvs, grid_crvs, flip_guide_crvs, sorting_crv):
        self.srfs = srfs
        self.flip_guide_crvs = flip_guide_crvs
        self.sorting_crv = sorting_crv
        self.panels = []
        self.temp = []
        
        self.levels = []
        for level_crv in level_crvs:
            level_plane = rs.CreatePlane(rs.CreatePoint(rs.CurveEndPoint(level_crv)), [1,0,0], [0,1,0])
            self.levels.append(level_plane)
        self.level_cutter = Rhino.Geometry.Brep()
      
        for level_plane in self.levels:
            for srf in srfs:
                normal = rs.SurfaceNormal(srf, [0,0])
                res = Rhino.Geometry.Intersect.Intersection.BrepPlane(srf, level_plane, rs.UnitAbsoluteTolerance())
                intersection_crvs = res[1]
                if intersection_crvs is None:
                    continue
                for intersection_crv in intersection_crvs:
                    new_crv = rs.CopyObject(intersection_crv, normal)

                    # this step is to ensure the inner corner temp brep does not overlap
                    mid_pt = rs.CurveMidPoint(new_crv)
                    new_crv = rs.ScaleObject(new_crv, mid_pt, [0.5, 0.5, 0.5])

                    
                    mini_cutter = rs.AddLoftSrf([intersection_crv, new_crv])[0]
                    self.level_cutter.Append(rs.coercebrep(mini_cutter))
                    
        self.temp.append(self.level_cutter)
        
        self.grids = []
        for grid_crv in grid_crvs:
            x_axis = rs.CurveStartPoint(grid_crv) - rs.CurveEndPoint(grid_crv)
            grid_plane = rs.CreatePlane(rs.CreatePoint(rs.CurveEndPoint(grid_crv)), x_axis, [0,0,1])
            self.grids.append(grid_plane)

        self.grid_cutter = Rhino.Geometry.Brep()
        grid_crvs = rs.MoveObjects(grid_crvs, [0,0,-500])
        for grid_crv in grid_crvs:
            
            mini_cutter = rs.ExtrudeCurveStraight(grid_crv, [0,0,0], [0,0,1000])
            self.grid_cutter.Append(rs.coercebrep(mini_cutter))

        
    def process_srf(self, srf):

        rows = self.get_rows(srf)
        
        self.temp.extend(rows)
        for row in rows:
            row.Faces.ShrinkFaces()
            columns = self.get_columns(row)
            self.panels.extend(columns)
            

    
    def get_rows(self, srf):
        return srf.Split(self.level_cutter, rs.UnitAbsoluteTolerance())
        normal = rs.SurfaceNormal(srf, [0,0])
        cutter = Rhino.Geometry.Brep()
        for plane in self.levels:
            res = Rhino.Geometry.Intersect.Intersection.BrepPlane(srf, plane, rs.UnitAbsoluteTolerance())
            intersection_crvs = res[1]
            if intersection_crvs is None:
                    continue
            for intersection_crv in intersection_crvs:
                new_crv = rs.CopyObject(intersection_crv, normal)
                mini_cutter = rs.AddLoftSrf([intersection_crv, new_crv])[0]
                cutter.Append(rs.coercebrep(mini_cutter))
            
        return srf.Split(cutter, rs.UnitAbsoluteTolerance())
        
    def get_columns(self, srf):
        return srf.Split(self.grid_cutter, rs.UnitAbsoluteTolerance())
    
        normal = rs.SurfaceNormal(srf, [0,0])
      
        cutter = Rhino.Geometry.Brep()
        for plane in self.grids:
            
            res = Rhino.Geometry.Intersect.Intersection.BrepPlane(srf, plane, rs.UnitAbsoluteTolerance())
            intersection_crvs = res[1]
            if not intersection_crvs:
                continue
            
            for intersection_crv in intersection_crvs:

                new_crv = rs.CopyObject(intersection_crv, normal)
                mini_cutter = rs.AddLoftSrf([intersection_crv, new_crv])[0]
                self.temp.append(mini_cutter)
                cutter.Append(rs.coercebrep(mini_cutter))
            
        return srf.Split(cutter, rs.UnitAbsoluteTolerance())

    def process_srfs(self):
        map(self.process_srf, self.srfs)

        
        good_panels_default, good_panels_flipped, misc_panels = [], [], []
        for panel in self.panels:
            panel.Faces.ShrinkFaces()
            
            U = panel.Faces[0].Domain(0)
            U_dim = U[1]-U[0]
            V = panel.Faces[0].Domain(1)
            V_dim = V[1]-V[0]
            short_side = min(U_dim, V_dim)
            # print (short_side)
            if short_side > 5:
                # self.sort_srf(srf)
                if self.is_close_to_flip_guide(panel):
                    panel.Faces[0].Reverse(0, True)
                    good_panels_flipped.append(panel)
                else:
                    good_panels_default.append(panel)
               
                
            else:
                panel = rs.coercebrep(rs.OffsetSurface(panel, -2, create_solid=True))
                misc_panels.append(panel)


        self.bake_brep(misc_panels, "Massing::Small Framer", "EDGES")
        return good_panels_default, good_panels_flipped, misc_panels, self.temp


    def bake_brep(self, breps, layer, name):
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        old_objs = rs.ObjectsByName(name)
        if old_objs:
            rs.DeleteObjects(old_objs)

        objs = [Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(brep) for brep in breps]

        rs.ObjectLayer(objs, layer)
        rs.ObjectName(objs, name)
        rs.AddObjectsToGroup(objs, rs.AddGroup(name))
        rs.LayerVisible(layer, True)

        

        
    def sort_srf(self, srf):
        edges = srf.Edges
        base_crv = edges[0]
        t1 = rs.CurveClosestPoint(self.sorting_crv,rs.CurveStartPoint(base_crv))
        t2 = rs.CurveClosestPoint(self.sorting_crv,rs.CurveEndPoint(base_crv))
        if t2<t1:
            rs.ReverseCurve(base_crv)

    def is_close_to_flip_guide(self, panel):
        srf_center = get_center(panel)
        for flip_guide_crv in self.flip_guide_crvs:
            para = rs.CurveClosestPoint(flip_guide_crv, srf_center)
            closest_pt = rs.EvaluateCurve(flip_guide_crv, para)
            #print (closest_pt)
            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False


def get_center(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center

def main():
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    srfs, level_crvs, grid_crvs, flip_guide_crvs = None, None, None, None



    layers = ["facade layout::facade srfs",
            "facade layout::GH control::facade_levels",
            "facade layout::GH control::facade_grids",
            "facade layout::GH control::flip_guides",
            "facade layout::GH control::sorting_crv"]

    
    for layer in rs.LayerNames():
        
        if layer == layers[0]:
            srfs = [rs.coercebrep(x) for x in rs.ObjectsByLayer(layer)]
            rs.LayerVisible(layer, False)
        if layer == layers[1]:
            level_crvs = [rs.coercecurve(x) for x in rs.ObjectsByLayer(layer)]
        if layer == layers[2]:
            grid_crvs = [rs.coercecurve(x) for x in rs.ObjectsByLayer(layer)]
        if layer == layers[3]:
            flip_guide_crvs = [rs.coercecurve(x) for x in rs.ObjectsByLayer(layer)]
        if layer == layers[4]:
            sorting_crv = rs.coercecurve(rs.ObjectsByLayer(layer)[0])

    
    sc.doc = ghdoc


    solution = Solution(srfs, level_crvs, grid_crvs, flip_guide_crvs, sorting_crv)
    # print (solution)
    return solution.process_srfs()



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

