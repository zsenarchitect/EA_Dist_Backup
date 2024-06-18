import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import scriptcontext as sc
import time
print (time.time())

class Solution:
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




good_panels_default, good_panels_flipped, misc_panels, temp = main()




# this is the overload method syntax
# import System # pyright: ignore.Collections.Generic.IEnumerable as IEnumerable
# out = brep.Split.Overloads[IEnumerable[Rhino.Geometry.Brep], System.Double]( cutters, .001)
