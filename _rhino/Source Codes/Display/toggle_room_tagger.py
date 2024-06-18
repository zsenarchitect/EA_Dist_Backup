import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
import time

import sys
sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Layers")
from initiate_layers import LAYER_COLOR_MAP_BY_NAME
SAMPLE_COLOR_DICT = dict()
for item in LAYER_COLOR_MAP_BY_NAME:
    name, color_tuple = item
    SAMPLE_COLOR_DICT[name.lower()] = color_tuple

DOT_NAME = "EA_ROOM_TAGGER"
ZONE_NAME = "EA_ROOM_TAGGER_ZONE"
KEY_EXCEL_PATH = "ROOM_TAGGER_BAKING_PATH"
KEY_BAKING_COLORFILL = "ROOM_TAGGER_BAKING_COLORFILL"
KEY_HOLDING_CALC = "HOLDING_ALL_CALCULATION"
KEY_LABEL_SIZE = "FONT_SIZE"
KEY_COLOR_DICT = "EA_ROOM_TAGGER_COLOR_DICT"
KEY_LAYER_STAGE = "EA_ROOM_TAGGER_LAYER_STAGE"
sc.sticky["reset_timestamp"] = time.time()

def convert_area_to_good_unit(area, use_commas = True):
    # only provide sqm or sqft, depeding on which system it is using. mm and m -->sqm, in, ft -->sqft

    unit = rs.UnitSystemName(capitalize=False, singular=True, abbreviate=False, model_units=True)

    def get_factor(unit):
        if unit == "millimeter":
            return 1.0/(1000 * 1000), "SQM"
        if unit == "meter":
            return 1.0, "SQM"
        if unit == "inch":
            return 1.0/(12 * 12), "SQFT"
        if unit == "foot":
            return 1.0, "SQFT"
        return 1, "{0} x {0}".format(unit)
    factor, unit_text = get_factor(unit)

    area *= factor
    if use_commas:
        return "{:,.2f} {}".format(area, unit_text)
    else:
        return "{:.2f} {}".format(area, unit_text)
    pass



@EnneadTab.ERROR_HANDLE.try_catch_error
def room_tagger_single():
    crvs = rs.GetObjects(filter=rs.filter.curve)
    pt = rs.GetPoint()
    crvs = [sc.doc.Objects.Find(crv).Geometry for crv in crvs]
    plane = Rhino.Geometry.Plane.WorldXY
    pts = [Rhino.Geometry.Point3d(pt)]
    # print pts
    
   
    
    region = Rhino.Geometry.Curve.CreateBooleanRegions (crvs,
                                                        plane,
                                                        pts,
                                                        False,
                                                        sc.doc.ModelAbsoluteTolerance)
    
    boundary = region.RegionCurves(0)[0]

    sc.doc.Objects.AddCurve(boundary)

    rs.AddTextDot("{}".format(Rhino.Geometry.AreaMassProperties.Compute(boundary).Area),
                  pt)

    
    
    
    rs.EnableRedraw(False)
    
def add_room_tagger_dot(room_name = None):
    sc.sticky[KEY_HOLDING_CALC] = True
            
    pt = rs.GetPoint()
    if room_name is None:
        room_name = rs.StringBox("What is the name of the room?")
    dot = rs.AddTextDot(room_name,
                        pt)
    
    sc.sticky[KEY_HOLDING_CALC] = False
    if not dot:
        return
    rs.ObjectName(dot, DOT_NAME)
    
    
    key = "EA_room_tagger_display_conduit"
    if sc.sticky.has_key(key):
        conduit = sc.sticky[key]
        conduit.cached_data = []
    return dot

class ZoneData:
    def __init__(self, zone_name, zone_rect):
        self.zone_name = zone_name
        self.zone_rect = sc.doc.Objects.Find(zone_rect).Geometry
        self.collection = []
        
        return
    
    def is_room_in_zone(self, room):
        
        plane = Rhino.Geometry.Plane.WorldXY

        if self.zone_rect.Contains(room.room_location, plane, sc.doc.ModelAbsoluteTolerance)== Rhino.Geometry.PointContainment.Inside:
            return True
        return False
        
    

