
from EnneadTab import DATA_CONVERSION, NOTIFICATION, SAMPLE_FILE, EXCEL, FOLDER, TIME
from EnneadTab.REVIT import REVIT_FAMILY, REVIT_VIEW, REVIT_SCHEDULE,REVIT_SPATIAL_ELEMENT,REVIT_SELECTION, REVIT_AREA_SCHEME, REVIT_PARAMETER
from pyrevit import forms, script
from Autodesk.Revit import DB #pyright: ignore
from collections import OrderedDict
import traceback

class DepartmentOption:


    DEPARTMENT_KEY_PARA = "get from project data para_dict" #default value "Area_$Department" 
    PROGRAM_TYPE_KEY_PARA = "get from project data para_dict" #default value "Area_$Department_Program Type"
    PROGRAM_TYPE_DETAIL_KEY_PARA = "get from project data para_dict" #default value "Area_$Department_Program Type Detail"



    # KEY = REVIT ASSIGNED DEPARTMENT, VALUE = NICKNAME USED IN CALCUATOR FAMILY AND EXCEL AND  AREADATA CLASS
    DEPARTMENT_PARA_MAPPING = "get from project data table setting"

    # in the department area plan, if category fall into the IGNORE list, then it will not alert such discovery. This way only the mis spelled and unintentional category is alerted.
    DEPARTMENT_IGNORE_PARA_NAMES = "get from project data setting"


    @property
    def PARA_TRACKER_MAPPING(self):
        temp = OrderedDict([("MECHANICAL", "MERS")]) # mech is not part of department calc
        temp.update(self.DEPARTMENT_PARA_MAPPING)
        return temp



    #
    OVERALL_AREA_SCHEME_NAME = "get from project data option setting" # deafult value "GFA Scheme"
    OVERALL_PARA_NAME = "GSF"

    DEPARTMENT_AREA_SCHEME_NAME = "get from project data option setting" # deafult value "DGSF Scheme"



    FACTOR_PARA_NAME = "FACTOR" #the discount value, this should be typed in in proj
    DESIGN_SF_PARA_NAME = "DGSF TAKEOFF" 
    ESTIMATE_SF_PARA_NAME = "DGSF ESTIMATE"

    INTERNAL_PARA_NAMES = {"title":"LEVEL", "order":"order"}


    @property
    def FAMILY_PARA_COLLECTION(self):
        return self.INTERNAL_PARA_NAMES.values() + [self.OVERALL_PARA_NAME,  self.DESIGN_SF_PARA_NAME, self.FACTOR_PARA_NAME, self.ESTIMATE_SF_PARA_NAME] + self.PARA_TRACKER_MAPPING.values() 
    



    # in the setting file to set which level to run calc
    LEVEL_NAMES = []
    

    DUMMY_DATA_HOLDER = ["GRAND TOTAL",
                        "PROGRAM TARGET",
                        "DELTA"]

    # thia type name collection is to contain all and exact type names for the caulator
    @property
    def TYPE_NAME_COLLECTION(self):
        return self.LEVEL_NAMES + self.DUMMY_DATA_HOLDER


    def __init__(self, 
                 internal_option_name,
                 department_para_mapping,
                 department_ignore_para_names,
                 levels, 
                 option_name, 
                 overall_area_scheme_name, 
                 department_area_scheme_name,
                 department_key_para_name,
                 program_type_key_para_name,
                 program_type_detail_key_para_name):
        self.internal_option_name = internal_option_name
        self.is_primary = True if len(option_name) == 0 else False
        self.formated_option_name = "Main Option" if self.is_primary else option_name


        self.LEVEL_NAMES = levels

        self.CALCULATOR_FAMILY_NAME_RAW = "EnneadTab AreaData Calculator"
        self.CALCULATOR_FAMILY_NAME = self.CALCULATOR_FAMILY_NAME_RAW
        self.CALCULATOR_CONTAINER_VIEW_NAME = "EnneadTab Area Calculator Collection"
        self.FINAL_SCHEDULE_VIEW_NAME = "PROGRAM CATEGORY"

        if not self.is_primary:
            self.CALCULATOR_FAMILY_NAME += "_{}".format(self.formated_option_name)
            self.CALCULATOR_CONTAINER_VIEW_NAME += "_{}".format(self.formated_option_name)
            self.FINAL_SCHEDULE_VIEW_NAME += "_{}".format(self.formated_option_name)


        self.OVERALL_AREA_SCHEME_NAME = overall_area_scheme_name
        self.DEPARTMENT_AREA_SCHEME_NAME = department_area_scheme_name

        self.DEPARTMENT_KEY_PARA = department_key_para_name
        self.PROGRAM_TYPE_KEY_PARA = program_type_key_para_name
        self.PROGRAM_TYPE_DETAIL_KEY_PARA = program_type_detail_key_para_name

        self.DEPARTMENT_PARA_MAPPING = department_para_mapping
        self.DEPARTMENT_IGNORE_PARA_NAMES = department_ignore_para_names

