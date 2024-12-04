try:
    from pyrevit import script
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass


import math
import traceback
import random
from EnneadTab import NOTIFICATION, SAMPLE_FILE, IMAGE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_SELECTION, REVIT_VIEW, REVIT_SCHEDULE, REVIT_FORMS

LIFE_SAFETY_CALCULATOR_FAMILY_NAME = "LifeSafetyCalculator"
LIFE_SAFETY_CALCULATOR_FAMILY_PATH = SAMPLE_FILE.get_file("{}.rfa".format(LIFE_SAFETY_CALCULATOR_FAMILY_NAME))
LIFE_SAFETY_CALCULATOR_DUMP_VIEW = "EnneadTab_LifeSafetyCalculater_Dump"
DIVIDER = "+"
class EgressData:
    data_collection = dict()

    @staticmethod
    def level_name_match(level_name):
        return level_name.replace(" Lachman/Wolman/Campus", "")\
                        .replace(" (also Wolman / Campus)", "")\
                        .replace(" Existing", "")\
                        .replace(" Lachman", "")\
                        .replace(" Existing", "")\
                        .replace(" Wolman / Campus Exist Roof", "")
    
    @classmethod
    def egress_id_exist(cls, test_id):
        for data in cls.data_collection.values():
            if data.egress_id == test_id:
                return True
        return False
    
    @property
    def is_stair(self):
        return "stair" in self.EgressId.lower()
    
    def __init__(self, level_name, egress_id):
        self.LevelName = level_name
        self.EgressId = egress_id

        self.RevitDoorObjCollection = []
        self.RevitStairObjCollection = []
        self.OccupancyLoad = 0

    @classmethod
    def get_data(cls, level_name, egress_id):
        level_name = EgressData.level_name_match(level_name)
        
        key = (level_name, egress_id)
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = EgressData(level_name, egress_id)
        cls.data_collection[key] = instance
        return instance


    def add_load(self, load):
        self.OccupancyLoad += load


    @property
    def TypeName(self):
        return "{}_{}".format(self.LevelName, self.EgressId)
    

    def __str__(self):
        return "Level: {}, Egress Id: {}, Occupancy Load: {}, Total Width: {}".format(self.LevelName, self.EgressId, self.OccupancyLoad, self.total_width)





def load_life_safety_calculator(doc, force_reload = False):
    if force_reload:
        REVIT_FAMILY.get_family_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, 
                                        doc=doc,
                                        load_path_if_not_exist = LIFE_SAFETY_CALCULATOR_FAMILY_PATH)
    else:
        REVIT_FAMILY.get_family_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, 
                                        doc=doc)

def secure_dump_view(doc):
    view = REVIT_VIEW.get_view_by_name(LIFE_SAFETY_CALCULATOR_DUMP_VIEW, doc=doc)
    if not view:
        print ("Cannot find dump view, creating one")
        NOTIFICATION.messenger("Cannot find dump view, creating one")
        view = REVIT_VIEW.create_drafting_view(doc, LIFE_SAFETY_CALCULATOR_DUMP_VIEW, 200)
    return view