class EA_RoomTaggerConduit(Rhino.Display.DisplayConduit):
    color_dict = EnneadTab.DATA_FILE.get_sticky_longterm(KEY_COLOR_DICT, dict())
    zone_dict = dict()
    
    def update_color_map(self):
        self.__class__.color_dict = EnneadTab.DATA_FILE.get_sticky_longterm(KEY_COLOR_DICT, dict())
        
        
    def update_zone_dict(self):
        self.__class__.zone_dict = dict()
        
        def is_good(x):
            name = rs.ObjectName(x)
            if not name:
                return False
            if not name.startswith(ZONE_NAME):
                return False
            if rs.IsTextDot(x):
                return False
            return True
            
        objs = filter(is_good, rs.AllObjects())
        for obj in objs:
            name = rs.ObjectName(obj)
            self.__class__.zone_dict[name] = ZoneData(name, obj)
          
                
        # print self.__class__.zone_dict
        
    def assign_zone_to_room(self, room):
        for zone_name, zone_data in self.__class__.zone_dict.items():
            if zone_data.is_room_in_zone(room):
                room.zone_name = zone_name
                return
        room.zone_name = "#Unzoned"
        
            
    def __init__(self):
        EnneadTab.NOTIFICATION.messenger(main_text = "Room Tagger Starting...")
        self.cached_data = []
        sc.sticky[KEY_EXCEL_PATH] = None
        sc.sticky[KEY_BAKING_COLORFILL] = False
        sc.sticky[KEY_HOLDING_CALC] = False
        sc.sticky[KEY_LAYER_STAGE] = rs.LayerNames()
        
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_doc_updated(self,sender, e):
        self.reset_conduit_data("Room Tagger Calculating...")

        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_doc_update_after_adding(self,sender, e):
        if self.should_ignore(e.TheObject.Attributes):
            return
        self.reset_conduit_data("New obj added/deleted to document, recalculating...")
  
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_doc_updated_after_deleting(self,sender, e):


        if self.should_ignore(e.TheObject.Attributes):
            return
        self.reset_conduit_data("Obj deleted/added from document, recalculating...")


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_doc_updated_after_layertable_changed(self,sender, e):
        if sc.sticky[KEY_LAYER_STAGE] == rs.LayerNames():
            return
        
        layer = sc.doc.Layers.FindIndex(e.LayerIndex)
        if layer:
            full_layer = layer.FullPath
            if full_layer is None:
                return
            if "[RoomTagger]" not in full_layer:
                return
        
        self.reset_conduit_data("Layer table changed, recalculating...")
        sc.sticky[KEY_LAYER_STAGE] = rs.LayerNames()

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_doc_update_after_modifying(self,sender, e):
 
        if self.should_ignore(e.NewAttributes):
            return
        self.reset_conduit_data("Obj attribute modifed, recalculating...")
    
    
    def should_ignore(self, obj_attr):
        if obj_attr.Name == DOT_NAME:
            return False
        
        layer = sc.doc.Layers.FindIndex(obj_attr.LayerIndex)
        if layer:
            full_layer = layer.FullPath
            if "[RoomTagger]" not in full_layer:
                return True
        return False
        
    
    def reset_conduit_data(self, note):
        if sc.sticky[KEY_HOLDING_CALC]:
            return
        if time.time() - sc.sticky["reset_timestamp"] < 1:
            return
        if note:
            EnneadTab.NOTIFICATION.messenger(main_text = note)
        self.cached_data = []
        self.update_color_map()
        self.update_zone_dict()  
        sc.sticky["reset_timestamp"] = time.time()
    
    def add_hook(self):
        # print "add hook"
        # Rhino.RhinoDoc.SelectObjects  += self.check_doc_updated
        Rhino.RhinoDoc.AddRhinoObject  += self.check_doc_update_after_adding
        Rhino.RhinoDoc.DeleteRhinoObject  += self.check_doc_updated_after_deleting
        Rhino.RhinoDoc.UndeleteRhinoObject   += self.check_doc_update_after_adding
        Rhino.RhinoDoc.ModifyObjectAttributes  += self.check_doc_update_after_modifying
        
        Rhino.RhinoDoc.LayerTableEvent   += self.check_doc_updated_after_layertable_changed
        
    def remove_hook(self):
        # print "remove hook"
        # Rhino.RhinoDoc.SelectObjects  -= self.check_doc_updated 
        Rhino.RhinoDoc.AddRhinoObject  -= self.check_doc_update_after_adding
        Rhino.RhinoDoc.DeleteRhinoObject  -= self.check_doc_updated_after_deleting
        Rhino.RhinoDoc.UndeleteRhinoObject   -= self.check_doc_update_after_adding
        Rhino.RhinoDoc.ModifyObjectAttributes  -= self.check_doc_update_after_modifying
        
        Rhino.RhinoDoc.LayerTableEvent   -= self.check_doc_updated_after_layertable_changed
        
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def DrawForeground(self, e):
        text = "Ennead Room Tagger Mode"
        color = rs.CreateColor([87, 85, 83])
        #color = System.Drawing.Color.Red
        position_X_offset = 20
        position_Y_offset = 40
        main_title = 40
        title_size = 10
        title_gap = title_size + 5
        bounds = e.Viewport.Bounds
        pt = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        e.Display.Draw2dText(text, color, pt, False, main_title)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + main_title)
        e.Display.Draw2dText("Layer name with [RoomTagger] in it will count toward boundary.", color, pt, False, title_size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + title_gap)
        e.Display.Draw2dText("Right Click to add room object.", color, pt, False, title_size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + title_gap)
        e.Display.Draw2dText("Crvs and crvs inside blocks are recongnised when searching boundary..", color, pt, False, title_size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + title_gap)
        e.Display.Draw2dText("When run into performance issue, limit how many layer are searchable.", color, pt, False, title_size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + title_gap)
        e.Display.Draw2dText("Crvs inside block will also be calcualted, but it is slower than non-block crvs.", color, pt, False, title_size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + title_gap)
        size = 20
        offset = 20

        if not self.is_ready:
            return

        
        area_map = {}
        room_color_map = {}
        area_sum = 0
        for room in self.rooms:
            
            if room.room_name not in area_map:
                area_map[room.room_name] = room.area_raw
            else:
                area_map[room.room_name] += room.area_raw
            
            area_sum += room.area_raw
            if room.room_name not in room_color_map:
                room_color_map[room.room_name] = room.color
        
        
        for room_name in sorted(area_map):
            pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
  
            e.Display.Draw2dText("{}: {}".format(room_name, convert_area_to_good_unit(area_map[room_name])), room_color_map[room_name], pt, False, size)

        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset*1.5)
        area_map["Total"] = area_sum
        e.Display.Draw2dText("{}: {}".format("Total", convert_area_to_good_unit(area_sum)), color, pt, False, size)
        
        
        
        
        
        
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset*1.5)
        e.Display.Draw2dText("----Area Per Zone Below----", color, pt, False, size)

        zone_area_map = {}
        zone_sum_map = {}
        
        for room in self.rooms:
            key = room.zone_name + "@" + room.room_name
            if key not in zone_area_map:
                zone_area_map[key] = room.area_raw
            else:
                zone_area_map[key] += room.area_raw
                
            if room.zone_name not in zone_sum_map:
                zone_sum_map[room.zone_name] = room.area_raw
            else:
                zone_sum_map[room.zone_name] += room.area_raw
            

        
        last_zone_name = sorted(zone_area_map)[0]
        for key in sorted(zone_area_map):
     
            zone_name, room_name = key.split("@")
            area = zone_area_map[key]
            
            if last_zone_name != zone_name:
                pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset*2) # this makes overall gaps
                e.Display.Draw2dText("[{}]: {}".format(zone_name.replace(ZONE_NAME + "_", ""),
                                                       convert_area_to_good_unit(zone_sum_map[zone_name])), color, pt, False, size)
                pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
                last_zone_name = zone_name
            else:
                pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
                
  
            e.Display.Draw2dText("{}: {}".format(room_name, convert_area_to_good_unit(area)), room_color_map[room_name], pt, False, size)











        if sc.sticky[KEY_EXCEL_PATH]:
            filepath = sc.sticky[KEY_EXCEL_PATH]
            from EnneadTab.EXCEL import ExcelDataItem
            data = []
            
            ordered_keys = sorted(sorted(area_map.keys()), key = lambda x: x.lower() == "total")
            for i, room_name in enumerate(ordered_keys):
                entry_1 = ExcelDataItem(room_name, i,0)
                entry_2 = ExcelDataItem(convert_area_to_good_unit(area_map[room_name]), i,1)
                data.append(entry_1)
                data.append(entry_2)
                
            EnneadTab.EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab Room Tagger Data")
            sc.sticky[KEY_EXCEL_PATH] = None
            
        if sc.sticky[KEY_BAKING_COLORFILL]:
            bake_colorfill(self.rooms)
            sc.sticky[KEY_BAKING_COLORFILL] = False


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def PreDrawObjects(self, e):
        if not self.cached_data:
            
        
            crvs = get_good_crvs()
            if not crvs:
                self.is_ready = False
                return
            
            try:
                dots = rs.ObjectsByName(DOT_NAME)
            except:
                self.is_ready = False
                
                return
            self.rooms = [Room(dot, crvs) for dot in dots]
            map(self.assign_zone_to_room, self.rooms)
            self.cached_data = self.rooms
        else:
            self.rooms = self.cached_data
            
        self.is_ready = True
       
        
        for room in self.rooms:
            
            if room.shape:
                e.Display.DrawBrepShaded (room.shape, Rhino.Display.DisplayMaterial(room.color, 0))
                
        for room in self.rooms:  
            e.Display.DrawDot  (room.room_location, room.annotation,room.color, System.Drawing.Color.Red)
            
                
