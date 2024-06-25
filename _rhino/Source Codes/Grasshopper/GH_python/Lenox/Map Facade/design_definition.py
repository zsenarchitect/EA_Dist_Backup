import time



import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import scriptcontext as sc


import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


sys.path.append(os.path.dirname(__file__))
import helper

from abc import ABCMeta, abstractmethod



class Mode:
    Tower = "tower"
    Podium = "podium"

class DesignDefinition(object):
    # Class-level dictionary to store instances
    _instances = {}
    typ_width = 16
    typ_height = 14.5
    edge_offset = 2

    mode = "unassigned"

    is_symmetric_design = False
    # if is symetric deign, then query flip guide from this layer [xxxx],  that is layout in the ABABAB format
    # otherwise query mirror guide from this layer [yyyy] , that is layout in the AAAAAABBBBBB(it only mirror when turning the wall corner)
    @property
    def flipping_guide_crvs(cls):
        pts = rs.ObjectsByLayer("facade layout::GH control::flip_guides_{}".format(cls.mode))
        flip_guide_crvs = []
        pts = [rs.coerce3dpoint(x) for x in pts]
        for pt in pts:
            pt1 = pt + Rhino.Geometry.Vector3d(0,0,500)
            pt2 = pt + Rhino.Geometry.Vector3d(0,0,-500)
            line = Rhino.Geometry.Line(pt1, pt2)
            flip_guide_crvs.append(line)
        return flip_guide_crvs
        return [x for x in crvs if rs.IsCurve(x)]

    
    is_double_level_design = False
    # if is double level design, then query upper block from this layer [zzzz] and compare if srf.Z is close to those upper level guide crvs
    @property
    def upper_block_crvs(cls):
        if cls.is_double_level_design:
            e_file = helper.ExternalFile(r"J:\1643\0_3D\01_Envelope Sketch\_Facade Options\Sample_Mapping\Host.3dm")
            return e_file.get_external_objs_by_layer("facade layout::GH control::upper_ref")
        else:
            crvs = []
        return [x for x in crvs if rs.IsCurve(x)] 


    @property
    def block_reference(cls):
        return [[0,0,0], [cls.typ_width, 0,0], [0,1,0]]

    __metaclass__ = ABCMeta

    def __new__(cls, option_name, *args, **kwargs):

        # Check if the instance belongs to the base class
        if cls is DesignDefinition:
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

class SampleBlock(DesignDefinition):
    default_block_name = "sample_block"
    
    

class AngledFrame(DesignDefinition):
    default_block_name = "angled_frame"
    parapet_block_name = "angled_frame_top"
    parapet_height = 9.75

    

class SawTooth(DesignDefinition):
    default_block_name = "saw_tooth"
    parapet_block_name = "saw_tooth_parapet"
    parapet_height = 14.5 + 3

class SolarPanel(DesignDefinition):
    is_symmetric_design = True
    is_double_level_design = True    
    default_block_name = "solar_panel_lower"
    upper_block_name = "solar_panel_upper"
    alter_block_name = "solar_panel_lower_cagefree"
    alter_upper_block_name = "solar_panel_upper_cagefree"


    parapet_block_name = "solar_panel_parapet"
    parapet_height = 9.75

    if rs.IsLayer("Corner Block"):
        rs.LayerVisible("Corner Block",True)