class OptionValidation:
    def __init__(self, doc, option, show_log):


        self.doc = doc
        self.option = option
        self.output = script.get_output()
        self.show_log = show_log

    def validate_all(self):
        if not self.is_area_scheme_valid():
            return False
        if not self.validate_family():
            return False
        if not self.validate_container_view():
            return False
        self.validate_schedule_view()
        self.is_family_types_valid()
        return True



    def validate_family(self):
        default_sample_family_path = SAMPLE_FILE.get_file("{}.rfa".format(self.option.CALCULATOR_FAMILY_NAME_RAW))
        sample_family_path = FOLDER.copy_file_to_local_dump_folder(default_sample_family_path, "{}.rfa".format(self.option.CALCULATOR_FAMILY_NAME))
        fam = REVIT_FAMILY.get_family_by_name(self.option.CALCULATOR_FAMILY_NAME, doc=self.doc, load_path_if_not_exist=sample_family_path)
        if not fam:
            return False
        return True

    def validate_container_view(self):
        # test if container view exist
        view = REVIT_VIEW.get_view_by_name(self.option.CALCULATOR_CONTAINER_VIEW_NAME, doc=self.doc)
        if view:
            return True

        t = DB.Transaction(self.doc, "Making Container View")
        t.Start()
        view = DB.ViewDrafting.Create(self.doc, 
                                      REVIT_VIEW.get_default_view_type("drafting").Id)
        view.Name = self.option.CALCULATOR_CONTAINER_VIEW_NAME
        view.Scale = 250
        t.Commit()
        return True

    def validate_schedule_view(self):
        # test if schedule view exist
        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)
        if not view:
            t = DB.Transaction(self.doc, "Making Final Schedule View")
            t.Start()
            view = DB.ViewSchedule.CreateNoteBlock(self.doc, REVIT_FAMILY.get_family_by_name(self.option.CALCULATOR_FAMILY_NAME, self.doc).Id ) 
            # view = DB.ViewSchedule.CreateSchedule (self.doc, 
            #                                         DB.Category.GetCategory(self.doc,
            #                                                                 DB.BuiltInCategory.OST_GenericAnnotation).Id)
            view.Name = self.option.FINAL_SCHEDULE_VIEW_NAME
            t.Commit()
            
        self.format_schedule()

        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)
        if self.show_log:
            print ("Schedule view at [{}]".format(self.output.linkify(view.Id, title = self.option.FINAL_SCHEDULE_VIEW_NAME)))



    def is_family_types_valid(self):

        #  1.make sure the entire collection of family types is exactly matching the level names, so perform the following two steps.
        # 1a, each type should have one and only one instance in the project
        self.validate_singular_instance()
       
        # 1b, removing unrelated type from the project.
        self.remove_unrelated_types()
    
        # 2.set order index for each type. This will set the display order in schdeule
        self.set_type_order_index()

 

    def validate_singular_instance(self):
        # make sure each type is placed exactly once
        for type_name in self.option.TYPE_NAME_COLLECTION:

            
            calcs = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
            if calcs is None:
                # make new type and place on the container view
                self.make_new_calcualtor(type_name)
                continue

            foot_note = "level [{}]".format(type_name) if type_name in self.option.LEVEL_NAMES else "dummy data block [{}]".format(type_name)
            if calcs is not None and len(calcs) == 1:
                
                """maybe consideering force the data block in containner view only, but maybe team wants to have it in area plan view."""
                continue

            # when it is not 1, I want to make sure it is 1!
            elif len(calcs) > 1:
                print("Too many calculator found for {}. Resetting now...".format(foot_note))
            else:
                print("No calculator found for level {}. Creating now...".format(foot_note))

            # try to purge this type first
            self.purge_type_by_name(type_name)

            # make new type and place on the container view
            self.make_new_calcualtor(type_name)


    def purge_type_by_name(self, type_name):
        calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
        if calc_type:
            t = DB.Transaction(self.doc, "Purge Useless Type")
            t.Start()
            self.doc.Delete(calc_type.Id)
            t.Commit()

    def make_new_calcualtor(self, type_name):
        t = DB.Transaction(self.doc, "Making new type [{}]".format(type_name))
        t.Start()
        new_type = REVIT_FAMILY.get_all_types_by_family_name(self.option.CALCULATOR_FAMILY_NAME, self.doc)[0].Duplicate(type_name)
        new_type.Activate()
        self.doc.Regenerate()

        
        
        unit_distant = 75
        if type_name in self.option.LEVEL_NAMES:
            index = self.option.LEVEL_NAMES.index(type_name)
            row_count = 5
            x, y = index % row_count, index // row_count
        if type_name in self.option.DUMMY_DATA_HOLDER:
            index = self.option.DUMMY_DATA_HOLDER.index(type_name)
            x = index
            y = -2
            
        self.doc.Create.NewFamilyInstance(DB.XYZ(unit_distant*x, unit_distant*y, 0), 
                                            new_type,
                                            REVIT_VIEW.get_view_by_name(self.option.CALCULATOR_CONTAINER_VIEW_NAME, doc = self.doc))
        t.Commit()
        
        
    def remove_unrelated_types(self):
        for calc_type in REVIT_FAMILY.get_all_types_by_family_name(self.option.CALCULATOR_FAMILY_NAME, self.doc):
            type_name = calc_type.LookupParameter("Type Name").AsString()

            if type_name not in self.option.TYPE_NAME_COLLECTION:
                print("Extra type [{}] found . Deleting now...".format(type_name))

                t = DB.Transaction(self.doc,"Delete extra type [{}]".format(type_name))
                t.Start()
                self.doc.Delete(calc_type.Id)
                t.Commit()



    def set_type_order_index(self):
        
        for calc_type in REVIT_FAMILY.get_all_types_by_family_name(self.option.CALCULATOR_FAMILY_NAME, self.doc):
            type_name = calc_type.LookupParameter("Type Name").AsString()
            if type_name in self.option.LEVEL_NAMES:
                order_index = len(self.option.LEVEL_NAMES) - self.option.LEVEL_NAMES.index(type_name)
            elif type_name in self.option.DUMMY_DATA_HOLDER:
                order_index = self.option.DUMMY_DATA_HOLDER[::-1].index(type_name) - 100
            else:
                print ("!!!!!!!!!!!!!!!!![{}], is not a valid type name".format(type_name))
            
                
                
            current_index = calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["order"]).AsInteger()
            current_level_display = calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["title"]).AsString()
            if current_index != order_index or current_level_display != type_name:
                print ("Fixing order index/title display of [{}]".format(type_name))
                t = DB.Transaction(self.doc, "Set order index for [{}]".format(type_name))
                t.Start()
                calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["title"]).Set(type_name)
                calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["order"]).Set(order_index)

                t.Commit()
                
                
                

    def format_schedule(self):

        # test if schedule has all required parameters as field
        # create a schedule with defined rules(get viewschedule.definition, then add field, and set order)
        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc = self.doc)

        t = DB.Transaction(self.doc, "Check schedule contents.")
        t.Start()
        definition = view.Definition
        field_names = []  
        for index in range(definition.GetFieldCount()):
            field = definition.GetField(index)
            field_names.append(field.GetName())
            
            
            # options = field.GetFormatOptions()
            # style = field.GetStyle()
            # overrideOptions = style.GetCellStyleOverrideOptions()
            # overrideOptions.BackgroundColor = True
            # style.BackgroundColor = DB.Color(100,100,100)
            
            
            if field.GetName() not in self.option.FAMILY_PARA_COLLECTION:
                print ("[{}] should not appear in the schedule field".format(field.GetName()))
                definition.RemoveFeild(field.Id)
        

        REVIT_SCHEDULE.add_fields_to_schedule(view, self.option.FAMILY_PARA_COLLECTION)
        REVIT_SCHEDULE.hide_fields_in_schedule(view, self.option.INTERNAL_PARA_NAMES["order"])

        # set group order descending
        definition = view.Definition
        sort_group_field = DB.ScheduleSortGroupField()
        sort_group_field.FieldId = REVIT_SCHEDULE.get_field_by_name(view, self.option.INTERNAL_PARA_NAMES["order"]).FieldId
        sort_group_field.SortOrder = DB.ScheduleSortOrder.Descending
        definition.SetSortGroupFields (DATA_CONVERSION.list_to_system_list([sort_group_field], type = DB.ScheduleSortGroupField, use_IList = False))
                
        # set all digits to round to 10
        for field in self.option.FAMILY_PARA_COLLECTION:
            field = REVIT_SCHEDULE.get_field_by_name(view, field)
            try:
                format_option = field.GetFormatOptions()
                format_option.UseDefault = False
                format_option.Accuracy = 10.0
                format_option.UseDigitGrouping = True
                field.SetFormatOptions(format_option)
            except:
                pass


            try:    
                table_cell_style = field.GetStyle()
                table_cell_style.FontHorizontalAlignment = DB.HorizontalAlignmentStyle.Right
                import random
                table_cell_style.BackgroundColor  = DB.Color(random.randint(0,255),random.randint(0,255),random.randint(0,255))
                field.SetStyle(table_cell_style)
            except:
                pass


                










        # set order
        # REVIT_SCHEDULE.sort_fields_in_schedule(view, self.option.FAMILY_PARA_COLLECTION)

        
        t.Commit()
        # TO-DO

        # test if each schedule field is the right format(align to right, digit grouping)
        # TO-DO
        pass


    def is_area_scheme_valid(self):

        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.OVERALL_AREA_SCHEME_NAME, self.doc)
        if not area_scheme:

            print("Area scheme [{}] not found for overall area scheme, please create it first".format(self.option.OVERALL_AREA_SCHEME_NAME))
            return False


        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.DEPARTMENT_AREA_SCHEME_NAME, self.doc)
        if not area_scheme:
            print("Area scheme [{}] not found for departmental scheme, please create it first".format(self.option.DEPARTMENT_AREA_SCHEME_NAME))
            return False

        return True