def get_color_from_name(text):
    if not text:
        return rs.CreateColor( [0,0,0])
    if text.lower() in SAMPLE_COLOR_DICT:
        color = SAMPLE_COLOR_DICT[text.lower()]
        return rs.CreateColor( [color[0],
                                color[1],
                                color[2]])
         
    color = EA_RoomTaggerConduit.color_dict.get(text, None)
    if color:
        return rs.CreateColor( [color[0],
                                color[1],
                                color[2]])
    
    color = EnneadTab.COLOR.get_random_color()
    EA_RoomTaggerConduit.color_dict[text] = [color[0],
                                           color[1],
                                           color[2]]
    return rs.CreateColor( [color[0],
                            color[1],
                            color[2]])


class Room:
    def __init__(self, dot, crvs):
        dot_geo = sc.doc.Objects.Find(dot).Geometry
        # print dot_geo
        self.room_name, self.room_location = dot_geo.Text, dot_geo.Point
        
        self.color = get_color_from_name(self.room_name)
        plane = Rhino.Geometry.Plane.WorldXY
  
        
    
        
        region = Rhino.Geometry.Curve.CreateBooleanRegions (crvs,
                                                            plane,
                                                            [self.room_location],
                                                            False,
                                                            sc.doc.ModelAbsoluteTolerance)
        try:
            
            if region.RegionCount == 1:
                boundaries = region.RegionCurves(0)
                # print ("-----there is only one region, this should always be the case becasue there are only one testin gpt")
                # print boundaries
                if len(boundaries) == 1:
                    # print ("there is only one loop")
                    
                    self.shape = Rhino.Geometry.Brep.CreatePlanarBreps(boundaries[0], sc.doc.ModelAbsoluteTolerance)[0]
                else:
                    # print ("there are many loop")
                    # for boudnary in boundaries:
                    #     print boudnary
                    """
                    main_shape_crv = boundaries[0]
                    other_shapes_crvs = boundaries[1:]   
                    print("----")
                    print(main_shape_crv)
                    print(other_shapes_crvs)
                    for other_shape_crv in other_shapes_crvs:
                        remains = Rhino.Geometry.Curve.CreateBooleanDifference (main_shape_crv.ToNurbsCurve(), 
                                                                                other_shape_crv.ToNurbsCurve(), 
                                                                                sc.doc.ModelAbsoluteTolerance*2)
                        print(remains)
                        main_shape_crv = remains[0]
                        for crv in remains:
                            sc.doc.Objects.AddCurve(crv)
                    self.shape = Rhino.Geometry.Brep.CreatePlanarBreps(main_shape_crv, sc.doc.ModelAbsoluteTolerance)[0]
                    """
                    
                    main_shape = Rhino.Geometry.Brep.CreatePlanarBreps(boundaries[0], sc.doc.ModelAbsoluteTolerance)[0]
                    # print main_shape
                    other_shapes = [Rhino.Geometry.Brep.CreatePlanarBreps(boundary, sc.doc.ModelAbsoluteTolerance)[0] for boundary in boundaries[1:]]
                    for cutter in other_shapes:
                        
                        remains = main_shape.Split(cutter, sc.doc.ModelAbsoluteTolerance)
                        main_shape = remains[1]
                 
                    self.shape = main_shape
                    
            else:
                print ("!!!!!there is many regions.....this should not happen")
                for i in range(region.RegionCount):
                    boundaries = region.RegionCurves(i)
                    print(boundaries)
                    print(boundaries[0])
       

            
            # self.shape = sc.doc.Objects.AddCurve(boundary)
            self.area_raw = Rhino.Geometry.AreaMassProperties.Compute(self.shape).Area
            self.area  = convert_area_to_good_unit(self.area_raw)
            self.side_card = "{}:{}".format(self.room_name, self.area)
            self.annotation = "---\n\n\n{}".format(self.area)
        except Exception as e:
            
            self.shape = None
            self.area_raw = 0
            self.area = 0
            self.side_card = "{}:{}...{}".format(self.room_name, "No Area", e)
            self.annotation = "---\n\n\n{}".format("No Area")

        
