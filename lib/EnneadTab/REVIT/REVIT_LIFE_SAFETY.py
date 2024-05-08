
try:
    from pyrevit import script
    from Autodesk.Revit import DB
except:
    pass


import math

from EnneadTab import NOTIFICATION


class EgressData:
    data_collection = dict()
    
    @classmethod
    def egress_id_exist(cls, test_id):
        for data in cls.data_collection.values():
            if data.egress_id == test_id:
                return True
        return False
    
    @property
    def is_stair(self):
        return "stair" in self.egress_id.lower()
    
    def __init__(self, level_name, egress_id):
        self.level = level_name
        self.egress_id = egress_id

        self.revit_obj_collection = []
        self.occupancy_load = 0
        self.total_width = 0
        self.source_rooms = []

    @classmethod
    def get_data(cls, level_name, egress_id):
        key = (level_name, egress_id)
        if key in cls.data_collection:
            return cls.data_collection[key]
        if "stair" in egress_id.lower():
            
            instance = StairData(level_name, egress_id)
        else:
             instance = DoorData(level_name, egress_id)
        cls.data_collection[key] = instance
        return instance
    
    def add_room_occupancy_load(self, room, branch_count): 
        self.source_rooms.append(room)
        room_final_capacity = get_room_final_capacity(room)
        # only add occpancy portioned to this data
        self.occupancy_load += int(math.ceil(room_final_capacity / float(branch_count)))
        
    def print_data(self, show_log):
        if show_log or len(self.revit_obj_collection) == 0:
            print ("\n{} {} has {} items with {} occupancy capacity and {}feet total width".format(self.level, self.egress_id, len(self.revit_obj_collection), self.occupancy_load, self.total_width))
        if len(self.revit_obj_collection) > 0:
            if show_log:
                print ("The items are: ")
                for item in self.revit_obj_collection:
                    print (output.linkify(item.Id, title = str(item.GetType())))
        else:
            print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nNo item with this egress id {}. There are rooms point to this egress adress but no revit object is actually using this address.Talk to Sen Zhang for details for what it means.".format(self.egress_id))
            if show_log:
                for room in self.source_rooms:
                    print (output.linkify(room.Id, title = room.LookupParameter("Name").AsString()))


class DoorData(EgressData):

    def add_door(self, door):

        self.revit_obj_collection.append(door)
        self.total_width += get_door_width(door)
        
class StairData(EgressData):
    def add_stair(self, stair):
        
        self.revit_obj_collection.append(stair)
        if len(self.revit_obj_collection) > 1:
            print ("This should not have more than one stair with this egreeId {} , please check".format(self.egress_id))
            if self.show_log:
                for stair in self.revit_obj_collection:
                    print (output.linkify(stair.Id))
        self.total_width = get_stair_width(stair)



def get_door_width(door):
    try:
        return door.LookupParameter("Width").AsDouble()
    except:
        return door.Symbol.LookupParameter("Width").AsDouble()
    
def get_stair_width(stair):
    runs = [stair.Document.GetElement(x) for x in stair.GetStairsRuns()]
    
    max_width = runs[0].ActualRunWidth
    for run in runs:
        if not  run.ActualRunWidth == max_width:
            print( "--This stair has variring  run width--->{}. Talk to Sen Zhang to understand what it means.".format(output.linkify(run.Id)))
    return max_width
    



def get_all_calculators(doc):
    all_symbols = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.FamilyName == "Stair Life Safety Calculator", all_symbols)


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)


def get_calculators_by_key(doc, level_name, egress_id):

    return filter(lambda x: x.LookupParameter("Level_Name").AsString() == level_name and x.Symbol.LookupParameter("Egress Id").AsString() == egress_id, get_all_calculators(doc))

def get_calculator_type_by_egress_id(doc, egress_id):

    list =  filter(lambda x: x.LookupParameter("Egress Id").AsString() == egress_id, get_all_calcuator_types(doc))
    if len(list) > 0:
        return list[0]
    return None


