class LifeSafetyChecker:
    output = script.get_output()
    
    @staticmethod
    def get_door_width(door, para_name):
        try:
            return door.LookupParameter(para_name).AsDouble()
        except:
            return door.Symbol.LookupParameter(para_name).AsDouble()



    @staticmethod
    def get_stair_width(stair):

        runs = [stair.Document.GetElement(x) for x in stair.GetStairsRuns()]
        
        max_width = runs[0].ActualRunWidth
        for run in runs:
            if not  run.ActualRunWidth == max_width:
                print( "--This stair has variring  run width--->{}. Talk to Sen Zhang to understand what it means.".format(LifeSafetyChecker.output.linkify(run.Id)))
        return max_width
    
    def __init__(self, doc, data_source):
        self.is_ready = True
        self.doc = doc
        self.data_source = data_source
        self.output = script.get_output()

        self.dump_view = secure_dump_view(doc)

        if not REVIT_FAMILY.get_family_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, 
                                                doc=doc):
            NOTIFICATION.messenger("Cannot find life safety calculator family, please load it first")
            self.is_ready = False
            return


    def run_check(self):
        if not self.is_ready:
            NOTIFICATION.messenger("Life safety checker is not ready")
            return
        # loop thru all spatial element, either from area or from room. 
        cate = DB.BuiltInCategory.OST_Rooms if self.data_source.Source == "Room" else DB.BuiltInCategory.OST_Areas
        all_spatial_elements = DB.FilteredElementCollector(self.doc).OfCategory(cate).WhereElementIsNotElementType().ToElements()

        if self.data_source.Source == "Area":
            all_spatial_elements = filter(lambda x: x.AreaScheme.Name == self.data_source.AreaSchemeName, all_spatial_elements)

        if len(all_spatial_elements) == 0:
            print ("Cannot find any spatial element to calculate life safety")
            return

        # get a test spatial element to see if all needed parameter is valid
        tester = all_spatial_elements[0]
        if not self.varify_para_exist(tester):
            print ("Missing parameters, please fix")
            return
                          

        
        # for each egress data, 
            # collect final load number
            # find the target egress door and egress stair and egress exit of this spatial element, add to the load of that item data

        all_spatial_elements = sorted(all_spatial_elements, key = lambda x: x.LookupParameter("Name").AsString())
        for spatial_element in all_spatial_elements:

            
            final_load = self.get_spatial_element_final_capacity(spatial_element)

            level_name = self.doc.GetElement(spatial_element.LevelId).Name
            target_list = self.get_spatial_element_target_list(spatial_element)

            # when a egress is assigned to A2+B2, the total load of this space need to divide to 2 parts and assign one each
            divider_count = len(target_list) 
            for target_name in target_list:
                local_load = int(math.ceil(final_load / float(divider_count)))
                target_data = EgressData.get_data(level_name, target_name)
                target_data.add_load(local_load)

            


        # for ground level need to treat specially: the immediate load(NOT the worst load) from above and below of EACH stair need to converge
        #  but do not need to add current ground level load to the same door


        self.gather_revit_objs()
        self.update_life_safety_calculator()
        self.purge_bad_calculater()


        
    def update_life_safety_calculator(self):
        # for each item data, get a data calculator and update.
        # why not use revit obj directly? 
            # becasue stair can not easitl disply data by level. and stair and door if mixed in multi-category schdule can cause confusion, althoug it is technically possoble
            # because it is impossible to update door from a link
        for i, data_item in enumerate(sorted(EgressData.data_collection.values(), key = lambda x: (x.LevelName, x.EgressId))):
            type_name = data_item.TypeName
            family_type = REVIT_FAMILY.get_family_type_by_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, type_name, create_if_not_exist=True)
            if family_type and not family_type.IsActive:
                family_type.Activate()
            instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME, type_name)
            if instances is None:
                print ("Cannot find life safety calculator family type [{}], if persistant, please at least place one instance of this family in the project".format(type_name))
                continue
            if len(instances) == 0:
                dist = 100
                x = dist * (i % 5)
                y = dist * (i // 5)  
                instance = self.doc.Create.NewFamilyInstance(DB.XYZ(x, y, 0), family_type, self.dump_view)
                instances = [instance]



            for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):
                level_obj = REVIT_SELECTION.get_level_by_name(data_item.LevelName, doc)
                if level_obj:
                    break
            else:
                print("Cannot find level obj [{}]".format(data_item.LevelName))
            data_item.LevelElevation = level_obj.Elevation



            door_width = 0
            for i, door in enumerate(data_item.RevitDoorObjCollection):
                print ("{}. door {} LS width is {}".format(i+1,self.output.linkify(door.Id, title = door.Name), LifeSafetyChecker.get_door_width(door, self.data_source.ParaNameDoorWidth)))
                door_width += LifeSafetyChecker.get_door_width(door, self.data_source.ParaNameDoorWidth)
            data_item.EgressDoorWidth = door_width
            data_item.OccupancyDoorCapacity = int(math.floor(data_item.EgressDoorWidth * 12 /0.2))

            if len(data_item.RevitStairObjCollection) > 0:
                stair = data_item.RevitStairObjCollection[0]
                data_item.EgressStairWidth = LifeSafetyChecker.get_stair_width(stair)
            else:
                print ("Cannot find stair for {} on level [{}], going to use existing value from the calculator type.".format(data_item.EgressId, data_item.LevelName))
                stair = None
                data_item.EgressStairWidth = family_type.LookupParameter("EgressStairWidth").AsDouble()
            data_item.OccupancyStairCapacity = int(math.floor(data_item.EgressStairWidth * 12 /0.3))

            data_item.Zone = "To be defined per team"

                
            filler_para_names = [
                "EgressId",
                "LevelName",
                "LevelElevation",
                "EgressDoorWidth",
                "EgressStairWidth",
                "OccupancyDoorCapacity",
                "OccupancyStairCapacity",
                "OccupancyLoad",
                "Zone"
            ]
            for para_name in filler_para_names:
                family_type.LookupParameter(para_name).Set(getattr(data_item, para_name, 0))

            # below are useful if want to also push back the data to revit obj so it not entirely relying on data calculator
            sending_back_to_revit = False
            if sending_back_to_revit:
            
                # get the doors in this data item and update the door width
                for door in data_item.RevitDoorObjCollection:
                    door.LookupParameter(self.data_source.ParaNameDoorCapacityRequired).Set(data_item.OccupancyLoad)

                for stair in data_item.RevitStairObjCollection:
                    stair.LookupParameter(self.data_source.ParaNameDoorCapacityRequired).Set(data_item.OccupancyLoad)


    def gather_revit_objs(self):

        egress_id_para_name = self.data_source.ParaNameEgressId
        def is_valid_egress_id(element):
            if not element.LookupParameter(egress_id_para_name):
                return False
            if not element.LookupParameter(egress_id_para_name).HasValue:
                return False
            if not element.LookupParameter(egress_id_para_name).AsString() != "":
                return False
            return True

        for doc in REVIT_APPLICATION.get_revit_link_docs(including_current_doc=True):

            all_doors = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements())
            all_doors = filter(is_valid_egress_id, all_doors)
            # if (len(all_doors) == 0):
            #     print("Cannot find any egress door in document <{}>".format(doc.Title))

            for door in all_doors:
                level_name = doc.GetElement(door.LevelId).Name
                egress_id = door.LookupParameter(egress_id_para_name).AsString()
                egress_data = EgressData.get_data(level_name, egress_id)
                # why do i use collection instead of a single door? In example where there is a stadium, you have 3 doors side by side that are all called EXIT K, it is one big egreesss that need to map 3 instance of family.
                egress_data.RevitDoorObjCollection.append(door)

            all_stairs = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements())
            all_stairs = filter(is_valid_egress_id, all_stairs)
            #  why using nesting loop? need to collect all egress stair called "Stair 5", in some cases they might be several seprateed stairs to connect one long one.
            for stair in all_stairs:
                egress_id = stair.LookupParameter(egress_id_para_name).AsString()
                for item in EgressData.data_collection.values():
                    if item.EgressId == egress_id:
                        item.RevitStairObjCollection.append(stair)

        # # print all door and stair collected data
        # for data in EgressData.data_collection.values():
        #     print ("Door: {}".format(data.RevitDoorObjCollection))
        #     print ("Stair: {}".format(data.RevitStairObjCollection))

                
    def varify_para_exist(self, tester):
        
        for para_name in [self.data_source.ParaNameLoadPerArea,
                          self.data_source.ParaNameLoadManual,
                          self.data_source.ParaNameTarget]:
            if tester.LookupParameter(para_name) is None:
                print ("Missing <{}> for the spatial element".format(para_name))
                NOTIFICATION.messenger("Missing <{}> for the spatial element".format(para_name))
                return False

        return True

    
    def get_spatial_element_target_list(self, spatial_element):
        target_list = spatial_element.LookupParameter(self.data_source.ParaNameTarget).AsString()
        if target_list == "" or target_list is None:
            empty_target = "--No Egress Target--"
            print ("{} Egress target not assigned, please fix. Level = [{}]".format(self.output.linkify(spatial_element.Id, title = spatial_element.LookupParameter("Name").AsString()),
                                                                   spatial_element.Level.Name))
            spatial_element.LookupParameter(self.data_source.ParaNameTarget).Set(empty_target)
            return []
        
        if DIVIDER in target_list:
            target_list = target_list.split(DIVIDER)
            target_list = [x.strip() for x in target_list]
        else:
            target_list = [target_list]

        return target_list

    def get_manual_load_value(self, spatial_element):
        """Retrieve and convert the manual load parameter value."""
        manual_para = spatial_element.LookupParameter(self.data_source.ParaNameLoadManual)
        
        if manual_para.StorageType == DB.StorageType.Integer:
            return manual_para.AsInteger()

        elif manual_para.StorageType == DB.StorageType.String:
            if manual_para.AsString() is None:
                return 0
            try:
                return int(manual_para.AsString())
            except:
                print("Cannot convert {} to integer, please fix".format(manual_para.AsString()))
                return 0

        print("Unknown storage type: {}".format(manual_para.StorageType))
        return 0

    def get_spatial_element_final_capacity(self, spatial_element):

        # Prioritize manual override
        maunual_value = self.get_manual_load_value(spatial_element)
        
        if maunual_value > 0:
            print("{} is manually set to {}".format(self.output.linkify(spatial_element.Id, title=spatial_element.LookupParameter("Name").AsString()), maunual_value))
            return maunual_value


        # ignore rooms whose AreaPerPerson is negative
        if spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble() < 0:
            return 0

        if spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble () == 0:
            print ("{} has 0 area per person, assign a value to this parameter to enable life safety calculation or even better, use key schedule to set values".format(self.output.linkify(spatial_element.Id, title = spatial_element.LookupParameter("Name").AsString())))
            return 0

            
        return int(math.ceil(spatial_element.Area / spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble ()))


    def purge_bad_calculater(self):
        valid_type_names = [x.TypeName for x in EgressData.data_collection.values()]
   
        

        all_types = REVIT_FAMILY.get_all_types_by_family_name(LIFE_SAFETY_CALCULATOR_FAMILY_NAME)
        if not all_types:
            print ("Cannot find any life safety calculator types in the project, please place at least one instance of this calculator family")
            return
        for type in all_types:
            if type.LookupParameter("Type Name").AsString() not in valid_type_names:
                self.doc.Delete(type.Id)