@EnneadTab.ERROR_HANDLE.try_catch_error
def get_good_crvs():
    
    
    def is_allowed(x):
        try:
            return rs.IsCurve(x)
        except:
            return False
        
        
    good_layers = [x for x in rs.LayerNames() if "[RoomTagger]" in x]
    crvs = []
    for layer in good_layers:
        crv_objs = [sc.doc.Objects.Find(x).Geometry for x in rs.ObjectsByLayer(layer) if rs.IsCurve(x)]
        if len(crv_objs)>200:
            print ("more than 200 objs uder layer <{}>, skipping".format(layer))
            EnneadTab.NOTIFICATION.messenger(main_text = "Layer {} have too many objs to abstract. Skipping".format(layer))
            
            continue
        
        instance_objs = [x for x in rs.ObjectsByLayer(layer) if rs.IsBlockInstance(x)]
        if instance_objs:
            for instance_obj in instance_objs:
                crv_objs += [x for x in EnneadTab.RHINO.RHINO_OBJ_DATA.get_instance_geo(instance_obj) if is_allowed(x)]
            
        if len(crv_objs) > 5000:
            print ("with content inside blocks, there more than 5000 objs uder layer <{}>, skipping".format(layer))
            EnneadTab.NOTIFICATION.messenger(main_text = "Layer {} have too many objs to abstract. SKipping".format(layer))
            continue
        else:
            crvs += crv_objs
        
    
    
    # crvs = [sc.doc.Objects.Find(crv).Geometry for crv in crvs]
    
    return crvs