class LifeSafetyChecker:
    def __init__(self, doc, data_source):
        self.doc = doc
        self.data_source = data_source
        self.output = script.get_output()

    def run_check(self):
        # loop thru all spatial element, either from area or from room. 
        cate = DB.BuiltInCategory.OST_Rooms if self.data_source.Source == "Room" else DB.BuiltInCategory.OST_Areas
        all_spatial_elements = DB.FilteredElementCollector(self.doc).OfCategory(cate).WhereElementIsNotElementType().ToElements()
        if len(all_spatial_elements) == 0:
            return

        # get a test spatial element to see if all needed parameter is valid
        tester = all_spatial_elements[0]
        for para_name in [self.data_source.ParaNameLoadPerArea,
                          self.data_source.ParaNameLoadManual,
                          self.data_source.ParaNameTarget]:
            if tester.LookupParameter(para_name) is None:
                NOTIFICATION.messenger("Missing <{}> for the spatial element".format(para_name))
                return
                          

        
        # for each egress data, 
            # collect final load number
            # find the target egress door and egress stair and egress exit of this spatial element, add to the load of that item data
        for spatial_element in all_spatial_elements:
            final_load = self.get_spatial_element_final_capacity(spatial_element)

            level_name = self.doc.GetElement(spatial_element.LevelId).Name
            target_list = self.get_spatial_element_target_list(spatial_element)

            # when a egress is assigned to A2+B2, the total load of this space need to divide to 2 parts and assign one each
            divider_count = len(target_list) 
            for target_name in target_list:
                local_load = int(math.ceil(final_load / float(divider_count)))
                target_door = DoorData.get_data(level_name, target_name)
                target_stair = StairData.get_data(level_name, target_name)
                target_door.add_load(local_load)
                target_stair.add_load(local_load)
            


        # for each item data, get a data calculator and update.
        # why not use revit obj directly? becasue stair can not easitl disply data by level. and stair and door if mixed in multi-category schdule can cause confusion, althoug it is technically possoble


    def get_spatial_element_target_list(self, spatial_element):
        target_list = spatial_element.LookupParameter(self.data_source.ParaNameTarget).AsString()
        if target_list == "" or target_list is None:
            target = "--No Egress Target--"
            print ("{}Target not assigned, please fix.".format(self.output.linkify(spatial_element.Id, title = spatial_element.LookupParameter("Name").AsString())))
            return []
        
        if "+" in target_list:
            target_list = target_list.split("+")
            target_list = [x.strip() for x in target_list]
        else:
            target_list = [target_list]

        return target_list

    def get_spatial_element_final_capacity(self, spatial_element):

        # ignore rooms whose AreaPerPerson is negative
        if spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble() < 0:
            return 0
        
        # pioritise manual override
        if spatial_element.LookupParameter(self.data_source.ParaNameLoadManual).AsInteger() >= 0:
            return spatial_element.LookupParameter(self.data_source.ParaNameLoadManual).AsInteger()
            

        return math.ceil(spatial_element.Area / spatial_element.LookupParameter(self.data_source.ParaNameLoadPerArea).AsDouble ())



#####################################################################################################################################

class SpatialDataSource:
    """use this format to define how to extract lfe safety data, 
    each project mght want to s=do sometingdifferently."""
    def __init__(self, source =  "Area" or "Room",
                 para_name_load_per_area = "Rooms_$LS_Occupancy AreaPer",
                 para_name_load_manual = "LSLoadManual",
                 para_name_target = "LSTarget"):
        self.Source = source
        self.ParaNameLoadPerArea = para_name_load_per_area
        self.ParaNameLoadManual = para_name_load_manual
        self.ParaNameTarget = para_name_target

def update_life_safety(doc, data_source):
    LifeSafetyChecker(doc, data_source).run_check()