#####################################################################################################################################

class SpatialDataSource:
    """use this format to define how to extract lfe safety data, 
    each project mght want to do someting differently.
    source: "Area" or "Room"
    area_scheme_name: the name of the area scheme to use for area source
    para_name_load_per_area: the name of the parameter to use for the load per area
    para_name_load_manual: the name of the parameter to use for the load manual
    para_name_target: the name of the parameter to use for the target, ex: "Exit 1+Exit 2"
    para_name_egress_id: the name of the parameter to use for the egress id, ex: "Stair 1", "Stair 2", "Exit 1", "Exit 2"
    para_name_door_width: the name of the parameter to use for the door width
    para_name_door_required: the name of the parameter to use for the door capacity required
    para_name_stair_width: the name of the parameter to use for the stair width
    """
    def __init__(self, source,
                 para_name_load_per_area,
                 para_name_load_manual,
                 para_name_target,
                 para_name_egress_id,
                 para_name_door_width,
                 para_name_door_capacity_required,
                 para_name_stair_width,
                 area_scheme_name = None,
                 ):
        self.Source = source# "Area" or "Room"
        self.AreaSchemeName = area_scheme_name
        self.ParaNameLoadPerArea = para_name_load_per_area
        self.ParaNameLoadManual = para_name_load_manual
        self.ParaNameTarget = para_name_target
        self.ParaNameEgressId = para_name_egress_id
        self.ParaNameDoorWidth = para_name_door_width
        self.ParaNameDoorCapacityRequired = para_name_door_capacity_required
        self.ParaNameStairWidth = para_name_stair_width