@EnneadTab.ERROR_HANDLE.try_catch_error
def bake_colorfill(rooms):
    sc.sticky[KEY_HOLDING_CALC] = True
    rs.StatusBarProgressMeterShow(label="Baking Graphic...",
                                  lower=0,
                                  upper=len(rooms))
    
    label_collection = []
    hatch_collection = []
    rs.EnableRedraw(False)
    
    for layer in rs.LayerNames():
        if not rs.IsLayer(layer):
            continue
        if layer.startswith("RoomTagger::"):
            rs.PurgeLayer(layer)
    
    # add temp hatch to trigger the hatchpattern table reader
    temp_hatch = rs.AddHatch(rs.AddCircle(rs.WorldXYPlane(),1))
    
    solid_hatch_index = sc.doc.HatchPatterns.FindName("Solid").Index
    font_size = sc.sticky[KEY_LABEL_SIZE]
    
    for i, room in enumerate(rooms):
        rs.StatusBarProgressMeterUpdate(i)
        hatch_obj, text_obj = bake_room(room,solid_hatch_index, font_size)
        label_collection.append(text_obj)
        hatch_collection.append(hatch_obj)
    
    rs.StatusBarProgressMeterHide()
    rs.EnableRedraw(True)
    
    rs.AddObjectsToGroup(label_collection, rs.AddGroup())
    rs.ObjectColorSource(label_collection, 1)
    rs.ObjectColor(label_collection, rs.CreateColor(0,0,0))
    rs.AddObjectsToGroup(hatch_collection, rs.AddGroup())
    
    # clear temp hatch
    rs.DeleteObject(temp_hatch)
    
    sc.sticky[KEY_HOLDING_CALC] = False

