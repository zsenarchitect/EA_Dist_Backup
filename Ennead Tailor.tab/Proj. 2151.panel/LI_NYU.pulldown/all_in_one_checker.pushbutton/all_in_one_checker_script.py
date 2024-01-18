#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = "Basic area summery checker that update the data in special calculator. \n\nThis is also hooked to the sync event for this project. Request by Gayatri"
__title__ = "All In One Checker"

# from pyrevit import forms #
from pyrevit import script

import ENNEAD_LOG
import EnneadTab
import random
from Autodesk.Revit import DB  # fastest DB
# from Autodesk.Revit import UI
try:
    doc = __revit__.ActiveUIDocument.Document
except:
    pass



import os
import sys
sys.path.append((os.path.realpath(os.path.dirname(__file__))))

from area_data_class import AreaData
import utility


from constants import LEVEL_NAMES, DUMMY_DATA_HOLDER
from constants import PARA_TRACKER_MAPPING, OVERALL_PARA_NAME,FAMILY_PARA_COLLECTION, DEPARTMENT_IGNORE_PARA_NAMES,INTERNAL_PARA_NAMES
from constants import FACTOR_PARA_NAME, DESIGN_SF_PARA_NAME,ESTIMATE_SF_PARA_NAME
from constants import DEPARTMENT_AREA_SCHEME_NAME, OVERALL_AREA_SCHEME_NAME
from constants import DEPARTMENT_KEY_PARA


"""


for future abstract version, can process such that calculator family 
is opened by familymamager and validate to have such para meters. 

if famioly not found, will copy to dump folder and open.

If missing, will add missing parameter as area type
Load back to project

if symbol not activated. duplicate type until the all name of type match the names of level to check, place at EA_SPECIAL VIEW. Delete types who name is not in LevelNames list




some of the step need to be shared by seting maker.
The setting of the profile is saved in a L drive dict by project name
"""