def update_life_safety(doc, data_source):

    LifeSafetyChecker(doc, data_source).run_check()
    NOTIFICATION.messenger("Life Safety updated")


def purge_tags_on_non_egress_door(doc, tag_family_name, tag_family_type_name, key_para_name = "Door_$LS_Exit Name"):
    
    family_type = REVIT_FAMILY.get_family_type_by_name(tag_family_name, tag_family_type_name, doc=doc)
    if not family_type:
        print ("Cannot find tag family type [{}]".format(tag_family_type_name))
        return

    tags = REVIT_SELECTION.get_all_instances_of_type(family_type)
    tags = [el for el in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_DoorTags).WhereElementIsNotElementType().ToElements() if el.GetTypeId() == family_type.Id]

    for tag in tags:
        host_refs = list(tag.GetTaggedReferences())
        if len(host_refs) == 0:
            continue
        for host_ref in host_refs:
            host = doc.GetElement(host_ref.ElementId) or doc.GetElement(host_ref.LinkedElementId)

            if not host.LookupParameter(key_para_name) or not host.LookupParameter(key_para_name).HasValue or host.LookupParameter(key_para_name).AsString() == "":
                doc.Delete(tag.Id)



def display_room_targets(doc, views, key_para_name = "Rooms_$LS_Occupancy Load_Target"):
    """
    display a graphic on each room that show the target of the room
    """
    if not views:
        return
    if not isinstance(views, list):
        views = [views]
    from pyrevit import script
    output = script.get_output()
    graphic_datas = []
    target_color_map = {}
    for view in views:
        print ("Displaying egress targets on [{}]".format(output.linkify(view.Id, title = view.Name)))
        all_rooms = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
        for room in all_rooms:
            room_target = room.LookupParameter(key_para_name).AsString()
            if room_target not in target_color_map:
                target_color_map[room_target] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            color = target_color_map[room_target]
            image = IMAGE.create_bitmap_text_image(text = room_target, size = (128, 32), bg_color = color)
            graphic_data = REVIT_VIEW.GraphicDataItem(room.Location.Point, additional_info={"description":"Egress Targets: {}".format(room_target)}, image = image)
            graphic_datas.append(graphic_data)

        
    REVIT_VIEW.show_in_convas_graphic(graphic_datas, doc = doc, view = view)

