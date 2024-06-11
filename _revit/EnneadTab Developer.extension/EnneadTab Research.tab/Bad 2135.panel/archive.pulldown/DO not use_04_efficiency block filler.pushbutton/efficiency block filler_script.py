__doc__ = "DO NOT USE, use the new filler tool"
__title__ = "DO not USE_04_efficiency block data filler"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab

def get_element_level(element):

    #print element.LevelId
    #print revit.doc.GetElement( element.LevelId)
    try:

        level = revit.doc.GetElement( element.LevelId).Name.split("LEVEL ")[1].replace("(REFUGE)", "")
    except:
        level = 99
        print("cannot find level for {}".format(output.linkify(element.Id)))
    return level

def print_all_para(element):
    print("^"*10)
    for para in element.Parameters:
        #print para.Definition.Name
        if para.Definition.Name == "Workstation Occupancy":
            print("*"*50)
    print("/"*10)

def print_element_link(el):
    print("{}".format(output.linkify(el.Id)))

def get_all_efficiency_data_blocks():
    all_symbol_types =  DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.Family.Name == "Office Efficiency Calculator", all_symbol_types)


def get_data_block_by_level(level, data_blocks):
    filter(lambda x: x.LookupParameter("Type Name").AsString() == "Office Efficiency Calculator", all_symbol_types)
    pass

def get_all_sgl_workstations():
    primary_option_filter = DB.PrimaryDesignOptionMemberFilter()
    all_furnichures_in_primary_option = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Furniture).WherePasses(primary_option_filter).WhereElementIsNotElementType().ToElements()

    all_furnichures_raw = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()
    all_furnichures_in_main_model = filter(lambda x: x.DesignOption == None, all_furnichures_raw)

    all_furnichures = list(all_furnichures_in_primary_option) + all_furnichures_in_main_model
    #for x in all_furnichures:
        #print x
        #print_all_para(x.Symbol)
    workstation_furnichures = filter(lambda x: x.Symbol.LookupParameter("Workstation Occupancy") != None, all_furnichures)
    single_workstations = filter(lambda x: x.Symbol.LookupParameter("Description").AsString() == "Workstation(1 person)", workstation_furnichures)
    return single_workstations

def get_worksation_count_by_level(level):
    global single_workstations
    #print workstation_furnichures
    """
    for x in workstation_furnichures:
        print_element_link(x)
        """
    #print all_furnichures[0]
    #print_all_para(all_furnichures[0])
    #print get_element_level(all_furnichures[0])
    level_workstations = filter(lambda x: get_element_level(x) == level, single_workstations)
    count = 0
    safety = 0


    for furnichure in level_workstations:
        safety += 1
        #print "safety:{}".format(safety)
        if safety > 5000:
            break
        #print furnichure.Symbol#.Name
        #print_all_para(furnichure.Symbol)
        #if hasattr(furnichure.Symbol, "Workstation Occupancy"):
        count += furnichure.Symbol.LookupParameter("Workstation Occupancy").AsInteger()
            #print "found one----------------------"

    #print count
    return count

def get_GFA_area_by_level(level):
    all_areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    all_GFAs =  filter(lambda x: x.AreaScheme.Name == "Gross Building" and x.LookupParameter("Area Department").AsString() == "OFFICE", all_areas)
    return filter(lambda x: level == get_element_level(x), all_GFAs)

def get_function_area_by_level(level):

    GFA_in_level = get_GFA_area_by_level(level)


    net_office_area = 0
    core_area = 0
    other_area = 0
    for area in GFA_in_level:
        """
        if level == str(9):
            print(area.LookupParameter("Name").AsString())
            print(EA_UTILITY.sqft_to_sqm(area.Area))
        """
        area_function = area.LookupParameter("Area Layout Function").AsString()
        temp_area = area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble()

        if area_function == "NET OFFICE":
            net_office_area += temp_area
        elif area_function == "CORE":
            core_area += temp_area
        else:
            other_area += temp_area
    #EA_UTILITY.sqft_to_sqm(x)

    return net_office_area, core_area, other_area



def set_data_to_data_block(data_block):

    print("*"*20)
    level = data_block.LookupParameter("Type Name").AsString().split("level ")[1]
    print(level)
    workstation_count = get_worksation_count_by_level(level)
    print("workstation count = {}".format(workstation_count))
    data_block.LookupParameter("workstation count").Set(workstation_count)


    net_office_area, core_area, other_area = get_function_area_by_level(level)
    print("net_office_area = {}".format(EA_UTILITY.sqft_to_sqm(net_office_area)))
    print("core_area = {}".format(EA_UTILITY.sqft_to_sqm(core_area)))
    print("amenity_area = {}".format(EA_UTILITY.sqft_to_sqm(other_area)))
    data_block.LookupParameter("net office area").Set(net_office_area)
    data_block.LookupParameter("core area").Set(core_area)
    data_block.LookupParameter("amenity area").Set(other_area)


    #sepearte net office, amenity and core
    pass
################## main code below #####################
output = script.get_output()
output.close_others()

single_workstations = get_all_sgl_workstations()

with revit.Transaction("Filler blocks"):
    map(set_data_to_data_block, get_all_efficiency_data_blocks())
