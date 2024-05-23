import clr # pyright: ignore
from System.Collections.Generic import List # pyright: ignore, IEnumerable

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
import helper
reload(helper)


class DividerSolution:
    def __init__(self, mode):
        
        """mode is either tower or podium"""

        # fetch from local file, those are different per design
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        local_layers = ["facade srfs",
                        "GH control::facade_grids",
                        "GH control::flip_guides"
                        ]
        local_layers = ["facade layout::{}_{}".format(x, mode) for x in local_layers]
        # print (local_layers)
        
        self.srfs = [rs.coercebrep(x) for x in rs.ObjectsByLayer(local_layers[0])]
        rs.LayerVisible(local_layers[0], False)

        grid_crvs = [rs.coercecurve(x) for x in rs.ObjectsByLayer(local_layers[1])]

        self.flip_guide_crvs = []
        temp_pts = [rs.coerce3dpoint(x) for x in rs.ObjectsByLayer(local_layers[2])]
        for pt in temp_pts:
            pt1 = pt + Rhino.Geometry.Vector3d(0,0,500)
            pt2 = pt + Rhino.Geometry.Vector3d(0,0,-500)
            line = Rhino.Geometry.Line(pt1, pt2)
            self.flip_guide_crvs.append(line)

        ###############################################
        
        # fetch from external file, those are always the same
        shared_layers = ["GH control::facade_levels",
                         "GH control::sorting_crv"]

        shared_layers = ["facade layout::{}".format(x) for x in shared_layers]

        
        e_file = helper.ExternalFile(r"J:\1643\0_3D\01_Envelope Sketch\_Facade Options\Sample_Mapping\Host.3dm")



        level_crvs = e_file.get_external_objs_by_layer(shared_layers[0])
        self.sorting_crv = e_file.get_external_objs_by_layer(shared_layers[1])[0]
        
        
        ###############################################

        self.tolerance = rs.UnitAbsoluteTolerance()
        #######################################################
        
        self.panels = []
        self.good_panels_default, self.good_panels_flipped, self.misc_panels = [], [], []
        

        
        self.levels = []
        for level_crv in level_crvs:
            level_plane = rs.CreatePlane(rs.CreatePoint(level_crv.PointAtEnd), [1,0,0], [0,1,0])
            self.levels.append(level_plane)
        self.level_cutter = Rhino.Geometry.Brep()
      
        for level_plane in self.levels:
            for srf in self.srfs:
                normal = rs.SurfaceNormal(srf, [0,0])
                res = Rhino.Geometry.Intersect.Intersection.BrepPlane(srf, level_plane, self.tolerance)
                intersection_crvs = res[1]
                if intersection_crvs is None:
                    continue
                for intersection_crv in intersection_crvs:
                    new_crv = intersection_crv.Duplicate()
                    new_crv.Translate( normal)
                    # new_crv = rs.CopyObject(intersection_crv, normal)

                    # this step is to ensure the inner corner temp brep does not overlap
                    mid_pt = rs.CurveMidPoint(new_crv)
                    transform_scale = Rhino.Geometry.Transform.Scale(mid_pt, 0.5)
                    new_crv.Transform(transform_scale)
                    # new_crv = rs.ScaleObject(new_crv, mid_pt, [0.5, 0.5, 0.5])

                    net_curves = List[Rhino.Geometry.Curve]()
                    for curve in [intersection_crv, new_crv]:
                        net_curves.Add(curve)
                    # net_curves_as_enumerable = IEnumerable[Rhino.Geometry.Curve](net_curves)

                    start = Rhino.Geometry.Point3d.Unset
                    end = Rhino.Geometry.Point3d.Unset
                    start = rs.coerce3dpoint(start, True)
                    end = rs.coerce3dpoint(end, True)
                    mini_cutter = Rhino.Geometry.Brep.CreateFromLoft(net_curves, 
                                                                     start, 
                                                                     end, 
                                                                     Rhino.Geometry.LoftType.Straight, 
                                                                     False)[0]
          
                    # mini_cutter = rs.AddLoftSrf([intersection_crv, new_crv])[0]
                    self.level_cutter.Append(mini_cutter)
        # helper.bake_brep(self.level_cutter, "level_cutter")         
        

        
        self.grids = []
        for grid_crv in grid_crvs:
            x_axis = rs.CurveStartPoint(grid_crv) - rs.CurveEndPoint(grid_crv)
            grid_plane = rs.CreatePlane(rs.CreatePoint(rs.CurveEndPoint(grid_crv)), x_axis, [0,0,1])
            self.grids.append(grid_plane)

        self.grid_cutter = Rhino.Geometry.Brep()

        sc.doc = Rhino.RhinoDoc.ActiveDoc
        grid_crvs = rs.MoveObjects(grid_crvs, [0,0,-500])
        for grid_crv in grid_crvs:
            
            mini_cutter = rs.ExtrudeCurveStraight(grid_crv, [0,0,0], [0,0,1000])
            self.grid_cutter.Append(rs.coercebrep(mini_cutter))
            rs.DeleteObject(mini_cutter)
        rs.DeleteObjects(grid_crvs)
        

        
    def process_srf(self, srf):

        rows = self.get_rows(srf)

        for row in rows:
            row.Faces.ShrinkFaces()
            columns = self.get_columns(row)
            self.panels.extend(columns)



    
    def get_rows(self, srf):
        return srf.Split(self.level_cutter, self.tolerance)

        
    def get_columns(self, srf):
        srfs = srf.Split(self.grid_cutter, self.tolerance)
        for srf in srfs:
            srf.Faces.ShrinkFaces()
            srf.Edges.MergeAllEdges(rs.UnitAngleTolerance())
        return srfs


    def process_srfs(self):
        map(self.process_srf, self.srfs)
        

        
        
        for panel in self.panels:

            # lets take care of the funky shapes first
            if panel.Vertices.Count != 4:
                shape = Rhino.Geometry.Brep.CreateFromOffsetFace(panel.Faces[0], 
                                                                 -2, 
                                                                 self.tolerance, 
                                                                 False, 
                                                                 True)
                if shape:
                    self.misc_panels.append(shape)
                continue
                

            
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
                    self.good_panels_flipped.append(panel)
                else:
                    self.good_panels_default.append(panel)
               
                
            else:

                self.misc_panels.append(panel)
                
                  

        # print(self.good_panels_default)
        # print(self.misc_panels)





        

        
    def sort_srf(self, srf):
        edges = srf.Edges
        base_crv = edges[0]
        t1 = rs.CurveClosestPoint(self.sorting_crv,rs.CurveStartPoint(base_crv))
        t2 = rs.CurveClosestPoint(self.sorting_crv,rs.CurveEndPoint(base_crv))
        if t2<t1:
            rs.ReverseCurve(base_crv)

    def is_close_to_flip_guide(self, panel):
        srf_center = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(panel)
        srf_center = rs.coerce3dpoint(srf_center, True)
        
        for flip_guide_crv in self.flip_guide_crvs:
            # print (flip_guide_crv)
            
            closest_pt = flip_guide_crv.ClosestPoint(srf_center, 0.0)
            # para = rs.CurveClosestPoint(flip_guide_crv, srf_center)
            
            
            # closest_pt = rs.EvaluateCurve(flip_guide_crv, para)
            
            #print (closest_pt)
            if rs.Distance(closest_pt, srf_center) < 5:
                return True
        return False

