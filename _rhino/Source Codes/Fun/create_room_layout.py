import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
from pprint import pprint
import random
from System import Array


import sys
sys.path.append("..\lib")

import EnneadTab



def clean_scence():
    # clear elelemt but keep boundary
    rs.UnselectAllObjects()
    crv = rs.ObjectsByType(4, select = True)
    if len(crv) != 1:
        rs.MessageBox("keep only one closed crv at begining screen")
        return False

    rs.InvertSelectedObjects()
    rs.DeleteObjects(rs.SelectedObjects())
    return True


def total_area_not_adding_up(room_list, project_bound_crv):
    total = 0.0
    for x in room_list:
        total += x[1]

    if abs(random_factor() * total - rs.Area(project_bound_crv)) < 10:
        return False

    rs.MessageBox("total area not adding up.\nAsking for {:.2f} total.\nGiven {:.2f} total.".format(total, rs.Area(project_bound_crv)))
    return True


def almost_equal(A, B, t = 0.1):
    if abs(A - B) < t:
        return True
    return False


def find_match_from_list(value, list):
    if list is None:
        return False
    for item in list:
        if almost_equal(item, value):
            return True
    return False


def divide_region(closed_crv, desired_area):
    options = []
    max_t = rs.CurveDomain(closed_crv)[1]
    step = 100


    for t in rs.frange(0.0, max_t, float(max_t / step)):
        test_pt = rs.EvaluateCurve(closed_crv, t)
        direction = rs.CurveTangent(closed_crv, t)
        p_direction = rs.VectorRotate(direction, 90, [0,0,1])
        end_pt = rs.CopyObject(test_pt, p_direction * 20)
        p_line = rs.AddLine(test_pt, end_pt)

        IElist = Array[Rhino.Geometry.Curve]([rs.coercecurve(x) for x in [p_line, closed_crv]])
        result = Rhino.Geometry.Curve.CreateBooleanRegions(IElist,
                                                            Rhino.Geometry.Plane.WorldXY,
                                                            combineRegions = False,
                                                            tolerance = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
                                                    )
        #result = rs.CurveBooleanIntersection(closed_crv, p_line)
        result_crvs = [ result.RegionCurves(i) for i in range(result.RegionCount)]
        #print result_crvs

        if find_match_from_list(desired_area, [ Rhino.Geometry.AreaMassProperties.Compute(x).Area for x in result_crvs]):
            options.append([sc.doc.Objects.AddCurve(x[0]) for x in result_crvs])

        rs.DeleteObjects([end_pt, p_line])


    # when runing parameter on crv there might be multiple results that gives desired_area, this func random pick one pair from all pair
    # return list [desired region, other region]
    random.shuffle(options)
    if len( options) > 0:
        return options[0]
    return False

def random_factor():
    return random.uniform(0.8, 1.2)

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    if not clean_scence():
        return




    # main bounary
    project_bound_crv = rs.ObjectsByType(4)[0]

    # room_list:[ (room_name, room_area),.....]
    room_list = [ ("Living Room", 24),
                    ("Bath Room", 6),
                    ("Bed Room", 15),
                    ("Kitchen", 10)
                    ]


    if total_area_not_adding_up(room_list, project_bound_crv):
        return
    # sort room list by size
    room_list.sort(key = lambda x: x[1], reverse = True)

    pprint(room_list)
    success_count = 0
    attampt = 0
    while attampt < 100:
        if attampt % 50 == 0:
            EnneadTab.NOTIFICATION.toast(sub_text = str(success_count) + " success layouts so far.",
                                        main_text = str(attampt) + " attempts so far.")
        attampt += 1
        if success_count == 10:# make 10 options
            break
        current_layout = Layout(success_count, project_bound_crv)

        # for room data in room list: divide_region
        for room_data in room_list:
            res = current_layout.define_room(room_data)
            if not res:
                current_layout.clean_up()
                break
        else:
            success_count += 1
            # result added to layout collection class

            # copy layout result to  index * dist.
            current_layout.archive_option()


class Layout(object):
    """docstring for layout."""

    def __init__(self, opt_index, raw_boundary_crv):
        self.index = opt_index
        #to become this:  self.rooms = [RoomRegion("Livintg Room", living_rm_boundary_crv), RoomRegion("123", crv)]
        self.rooms = []
        self.unused_boundary_crv = raw_boundary_crv
        self.protected_crv = [raw_boundary_crv]
        #self.unassigned_rooms = room_list

    def define_room(self, room_data):
        room_name, room_area = room_data
        regions = divide_region(self.unused_boundary_crv, room_area)# return list [desired region, other region]
        if not regions: #cannot find a reasonable shape in the remaining area.
            return False
        for region in regions:
            if almost_equal(room_area * random_factor(), rs.Area(region)):
                self.rooms.append(RoomRegion(room_name, region))
            else:
                if self.unused_boundary_crv not in self.protected_crv:
                    rs.DeleteObject(self.unused_boundary_crv)
                self.unused_boundary_crv = region
        return True


    def clean_up(self):
        return
        rs.DeleteObjects([room.region for room in self.rooms])
        if self.unused_boundary_crv not in self.protected_crv:
            rs.DeleteObject(self.unused_boundary_crv)

    def archive_option(self):
        # move collection to side
        # make solid planr surf to room, add text
        for room in self.rooms:
            rs.MoveObject(room.region, (1 + self.index) * rs.CreateVector([20, 0, 0]))
            srf = rs.AddPlanarSrf(room.region)
            text = "{}\n{:.2f}".format(room.name, rs.Area(srf))
            rs.AddTextDot(text, rs.SurfaceAreaCentroid(srf)[0])
        
        rs.Redraw()


class RoomRegion():
    def __init__(self, room_name, room_shape ):
        self.region = room_shape
        self.name = room_name

    """
    def divide_region(self, desired_area):
        closed_crv = self.region

        return region_list
    """
######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    main()