##########################################################################
# egress path reflated
##########################################################################

class EgressPathManager:
    def __init__(self, doc, schedule_name, egress_path_family_name, egress_path_family_path, egress_path_tag_family_name, egress_path_tag_family_path):
        self.doc = doc
        self.schedule_name = schedule_name
        self.egress_path_family_name = egress_path_family_name
        self.egress_path_family_path = egress_path_family_path
        self.egress_path_tag_family_name = egress_path_tag_family_name
        self.egress_path_tag_family_path = egress_path_tag_family_path
        self.para_name_egress_path_path_id = "EgressPath_ID"
        self.para_name_egress_path_total = "EgressPath_TotalLength"
        self.para_name_egress_level = "EgressPath_Level"

    def secure_egress_path_family_package(self):
        family = REVIT_FAMILY.get_family_by_name(self.egress_path_family_name, doc=self.doc)
        if family is None:
            t = DB.Transaction(self.doc, "Create Egress Path Marker Family")
            t.Start()
            family = REVIT_FAMILY.get_family_by_name(self.egress_path_family_name, doc=self.doc, load_path_if_not_exist=self.egress_path_family_path)
            t.Commit()

        tag_family = REVIT_FAMILY.get_family_by_name(self.egress_path_tag_family_name, doc=self.doc)
        if tag_family is None:
            t = DB.Transaction(self.doc, "Create Egress Path Tag Family")
            t.Start()
            tag_family = REVIT_FAMILY.get_family_by_name(self.egress_path_tag_family_name, doc=self.doc, load_path_if_not_exist=self.egress_path_tag_family_path)
            t.Commit()
        return family, tag_family

    def update_all_egress_marker_family(self):
        t = DB.Transaction(self.doc, "Update All Egress Path Marker Family")
        t.Start()
        options = ["Show Note", "Hide Note"]
        res = REVIT_FORMS.dialogue(main_text="Do you want to show or hide the note on the egress path marker?", options=options)
        hide_note = res == options[0]
        all_type_names = REVIT_FAMILY.get_all_types_by_family_name(self.egress_path_family_name, doc=self.doc, return_name=True)
        for family_type_name in all_type_names:
            self.process_type(family_type_name, hide_note)
        t.Commit()

    def process_type(self, family_type_name, hide_note):
        family_type = REVIT_FAMILY.get_family_type_by_name(self.egress_path_family_name, family_type_name, doc=self.doc)
        family_type.LookupParameter("Type Comments").Set(family_type_name)
        family_type.LookupParameter("show_note").Set(hide_note)

        instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(self.egress_path_family_name, family_type_name, doc=self.doc)
        egress_dict = {}
        for instance in instances:
            view_scale = self.doc.GetElement(instance.OwnerViewId).Scale
            instance.LookupParameter("ScaleFactor_desired").Set(view_scale)
            instance.LookupParameter(self.para_name_egress_level).Set(self.doc.GetElement(instance.OwnerViewId).GenLevel.Name)

            path_id = instance.LookupParameter(self.para_name_egress_path_path_id).AsString() or "No Path ID"
            instance.LookupParameter(self.para_name_egress_path_path_id).Set(path_id)
            egress_dict.setdefault(path_id, []).append(instance)

        for path_id, instances in egress_dict.items():
            total_length = sum(instance.LookupParameter("Length").AsDouble() for instance in instances)
            for instance in instances:
                instance.LookupParameter(self.para_name_egress_path_total).Set(total_length)

    def create_egress_schedule(self):
        t = DB.Transaction(self.doc, "Create Egress Schedule")
        t.Start()
        family = REVIT_FAMILY.get_family_by_name(self.egress_path_family_name, doc=self.doc)
        field_names = ["Family", "Type Comments", self.para_name_egress_level, self.para_name_egress_path_path_id, self.para_name_egress_path_total]
        view = REVIT_SCHEDULE.create_schedule(self.doc, self.schedule_name, field_names, built_in_category=DB.BuiltInCategory.OST_DetailComponents)
        try:
            if REVIT_FAMILY.is_family_used(self.egress_path_family_name, doc=self.doc):
                pass
            t.Commit()
        except Exception as e:
            print(traceback.format_exc())
            t.RollBack()

def smart_egress_path(doc, schedule_name, egress_path_family_name, egress_path_family_path, egress_path_tag_family_name, egress_path_tag_family_path):
    manager = EgressPathManager(doc, schedule_name, egress_path_family_name, egress_path_family_path, egress_path_tag_family_name, egress_path_tag_family_path)
    manager.secure_egress_path_family_package()
    view = REVIT_VIEW.get_view_by_name(schedule_name, doc=doc)
    if view is None:
        manager.create_egress_schedule()
    manager.update_all_egress_marker_family()
