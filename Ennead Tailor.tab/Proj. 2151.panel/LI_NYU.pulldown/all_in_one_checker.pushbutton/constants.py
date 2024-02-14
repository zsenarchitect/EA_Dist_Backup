import EnneadTab
from collections import OrderedDict
# data_file = EnneadTab.read_json_as_dict_in_dump_folder("LI_NYU_area.json")



# in future ther could be running this updates for mutiple desiong options
OPTION_NAME = ""
SURFIX = "" if len(OPTION_NAME) == 0 else "_{}".format(OPTION_NAME)



CALCULATOR_FAMILY_NAME = "EnneadTab AreaData Calculator{}".format(SURFIX)


CALCULATOR_CONTAINER_VIEW_NAME = "EnneadTab Area Calculator Collection{}".format(SURFIX)
FINAL_SCHEDULE_VIEW_NAME = "PROGRAM CATEGORY{}".format(SURFIX)

DEPARTMENT_AREA_SCHEME_NAME = "1_Department"
DEPARTMENT_KEY_PARA = "Area_$Department" # this is the area parameter used to lookup category


# KEY = REVIT ASSIGNED DEPARTMENT, VALUE = NICKNAME USED IN CALCUATOR FAMILY AND EXCEL AND  AREADATA CLASS
DEPARTMENT_PARA_MAPPING = {"DIAGNOSTIC AND TREATMENT": "D&T",
                           "AMBULATORY CARE": "AMBULATORY CARE",
                           "EMERGENCY DEPARTMENT": "ED",
                           "INPATIENT CARE": "BEDS",
                           "PUBLIC SUPPORT": "PUBLIC SUPPORT",
                           "ADMINISTRATION AND STAFF SUPPORT": "ADMIN",
                           "CLINICAL SUPPORT": "CLINICAL SUPPORT",
                           "BUILDING SUPPORT": "BUILDING SUPPORT",
                           "UNASSIGNED": "UNASSIGNED"}

# in the department area plan, if category fall into the IGNORE list, then it will not alert such discovery. This way only the mis spelled and unintentional category is alerted.
DEPARTMENT_IGNORE_PARA_NAMES = ["PUBLIC CIRCULATION",
                                "SERVICE CIRCULATION"]

PARA_TRACKER_MAPPING = {"MECHANICAL": "MERS"} # mech is not part of department calc
PARA_TRACKER_MAPPING.update(DEPARTMENT_PARA_MAPPING)


#
OVERALL_AREA_SCHEME_NAME = "1_T Tower Gross Building"
OVERALL_PARA_NAME = "GSF"



FACTOR_PARA_NAME = "FACTOR" #the discount value, this should be typed in in proj
DESIGN_SF_PARA_NAME = "DGSF TAKEOFF" 
ESTIMATE_SF_PARA_NAME = "DGSF ESTIMATE"

INTERNAL_PARA_NAMES = {"title":"LEVEL", "order":"order"}

FAMILY_PARA_COLLECTION = INTERNAL_PARA_NAMES.values() + [OVERALL_PARA_NAME,  DESIGN_SF_PARA_NAME, FACTOR_PARA_NAME, ESTIMATE_SF_PARA_NAME] + PARA_TRACKER_MAPPING.values() 
SCHEDULE_FIELD_ORDER = INTERNAL_PARA_NAMES.values() + [OVERALL_PARA_NAME,  DESIGN_SF_PARA_NAME, FACTOR_PARA_NAME, ESTIMATE_SF_PARA_NAME] + ["D&T","AMBULATORY CARE","ED","BEDS","PUBLIC SUPPORT","ADMIN","CLINICAL SUPPORT","BUILDING SUPPORT","UNASSIGNED"]


# in the setting file to set which level to run calc
LEVEL_NAMES = ["L0",
               "L1",
               "L2",
               "L3",
               "L4",
               "L5",
               "L6",
               "L7",
               "L8",
               "L9",
               "L10",
               "L11",
               "L12",
               "L13",
               "L14",
               "L15"]

# TO-DO: this dummy will pretend to be the excel button sum
DUMMY_DATA_HOLDER = ["GRAND TOTAL",
                     "PROGRAM TARGET",
                     "DELTA"]

# thia type name collection is to contain all and exact type names for the caulator
TYPE_NAME_COLLECTION = LEVEL_NAMES + DUMMY_DATA_HOLDER


