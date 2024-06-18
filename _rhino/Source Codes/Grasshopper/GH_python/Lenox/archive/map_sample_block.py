"""this script was patched mutiple times to add new features during design phase, 
it is not a very clean stage.

To clean it up, i suggest prepare a dict that make a dict of deisgn option and class objs.
Those class all come from a abstract class that define what blocks names to use, what is the typ width and height, what is the layers needed to do mirror action and upper/lower action
By using abstract class you can make sub option by inherate a class and modify some prperty


also try to break some common action to EnneadTab CORE so other can use it later"""

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import scriptcontext as sc
import time
print (time.time())
import os
import sys
parent_folder = os.path.dirname(os.path.dirname(__file__))
parent_folder = os.path.dirname(os.path.dirname(parent_folder))
sys.path.append("{}\\lib".format(parent_folder))
import EnneadTab


SAMPLE_NAME = block_name
SAMPLE_WIDTH = 16
SAMPLE_HEIGHT = 14.5



class Solution:
    def __init__(self):
        self.srfs = input_srfs
        
        

    def process_srf(self, srf):
        # print ("\n\nnew srf")
        corners = srf.Vertices
        pts = sorted(corners, key=lambda x: x.Location.Z)

        pt0 = pts[0].Location
        pt1 = pts[1].Location

        t1 = rs.CurveClosestPoint(self.sorting_crv,pt0)
        t2 = rs.CurveClosestPoint(self.sorting_crv,pt1)
        t1 = rs.CurveNormalizedParameter(self.sorting_crv, t1)
        t2 = rs.CurveNormalizedParameter(self.sorting_crv, t2)

        if abs(abs(t1) - abs(t2)) > 0.2: #deal with para point that span the crv seam
            pt0, pt1 = pt1, pt0
        if t2<t1:
            pt0, pt1 = pt1, pt0
        if self.is_close_to_flip_guide(srf):
            pt0, pt1 = pt1, pt0
            is_mirrored = True
        else:
            is_mirrored = False


    
        h = pts[-1].Location.Z - pts[0].Location.Z


        tangent = Rhino.Geometry.Vector3d(pt1 - pt0)

        angle = -90 if is_mirrored else 90
        side_vector = rs.VectorRotate(tangent, angle, [0,0,1])

        directional_ref_temp = pt0 + side_vector


        target_reference = [pt0, pt1, directional_ref_temp]

        if self.is_upper_srf(srf):
            temp_block = self.temp_upper_block_flipped if is_mirrored else self.temp_upper_block
        else:
            temp_block = self.temp_flipped_block if is_mirrored else self.temp_block
        placed_block = rs.OrientObject( temp_block, self.block_reference, target_reference, flags = 1 + 2)
        scale_factor_hori = rs.Distance(pt0, pt1)/SAMPLE_WIDTH
        scale_factor_vert = h/SAMPLE_HEIGHT
        scale_factor_vert *= -1 if is_mirrored else 1

        local_plane = Rhino.Geometry.Plane(pt0, pt1, directional_ref_temp)
        transform = Rhino.Geometry.Transform.Scale(local_plane, scale_factor_hori, 1,scale_factor_vert)

        rs.TransformObject( placed_block, transform, copy = False)

        self.collection.append(placed_block)
        rs.ObjectName(self.collection, SAMPLE_NAME)

        

    
    def process_srfs(self):
        self.sorting_crv = rs.coercecurve(rs.ObjectsByLayer("sorting_crv")[0])
        # print self.sorting_crv
        if SAMPLE_NAME == "Solar Panel_Lower":
            self.flip_guide_crvs = rs.ObjectsByLayer("flip_guides_sym")
            self.upper_guide_crvs = rs.ObjectsByLayer("upper_ref")
            self.upper_guide_crvs = [x for x in self.upper_guide_crvs if rs.IsCurve(x)]
            self.temp_upper_block = rs.InsertBlock("Solar Panel_Upper", [0,0,0])
        else:
            self.flip_guide_crvs = rs.ObjectsByLayer("flip_guides")


        self.temp_block = rs.InsertBlock(SAMPLE_NAME, [0,0,0])
        if SAMPLE_NAME == "sample_block":
            flipped_block_name = SAMPLE_NAME
        else:
            flipped_block_name = SAMPLE_NAME + "_flipped"
        self.temp_flipped_block = rs.InsertBlock(flipped_block_name, [0,0,0])
        self.temp_upper_block_flipped = rs.InsertBlock("Solar Panel_Upper" + "_flipped", [0,0,0])
        self.block_reference = [[0,0,0], [SAMPLE_WIDTH, 0,0], [0,1,0]]

        for group_name in rs.GroupNames():
            if SAMPLE_NAME in group_name:
                rs.DeleteGroup(group_name)
        old_blocks = rs.ObjectsByName(SAMPLE_NAME)
        if old_blocks:
            rs.DeleteObjects(old_blocks)
        self.collection = []
        
        map(self.process_srf, self.srfs)
        
        rs.DeleteObject(self.temp_block)
        rs.DeleteObject(self.temp_flipped_block)
        if hasattr(self, "temp_upper_block") and rs.IsObject(self.temp_upper_block):
            rs.DeleteObject(self.temp_upper_block)

        if hasattr(self, "temp_upper_block_flipped") and rs.IsObject(self.temp_upper_block_flipped):
            rs.DeleteObject(self.temp_upper_block_flipped)

            
        rs.ObjectName(self.collection, SAMPLE_NAME)
        rs.AddObjectsToGroup(self.collection, rs.AddGroup(SAMPLE_NAME))
        layer = "blocks::{}".format(SAMPLE_NAME)
        if not rs.IsLayer(layer):
            rs.AddLayer(layer)
        rs.ObjectLayer(self.collection, layer)
        


    def is_close_to_flip_guide(self, srf):
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        for flip_guide_crv in self.flip_guide_crvs:
            para = rs.CurveClosestPoint(flip_guide_crv, srf_center)
            closest_pt = rs.EvaluateCurve(flip_guide_crv, para)
            # print (closest_pt)
            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False

    def is_upper_srf(self, srf):
        if SAMPLE_NAME != "Solar Panel_Lower":
            return False

     
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(srf)
        # print sc.doc
        for upper_guide_crv in self.upper_guide_crvs:
            # print upper_guide_crv
            upper_guide_crv =  rs.coercegeometry(upper_guide_crv)
            
            end_pt = upper_guide_crv.PointAtEnd
          
            if abs(end_pt.Z - srf_center.Z) < 3:
                return True
        return False


def main():
    solution = Solution()
    # with EnneadTab.RHINO.RHINO_GRASSHOPPER.AccessRhinoDoc(ghdoc):
    #     solution.process_srfs()

    sc.doc = Rhino.RhinoDoc.ActiveDoc
    rs.EnableRedraw(False)
    solution.process_srfs()
    rs.EnableRedraw(True)
    sc.doc = ghdoc

    print ("done!")
    print (time.time())
    

main()