def bake_room(room,solid_hatch_index, font_size):
    # print (room.room_name)
    text_layer = "RoomTagger::Label::{}".format(room.room_name)
    if not rs.IsLayer(text_layer):
        rs.AddLayer(text_layer, room.color)
    text_obj = rs.AddText(text="{}\n{}".format(room.room_name, room.area),
                        point_or_plane=room.room_location,
                        justification=2,
                        height=font_size)
    rs.ObjectLayer(text_obj, text_layer)

    
    hatch_layer = "RoomTagger::Hatch::{}".format(room.room_name)
    if not rs.IsLayer(hatch_layer):
        rs.AddLayer(hatch_layer, room.color)
    hatch_geo = Rhino.Geometry.Hatch.CreateFromBrep (room.shape,
                                                    0,
                                                    solid_hatch_index,
                                                    0,
                                                    1,
                                                    room.room_location)
    
    hatch_obj = sc.doc.Objects.AddHatch(hatch_geo)
    rs.ObjectLayer(hatch_obj, hatch_layer)
    return hatch_obj, text_obj

@EnneadTab.ERROR_HANDLE.try_catch_error
def toggle_room_tagger():

    conduit = None
    key = "EA_room_tagger_display_conduit"
    if sc.sticky.has_key(key):
        conduit = sc.sticky[key]
    else:
        # create a conduit and place it in sticky
        conduit = EA_RoomTaggerConduit()
        sc.sticky[key] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled: 
        conduit.add_hook()
        
        print("conduit enabled")
    else: 
        conduit.remove_hook()
        print("conduit disabled")
    sc.doc.Views.Redraw()
    rs.EnableRedraw(False)
     
    EnneadTab.DATA_FILE.set_sticky_longterm(KEY_COLOR_DICT, conduit.__class__.color_dict)
    
    print("Tool Finished")
######################  main code below   #########
if __name__ == "__main__":

    # room_tagger_single()
    toggle_room_tagger()