class InternalCheck:
    """the main class for hosting method about area summery
    """

    def __init__(self, doc, show_log):
        self.doc = doc
        self.show_log = show_log
        self._found_bad_area = False
        
        AreaData.purge_data()
       

        from validator import validate_all
        self.validate_all = validate_all
        # this is the only func to import for the vaidation

    def collect_all_area_data(self):
        self.collect_area_data_action(DEPARTMENT_AREA_SCHEME_NAME, DEPARTMENT_KEY_PARA, PARA_TRACKER_MAPPING)
        self.collect_area_data_action(OVERALL_AREA_SCHEME_NAME, None, None)

    def collect_area_data_action(self, area_scheme_name, search_key_name, para_mapping):
        # get all the areas
        all_areas = DB.FilteredElementCollector(self.doc).OfCategory(
            DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name == area_scheme_name, all_areas)

        # add info to dataItem
        for area in all_areas:
            level = area.Level
            if level.Name not in LEVEL_NAMES:
                if self.show_log:
                    print("Area is on [{}], which is not a tracking level....{}".format(level.Name,
                                                                                        output.linkify(area.Id)))
                continue

            if not level:
                if self.show_log:
                    print("Area has no level, might not be placed....{}".format(
                        output.linkify(area.Id)))
                continue

            if area.Area <= 0:
                if self.show_log:

                    print("\nArea has no area number!\nIt might not be enclosed or placed....{} @ Level [{}] @ [{}]".format(output.linkify(area.Id),
                                                                                                   level.Name,
                                                                                                   area_scheme_name))
                else:
                    info = DB.WorksharingUtils.GetWorksharingTooltipInfo(self.doc, area.Id)
                    editor = info.LastChangedBy
                    print("\nArea has no area number!....Last edited by [{}]\nIt might not be enclosed or placed. Run in manual mode to find out more detail.".format(editor))
                    
                self._found_bad_area = True
                continue
            
        

            level_data = AreaData.get_data(level.Name)

            if search_key_name:
                department_name = area.LookupParameter(DEPARTMENT_KEY_PARA).AsString()
                if department_name in DEPARTMENT_IGNORE_PARA_NAMES:
                    
                    continue
                department_nickname = para_mapping.get(department_name, None)
                if not department_nickname:
                    if self.show_log:

                        print("Area has department value [{}] not matched any thing in excel....{}".format(department_name,
                                                                                                           output.linkify(area.Id)))
                    else:
                        print("Area has department value [{}] not matched any thing in excel. Run in tailor mode to find out which.".format(
                            department_name))
                    continue
                level_data.update(department_nickname, area.Area)
                     
                    
     
                

            else:
                # this is for the GSF senario, everything will count.
                level_data.update(OVERALL_PARA_NAME, area.Area)

            
    

            
            


    def update_main_calculator_family_types(self):
        # for each data item, get the calcator family and update content
        t = DB.Transaction(self.doc, __title__ + "_Part 1")
        t.Start()
        for type_name in sorted(LEVEL_NAMES):
            if self.show_log:
                print("Processing data for Level: [{}]".format(type_name))
            level_data = AreaData.get_data(type_name)

            # get actual calculator types
            calc_type = utility.get_calculator_type_by_type_name(self.doc, type_name)

            # since validation is impleteed early on, the below check is no longer nessary...
            # if not calc_type:

            #     if self.show_log:
            #         print("   --No calculator found for level: {}".format(type_name))
            #     else:
            #         print(
            #             "   --No calculator found for level. Run in tailor mode to find out which.")

            if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(calc_type):
                print("Cannot update [{}] due to ownership by {}.. Skipping".format(type_name,
                                                                                    EnneadTab.REVIT.REVIT_SELECTION.get_owner(calc_type)))
                continue

            # process the content
            factor = calc_type.LookupParameter(FACTOR_PARA_NAME).AsDouble()
            level_data.factor = factor #adding new fator attr to the class instance



            # fill in department related data
            design_GSF_before_factor = 0
            for family_para_name in PARA_TRACKER_MAPPING.values() + [OVERALL_PARA_NAME]:
                if not hasattr(level_data, family_para_name):
                    setattr(level_data, family_para_name, 0)

                if family_para_name in PARA_TRACKER_MAPPING.values():
                    if family_para_name == "MERS":
                        pass
                    else:
                        design_GSF_before_factor += getattr(level_data, family_para_name)

                para = calc_type.LookupParameter(family_para_name)
                """this part of para availibility check is no longer needed becasue para names are valided before loading"""
                if para:
                    if family_para_name in [OVERALL_PARA_NAME, "MERS"]:
                        local_factor = 1
                    else:
                        local_factor = level_data.factor
                    factored_area = getattr(level_data, family_para_name)* local_factor
                    para.Set(factored_area)
               
                else:
                    print("No para found for [{}], please edit the family..".format(family_para_name))


            # fill in GSF data
            design_SF_para = calc_type.LookupParameter(DESIGN_SF_PARA_NAME)
            design_SF_para.Set(design_GSF_before_factor)
            estimate_SF_para = calc_type.LookupParameter(ESTIMATE_SF_PARA_NAME)
            estimate_SF_para.Set(design_GSF_before_factor * level_data.factor)
            
            # below check is no longer needed becasue ealier check
            # if design_SF_para:
            #     design_SF_para.Set(design_GSF_before_factor)
            # else:
            #     print("No para found for [{}], please edit the family..".format(
            #         DESIGN_SF_PARA_NAME))

        t.Commit()


    def update_summery_calculator_family_types(self):
        t = DB.Transaction(self.doc, __title__ + "_Part 2")
        t.Start()
        for i,type_name in enumerate( DUMMY_DATA_HOLDER):
            if self.show_log:
                print ("Processing data for Summery Data Block [{}]".format(type_name))

            
            calc_type = utility.get_calculator_type_by_type_name(self.doc, type_name)         
            if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(calc_type):
                print("AHHHHHHHHHHH!   Cannot update [{}] due to ownership by {}.. Skipping".format(type_name,
                                                                                    EnneadTab.REVIT.REVIT_SELECTION.get_owner(calc_type)))
                continue
            
            
            if i == 0:
                self.fill_dummy_sum(type_name)
            elif i == 1:
                self.fetch_dummy_target(type_name)
                pass
            elif i == 2:
                self.fill_delta_data(type_name)
            
        t.Commit()
            
    
    def fill_dummy_sum(self, type_name):
        dummy_sum_data = AreaData.get_data(type_name)

        
        for level in LEVEL_NAMES:
            level_calc_type = utility.get_calculator_type_by_type_name(self.doc, level)
            for para_name in  FAMILY_PARA_COLLECTION:
                if para_name == FACTOR_PARA_NAME:
                    setattr(dummy_sum_data,para_name, 1)
                    continue
                if para_name in INTERNAL_PARA_NAMES.values():
                    continue
                value = level_calc_type.LookupParameter(para_name).AsDouble()
                dummy_sum_data.update(para_name, value)
                
     
            
        
        dummy_calc_type = utility.get_calculator_type_by_type_name(self.doc, type_name)
        for para_name in FAMILY_PARA_COLLECTION:
            if para_name in INTERNAL_PARA_NAMES.values():
                continue
            para = dummy_calc_type.LookupParameter(para_name)
            para.Set(getattr(dummy_sum_data, para_name))
          

    def fetch_dummy_target(self, type_name):
        dummy_target_data = AreaData.get_data(type_name)

 
        
        dummy_target_type = utility.get_calculator_type_by_type_name(self.doc, type_name)
        for para_name in  FAMILY_PARA_COLLECTION:
            if para_name == FACTOR_PARA_NAME:
       
                setattr(dummy_target_data,para_name, 1)
                continue
            if para_name in INTERNAL_PARA_NAMES.values():
                continue
            value = dummy_target_type.LookupParameter(para_name).AsDouble()
            dummy_target_data.update(para_name, value)
                
     
            
        
        
    def fill_delta_data(self, type_name):
        """maybe should worry about making smaller commit so doc is updated before geting data dfrom type data"""
        dummy_sum_data = AreaData.get_data(DUMMY_DATA_HOLDER[0])
        dummy_tartget_data = AreaData.get_data(DUMMY_DATA_HOLDER[1])
        dummy_delta_data = AreaData.get_data(type_name)
        
 
 
       
        dummy_delta_type = utility.get_calculator_type_by_type_name(self.doc, type_name)
        for para_name in FAMILY_PARA_COLLECTION:
            if para_name == FACTOR_PARA_NAME:
                setattr(dummy_delta_data,para_name, 1)
                dummy_delta_type.LookupParameter(para_name).Set(1)
                continue
            if para_name in INTERNAL_PARA_NAMES.values():
                continue
            
            value_real = getattr(dummy_sum_data,para_name)
            value_manual = getattr(dummy_tartget_data, para_name)
            delta = value_real - value_manual
            dummy_delta_data.update(para_name, delta)
            
            dummy_delta_type.LookupParameter(para_name).Set(delta)
            
            
  
          
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def run_check(self):

        T = DB.TransactionGroup(self.doc, __title__)
        T.Start()

        if not self.validate_all(self):
            EnneadTab.NOTIFICATION.messenger(main_text="Cannot proceed further before all setup is validated.")
            T.Rollback()
            return

        self.collect_all_area_data()
        
        self.update_main_calculator_family_types()
        self.update_summery_calculator_family_types()
        T.Commit()
        
        
        if self.show_log:
            EnneadTab.NOTIFICATION.messenger(main_text="Program schedule calculator update done!")

        
        if self._found_bad_area:
            EnneadTab.NOTIFICATION.messenger(main_text="Attention, there are some un-enclosed area in area plans that might affect your accuracy.\nSee output window for details.")

        


#############################################################################


@EnneadTab.ERROR_HANDLE.try_catch_error
def all_in_one_checker(doc, show_log):
    """this is the main doc
    passing doc and show_log para to make sure using this as button VS using it
    during sync event hook can both work"""

    InternalCheck(doc, show_log).run_check()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    all_in_one_checker(doc, show_log=True)

    # record usage data to minbank
    ENNEAD_LOG.use_enneadtab(
        coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)
