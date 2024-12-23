
from EnneadTab import NOTIFICATION, SAMPLE_FILE
from EnneadTab.REVIT import REVIT_FAMILY, REVIT_VIEW, REVIT_SCHEDULE, REVIT_AREA_SCHEME
from pyrevit import forms, script
from Autodesk.Revit import DB #pyright: ignore
from collections import OrderedDict

class DepartmentOption:


    DEPARTMENT_KEY_PARA = "Area_$Department" # this is the area parameter used to lookup category
    PROGRAM_TYPE_KEY_PARA = "Area_$Department_Program Type"
    PROGRAM_TYPE_DETAIL_KEY_PARA = "Area_$Department_Program Type Detail"


    # KEY = REVIT ASSIGNED DEPARTMENT, VALUE = NICKNAME USED IN CALCUATOR FAMILY AND EXCEL AND  AREADATA CLASS
    DEPARTMENT_PARA_MAPPING = OrderedDict([
                            ("DIAGNOSTIC AND TREATMENT", "D&T"),
                            ("EMERGENCY DEPARTMENT", "ED"),
                            ("INPATIENT CARE", "BEDS"),
                            ("PUBLIC SUPPORT", "PUBLIC SUPPORT"),
                            ("ADMINISTRATION AND STAFF SUPPORT", "ADMIN"),
                            ("CLINICAL SUPPORT", "CLINICAL SUPPORT"),
                            ("BUILDING SUPPORT", "BUILDING SUPPORT"),
                            ("UNASSIGNED", "UNASSIGNED")
                            ])

    # in the department area plan, if category fall into the IGNORE list, then it will not alert such discovery. This way only the mis spelled and unintentional category is alerted.
    DEPARTMENT_IGNORE_PARA_NAMES = ["PUBLIC CIRCULATION",
                                    "SERVICE CIRCULATION"]

    PARA_TRACKER_MAPPING = OrderedDict([("MECHANICAL", "MERS")]) # mech is not part of department calc
    PARA_TRACKER_MAPPING.update(DEPARTMENT_PARA_MAPPING)


    #
    OVERALL_AREA_SCHEME_NAME = "GFA Scheme"
    OVERALL_PARA_NAME = "GSF"

    DGSF_SCHEME_NAME = "DGSF Scheme"



    FACTOR_PARA_NAME = "FACTOR" #the discount value, this should be typed in in proj
    DESIGN_SF_PARA_NAME = "DGSF TAKEOFF" 
    ESTIMATE_SF_PARA_NAME = "DGSF ESTIMATE"

    INTERNAL_PARA_NAMES = {"title":"LEVEL", "order":"order"}

    FAMILY_PARA_COLLECTION = INTERNAL_PARA_NAMES.values() + [OVERALL_PARA_NAME,  DESIGN_SF_PARA_NAME, FACTOR_PARA_NAME, ESTIMATE_SF_PARA_NAME] + PARA_TRACKER_MAPPING.values() 
    

    # in the setting file to set which level to run calc
    LEVEL_NAMES = []
    

    DUMMY_DATA_HOLDER = ["GRAND TOTAL",
                        "PROGRAM TARGET",
                        "DELTA"]

    # thia type name collection is to contain all and exact type names for the caulator
    @property
    def TYPE_NAME_COLLECTION(self):
        return self.LEVEL_NAMES + self.DUMMY_DATA_HOLDER


    def __init__(self, levels,  option_name = "", department_area_scheme_name = DGSF_SCHEME_NAME):
        self.is_primary = True if len(option_name) == 0 else False
        self.formated_option_name = "Main Option" if self.is_primary else option_name

        self.LEVEL_NAMES = levels


        self.CALCULATOR_FAMILY_NAME = "EnneadTab AreaData Calculator"

        self.CALCULATOR_CONTAINER_VIEW_NAME = "EnneadTab Area Calculator Collection"
        self.FINAL_SCHEDULE_VIEW_NAME = "PROGRAM CATEGORY"

        self.DEPARTMENT_AREA_SCHEME_NAME = department_area_scheme_name

class OptionValidation:
    def __init__(self, doc, option):
        self.doc = doc
        self.option = option
        self.output = script.get_output()


    def validate_all(self):
        if not self.validate_family():
            return False
        if not self.validate_container_view():
            return False
        self.validate_schedule_view()
        self.is_family_types_valid()
        self.validate_area_scheme()
        return True

    def validate_family(self):
        sample_family_path = SAMPLE_FILE.get_file("{}.rfa".format(self.option.CALCULATOR_FAMILY_NAME))
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
                order_index = self.option.LEVEL_NAMES.index(type_name)
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
                

                
        # set order
        # REVIT_SCHEDULE.sort_fields_in_schedule(view, self.option.FAMILY_PARA_COLLECTION)

        
        t.Commit()
        # TO-DO

        # test if each schedule field is the right format(align to right, set whole number, digit grouping)
        # TO-DO
        pass


    def validate_area_scheme(self):
        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.OVERALL_AREA_SCHEME_NAME, self.doc)
        if not area_scheme:
            print("Area scheme [{}] not found".format(self.option.OVERALL_AREA_SCHEME_NAME))
            return False

        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.DGSF_SCHEME_NAME, self.doc)
        if not area_scheme:
            print("Area scheme [{}] not found".format(self.option.DGSF_SCHEME_NAME))
            return False

        return True




#########################################################################################








def dgsf_chart_update(doc):
    levels = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements())
    levels.sort(key=lambda x: x.Elevation, reverse=True)
    selected_levels = forms.SelectFromList.show(levels, multiselect=True, title="Select the levels", button_name="Select levels", name_attr="Name")
    if not selected_levels:
        NOTIFICATION.messenger(main_text="No levels selected")
        return
    level_names = [level.Name for level in selected_levels]
    option = DepartmentOption(level_names)

    if not OptionValidation(doc, option).validate_all():
        NOTIFICATION.messenger(main_text="Validation failed")
        return