class AreaData:
    """the main class for holding area data on each level."""
    data_collection = dict()

    def __init__(self, type_name):
        self.title = type_name

    @classmethod
    def purge_data(cls):
        cls.data_collection.clear()
        
        
    @classmethod
    def get_data(cls, type_name):
        key = type_name
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = AreaData(type_name)

        cls.data_collection[key] = instance
        return instance

    def update(self, area_name, area):
        if not hasattr(self, area_name):
            setattr(self, area_name, area)
            return

        current_area = getattr(self, area_name)
        setattr(self, area_name, current_area + area)
        

class InternalCheck:
    """the main class for hosting method about area summery
    """

    def __init__(self, doc, option, show_log):
        self.doc = doc
        self.option = option
        self.show_log = show_log
        self.output = script.get_output()
        self._found_bad_area = False
        
        AreaData.purge_data()
       


    def collect_all_area_data(self):
        # collect data for deparmtnet details
        self.collect_area_data_action(self.option.DEPARTMENT_AREA_SCHEME_NAME, 
                                      self.option.DEPARTMENT_KEY_PARA, 
                                      self.option.PARA_TRACKER_MAPPING)

        # collect data for GFA
        self.collect_area_data_action(self.option.OVERALL_AREA_SCHEME_NAME, 
                                      None, 
                                      None)


        if not self.option.is_primary:
            self.copy_data_from_primary()


    def collect_area_data_action(self, area_scheme_name, search_key_name, para_mapping):
        """_summary_

        Args:
            area_scheme_name (_type_): _description_
            search_key_name (_type_): lookup para as key. If ommited, will count toward GFA
            para_mapping (_type_): abbr translation.If ommited, will count toward GFA
        """
        # get all the areas
        all_areas = DB.FilteredElementCollector(self.doc)\
                        .OfCategory(DB.BuiltInCategory.OST_Areas)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name == area_scheme_name, all_areas)

        # add info to dataItem
        for area in all_areas:
            level = area.Level
            if level.Name not in self.option.LEVEL_NAMES:
                if self.show_log:
                    print("Area is on [{}], which is not a tracking level....{}".format(level.Name,
                                                                                        self.output.linkify(area.Id)))
                continue

            if not level:
                if self.show_log:
                    print("Area has no level, might not be placed....{}".format(
                        self.output.linkify(area.Id)))
                continue

            if REVIT_SPATIAL_ELEMENT.is_element_bad(area):
                if self.show_log:
                    status = REVIT_SPATIAL_ELEMENT.get_element_status(area)

                    print("\nArea has no size!\nIt is {}....{} @ Level [{}] @ [{}]".format(status,
                                                                                           self.output.linkify(area.Id, area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString()),
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
                department_name = area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString()
                if department_name in self.option.DEPARTMENT_IGNORE_PARA_NAMES:
                    print ("Ignore {} for calculation at [{}]".format(self.output.linkify(area.Id, title=department_name), level.Name))
                    
                    continue
                department_nickname = para_mapping.get(department_name, None)
                if not department_nickname:

                    if self.show_log:

                        print("Area has department value [{}] not matched any thing in excel....{}@{}".format(department_name,
                                                                                                           self.output.linkify(area.Id),
                                                                                                           level.Name))
                    else:
                        print("Area has department value [{}] not matched any thing in excel. Run in tailor mode to find out which.".format(
                            department_name))
                    continue
                level_data.update(department_nickname, area.Area)
                     
                    
     
                

            else:
                # this is for the GSF senario, everything will count.
                level_data.update(self.option.OVERALL_PARA_NAME, area.Area)

    def copy_data_from_primary(self):
        
        """except BEDS, get all other area per level from OPTION_MAIN family type.

        first reset non BEDS to zero
        Second, go thru main option and get everything that is not BEDS and fill in.
        """
        #  reset all levels data where there is BED. SO later only update BEDS from main
        for type_name, data in AreaData.data_collection.items():
            # this is data per level
            if type_name not in self.option.LEVEL_NAMES:
                continue
            for attr_key in self.option.PARA_TRACKER_MAPPING.values():
                if attr_key != "BEDS":
                    setattr(data, attr_key, 0)



                
        all_areas = DB.FilteredElementCollector(self.doc)\
                        .OfCategory(DB.BuiltInCategory.OST_Areas)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name == self.option.DEPARTMENT_AREA_SCHEME_NAME, all_areas)

        for area in all_areas:
            level = area.Level
            if level.Name not in self.option.LEVEL_NAMES:
                continue

            if not level:
                continue

            if area.Area <= 0:
                continue
            


            department_name = area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString()
            if department_name in self.option.DEPARTMENT_IGNORE_PARA_NAMES:
                continue
            department_nickname = self.option.PARA_TRACKER_MAPPING.get(department_name, None)
            if department_nickname is not None and department_nickname != "BEDS":
                level_data = AreaData.get_data(level.Name)
                level_data.update(department_nickname, area.Area)





    
    def update_main_calculator_family_types(self):
        # for each data item, get the calcator family and update content
        t = DB.Transaction(self.doc, "_Part 1_update main calcuator family types")
        t.Start()
        for type_name in sorted(self.option.LEVEL_NAMES):
            if self.show_log:
                print("Processing data for Level: [{}]".format(type_name))
            level_data = AreaData.get_data(type_name)

            # get actual calculator types
            calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)

            # since validation is impleteed early on, the below check is no longer nessary...
            # if not calc_type:

            #     if self.show_log:
            #         print("   --No calculator found for level: {}".format(type_name))
            #     else:
            #         print(
            #             "   --No calculator found for level. Run in tailor mode to find out which.")

            if not REVIT_SELECTION.is_changable(calc_type):
                print("Cannot update [{}] due to ownership by {}.. Skipping".format(type_name,
                                                                                    REVIT_SELECTION.get_owner(calc_type)))
                continue

            # process the content
            factor = calc_type.LookupParameter(self.option.FACTOR_PARA_NAME).AsDouble()
            level_data.factor = factor #adding new fator attr to the class instance



            # fill in department related data
            design_GSF_before_factor = 0
            for family_para_name in self.option.PARA_TRACKER_MAPPING.values() + [self.option.OVERALL_PARA_NAME]:
                if not hasattr(level_data, family_para_name):
                    setattr(level_data, family_para_name, 0)

                if family_para_name in self.option.PARA_TRACKER_MAPPING.values():
                    if family_para_name == "MERS":
                        pass
                    else:
                        design_GSF_before_factor += getattr(level_data, family_para_name)

                para = calc_type.LookupParameter(family_para_name)
                """this part of para availibility check is no longer needed becasue para names are valided before loading"""
                if para:
                    if family_para_name in [self.option.OVERALL_PARA_NAME, "MERS"]:
                        local_factor = 1
                    else:
                        local_factor = level_data.factor
                    factored_area = getattr(level_data, family_para_name)* local_factor
                    para.Set(factored_area)
               
                else:
                    print("No para found for [{}], please edit the family..".format(family_para_name))


            # fill in GSF data
            design_SF_para = calc_type.LookupParameter(self.option.DESIGN_SF_PARA_NAME)
            design_SF_para.Set(design_GSF_before_factor)
            estimate_SF_para = calc_type.LookupParameter(self.option.ESTIMATE_SF_PARA_NAME)
            estimate_SF_para.Set(design_GSF_before_factor * level_data.factor)
            
            # below check is no longer needed becasue ealier check
            # if design_SF_para:
            #     design_SF_para.Set(design_GSF_before_factor)
            # else:
            #     print("No para found for [{}], please edit the family..".format(
            #         DESIGN_SF_PARA_NAME))

        t.Commit()


    def update_summery_calculator_family_types(self):
        t = DB.Transaction(self.doc, "_Part 2_update summery calcuator family types")
        t.Start()
        for i,type_name in enumerate( self.option.DUMMY_DATA_HOLDER):
            if self.show_log:
                print ("Processing data for Summery Data Block [{}]".format(type_name))

            
            calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)         
            if not REVIT_SELECTION.is_changable(calc_type):
                note = "AHHHHHHHHHHH!   Cannot update [{}] due to ownership by {}.. Skipping".format(type_name,
                                                                                    REVIT_SELECTION.get_owner(calc_type))
                print (note)

                NOTIFICATION.messenger(note)
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

        
        for level in self.option.LEVEL_NAMES:
            level_calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, level, self.doc)   
            for para_name in  self.option.FAMILY_PARA_COLLECTION:
                if para_name == self.option.FACTOR_PARA_NAME:
                    setattr(dummy_sum_data,para_name, 1)
                    continue
                if para_name in self.option.INTERNAL_PARA_NAMES.values():
                    continue
                value = level_calc_type.LookupParameter(para_name).AsDouble()
                dummy_sum_data.update(para_name, value)
                
     
            
        
        dummy_calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)    
        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue
            para = dummy_calc_type.LookupParameter(para_name)
            para.Set(getattr(dummy_sum_data, para_name))
          

    def fetch_dummy_target(self, type_name):
        dummy_target_data = AreaData.get_data(type_name)

 
        
        dummy_target_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)   

        # only update the internal para, which is Level Name and Order Number, also set factor as 1 as constant 
        for para_name in  self.option.FAMILY_PARA_COLLECTION:
            if para_name == self.option.FACTOR_PARA_NAME:
       
                setattr(dummy_target_data,para_name, 1)
                continue
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue
            value = dummy_target_type.LookupParameter(para_name).AsDouble()
            dummy_target_data.update(para_name, value)

        # if USER.IS_DEVELOPER:
        #     if ENVIRONMENT.IS_AVD:
        #         NOTIFICATION.messenger("Cannot update from excel in AVD becasue ACC desktop connector is not working in AVD.")
        #         return
        #     print ("\n\nThis is a developer version")
        #     self.update_from_excel(dummy_target_data)

                

    def update_from_excel(self, dummy_target_data):
        NOTIFICATION.duck_pop("Reading from ACC excel by downloading from cloud, this might take a moment.")
        data = EXCEL.read_data_from_excel(self.option.SOURCE_EXCEL, worksheet="EA Benchmarking DGSF Tracker", return_dict=True)

        key_column = "B"
        print ("avaibale excel departments: {}".format(EXCEL.get_column_values(data, key_column).keys()))
        for department_name in self.option.DEPARTMENT_PARA_MAPPING.keys():
            row = EXCEL.search_row_in_column_by_value(data, 
                                                      key_column, 
                                                      search_value=department_name, 
                                                      is_fuzzy=True)

            target = data.get((row,EXCEL.get_column_index("P")), None)
            print ("At this moment, there is no change to the target value. Just reading")
            if target:
                target = float(target)
                print ("target value found for [{}]: {}".format(department_name, target))
                # dummy_target_data.update(self.option.DEPARTMENT_PARA_MAPPING[department_name], target)
                print ("\n\n")  
        
    def fill_delta_data(self, type_name):
        """maybe should worry about making smaller commit so doc is updated before geting data dfrom type data"""
        dummy_sum_data = AreaData.get_data(self.option.DUMMY_DATA_HOLDER[0])
        dummy_tartget_data = AreaData.get_data(self.option.DUMMY_DATA_HOLDER[1])
        dummy_delta_data = AreaData.get_data(type_name)
        
 
 
       
        dummy_delta_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc) 
        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name == self.option.FACTOR_PARA_NAME:
                setattr(dummy_delta_data,para_name, 1)
                dummy_delta_type.LookupParameter(para_name).Set(1)
                continue
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue
            
            value_real = getattr(dummy_sum_data,para_name)
            value_manual = getattr(dummy_tartget_data, para_name)
            delta = value_real - value_manual
            dummy_delta_data.update(para_name, delta)
            
            dummy_delta_type.LookupParameter(para_name).Set(delta)
            
    def update_schedule_last_update_date(self):
        para_name = "Schedule_Last_Update_Date"
        schedule = REVIT_SCHEDULE.get_schedule_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, self.doc)

        if schedule.LookupParameter(para_name):
            schedule.LookupParameter(para_name).Set(TIME.get_formatted_current_time())




    def update_dgsf_chart(self):


        T = DB.TransactionGroup(self.doc, "update_dgsf_chart")
        T.Start()

        

        try:
            self.collect_all_area_data()
            self.update_main_calculator_family_types()
            self.update_summery_calculator_family_types()

            self.update_schedule_last_update_date()
            T.Commit()
        except:
            print (traceback.format_exc())

            T.RollBack()
        
        
        if self.show_log:
            NOTIFICATION.messenger(main_text="Program schedule calculator update done!")

        
        if self._found_bad_area:
            NOTIFICATION.duck_pop(main_text="Attention, there are some un-enclosed area in area plans that might affect your accuracy.\nSee output window for details.")

        


#########################################################################################








def dgsf_chart_update(doc, show_log = True):
    proj_data = REVIT_PARAMETER.get_revit_project_data(doc)
    if not proj_data:
        NOTIFICATION.messenger(main_text="No project data found, please initalize the project first.")

        return

    department_key_para_name = proj_data["area_tracking"]["para_dict"]["DEPARTMENT_KEY_PARA"]
    program_type_key_para_name = proj_data["area_tracking"]["para_dict"]["PROGRAM_TYPE_KEY_PARA"]
    program_type_detail_key_para_name = proj_data["area_tracking"]["para_dict"]["PROGRAM_TYPE_DETAIL_KEY_PARA"]


    department_para_mapping = OrderedDict(proj_data["area_tracking"]["table_setting"]["DEPARTMENT_PARA_MAPPING"])
    department_ignore_para_names = proj_data["area_tracking"]["table_setting"]["DEPARTMENT_IGNORE_PARA_NAMES"]

    for internal_option_name, option_setting in proj_data["area_tracking"]["option_setting"].items():
        
        level_names = option_setting["levels"]
        option_name = option_setting["option_name"]


        overall_area_scheme_name = option_setting["OVERALL_AREA_SCHEME_NAME"]
        department_area_scheme_name = option_setting["DEPARTMENT_AREA_SCHEME_NAME"]


        option = DepartmentOption(internal_option_name,
                                  department_para_mapping,
                                  department_ignore_para_names,
                                  level_names, 
                                  option_name, 
                                  overall_area_scheme_name, 
                                  department_area_scheme_name,
                                  department_key_para_name,

                                  program_type_key_para_name,
                                  program_type_detail_key_para_name)

  

        if not OptionValidation(doc, option, show_log).validate_all():
            NOTIFICATION.messenger(main_text="Validation failed")
            return

        InternalCheck(doc, option, show_log).update_dgsf_chart()



if __name__ == "__main__":
    pass