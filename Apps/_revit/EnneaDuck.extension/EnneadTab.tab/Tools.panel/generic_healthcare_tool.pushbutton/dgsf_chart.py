from EnneadTab import   NOTIFICATION, SAMPLE_FILE,   TIME, ERROR_HANDLE, USER
from EnneadTab.REVIT import REVIT_FAMILY, REVIT_VIEW, REVIT_SCHEDULE,REVIT_SPATIAL_ELEMENT,REVIT_SELECTION, REVIT_AREA_SCHEME, REVIT_PROJ_DATA, REVIT_PARAMETER
from pyrevit import script
from Autodesk.Revit import DB #pyright: ignore
from collections import OrderedDict
import traceback
import os


class FamilyDocToClose:
    family_docs = []

    @classmethod
    def add_family_doc(cls, doc):
        cls.family_docs.append(doc)

    @classmethod
    def close_family_docs(cls):
        for doc in cls.family_docs:
            try:
                doc.Close(False)
            except Exception as e:
                ERROR_HANDLE.print_note("Error closing document: {}".format(e))

class DepartmentOption:
    """Configuration class for department area tracking and calculations.
    
    Attributes:
        DEPARTMENT_KEY_PARA (str): Parameter name for department tracking
        PROGRAM_TYPE_KEY_PARA (str): Parameter name for program type
        PROGRAM_TYPE_DETAIL_KEY_PARA (str): Parameter name for program type detail
        DEPARTMENT_PARA_MAPPING (OrderedDict): Mapping between Revit departments and calculator nicknames
        DEPARTMENT_IGNORE_PARA_NAMES (list): List of department names to ignore in calculations
        OVERALL_AREA_SCHEME_NAME (str): Name of the overall area scheme
        OVERALL_PARA_NAME (str): Parameter name for overall area
        DEPARTMENT_AREA_SCHEME_NAME (str): Name of the department area scheme
        FACTOR_PARA_NAME (str): Parameter name for discount factor
        DESIGN_SF_PARA_NAME (str): Parameter name for design square footage
        ESTIMATE_SF_PARA_NAME (str): Parameter name for estimated square footage
        INTERNAL_PARA_NAMES (dict): Internal parameter names for tracking
        LEVEL_NAMES (list): List of level names to track
        DUMMY_DATA_HOLDER (list): List of dummy data types for summaries
    """

    DEPARTMENT_KEY_PARA = "get from project data para_dict"
    PROGRAM_TYPE_KEY_PARA = "get from project data para_dict"
    PROGRAM_TYPE_DETAIL_KEY_PARA = "get from project data para_dict"
    DEPARTMENT_PARA_MAPPING = "get from project data table setting"
    DEPARTMENT_IGNORE_PARA_NAMES = "get from project data setting"
    OVERALL_AREA_SCHEME_NAME = "get from project data option setting"
    OVERALL_PARA_NAME = "GSF"
    DEPARTMENT_AREA_SCHEME_NAME = "get from project data option setting"
    FACTOR_PARA_NAME = "FACTOR"
    DESIGN_SF_PARA_NAME = "DGSF TAKEOFF"
    ESTIMATE_SF_PARA_NAME = "DGSF ESTIMATE"
    INTERNAL_PARA_NAMES = {"title": "LEVEL", "order": "order"}
    LEVEL_NAMES = []
    DUMMY_DATA_HOLDER = ["GRAND TOTAL", "PROGRAM TARGET", "DELTA"]


    @property
    def PARA_TRACKER_MAPPING(self):
        """Returns mapping of department parameters including mechanical."""
        if not self._dedicated_department:
            temp = OrderedDict([("MECHANICAL", "MERS")])
            temp.update(self.DEPARTMENT_PARA_MAPPING)
            return temp

        if self._cached_para_mapping is not None:
            return self._cached_para_mapping

        if not hasattr(self, 'doc') or self.doc is None:
            ERROR_HANDLE.print_note("Document not initialized for department mapping")
            return OrderedDict()

        try:
            # get all the area whose department is equal to the dedicated department, collect the PROGRAM_TYPE_KEY_PARA of those areas
            areas = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
            temp = {}
            for area in areas:
                if area.LookupParameter(self.DEPARTMENT_KEY_PARA) and area.LookupParameter(self.DEPARTMENT_KEY_PARA).AsString() == self._dedicated_department:
                    program_type_key = area.LookupParameter(self.PROGRAM_TYPE_KEY_PARA).AsString() if area.LookupParameter(self.PROGRAM_TYPE_KEY_PARA) else None
                    if program_type_key:
                        temp[program_type_key] = program_type_key

            self._cached_para_mapping = OrderedDict(sorted(temp.items()))
            if self._cached_para_mapping is None:
                print("cached para mapping is None, return dummy data")
                return OrderedDict({"ABC": "abc", "DEF": "def", "GHI": "ghi"})
            return self._cached_para_mapping
        except Exception as e:
            ERROR_HANDLE.print_note("Error creating department mapping: {}".format(e))
            return OrderedDict({"ABC111111": "abc333333", "DEF222222": "def444444", "GHI333333": "ghi555555"})

    @property
    def FAMILY_PARA_COLLECTION(self):
        """Returns collection of all family parameters."""
        return (self.INTERNAL_PARA_NAMES.values() + 
                [self.OVERALL_PARA_NAME, self.DESIGN_SF_PARA_NAME, 
                 self.FACTOR_PARA_NAME, self.ESTIMATE_SF_PARA_NAME] + 
                self.PARA_TRACKER_MAPPING.values())

    @property
    def TYPE_NAME_COLLECTION(self):
        """Returns collection of all type names for calculator."""
        return self.LEVEL_NAMES + self.DUMMY_DATA_HOLDER

    @property
    def CALCULATOR_FAMILY_NAME_BASE(self):
        """Returns the base name of the calculator family."""
        return "AreaData Calculator"

    @property
    def CALCULATOR_FAMILY_NAME(self):
        """Returns the calculator family name with option suffix if not primary."""
        base_name = self.CALCULATOR_FAMILY_NAME_BASE
        new_name = base_name if self.is_primary else "{}_{}".format(base_name, self.formated_option_name)
        if self._dedicated_department:
            return new_name + "_" + self._dedicated_department
        else:
            return new_name

    @property
    def CALCULATOR_CONTAINER_VIEW_NAME(self):
        """Returns the calculator container view name with option suffix if not primary."""
        base_name = "Area Calculator Collection"
        new_name = base_name if self.is_primary else "{}_{}".format(base_name, self.formated_option_name)
        if self._dedicated_department:
            return new_name + "_" + self._dedicated_department
        else:
            return new_name

    @property
    def FINAL_SCHEDULE_VIEW_NAME(self):
        """Returns the final schedule view name with option suffix if not primary."""
        base_name = "PROGRAM CATEGORY"
        new_name = base_name if self.is_primary else "{}_{}".format(base_name, self.formated_option_name)
        if self._dedicated_department:
            return new_name + "_" + self._dedicated_department
        else:
            return new_name

    def __init__(self, internal_option_name, department_para_mapping,
                 department_ignore_para_names, levels, option_name,
                 overall_area_scheme_name, department_area_scheme_name,
                 department_key_para_name, program_type_key_para_name,
                 program_type_detail_key_para_name, dedicated_department, doc):
        """Initialize department option configuration.
        
        Args:
            internal_option_name (str): Internal name for the option
            department_para_mapping (OrderedDict): Department parameter mapping
            department_ignore_para_names (list): List of departments to ignore
            levels (list): List of levels to track
            option_name (str): Name of the option
            overall_area_scheme_name (str): Name of overall area scheme
            department_area_scheme_name (str): Name of department area scheme
            department_key_para_name (str): Department key parameter name
            program_type_key_para_name (str): Program type key parameter name
            program_type_detail_key_para_name (str): Program type detail parameter name
            dedicated_department (str): Department name to filter by, if any
            doc (Document): Revit document
        """
        # Initialize document first
        self.doc = doc
        self._cached_para_mapping = None
        
        # Initialize basic properties
        self.internal_option_name = internal_option_name
        self.is_primary = True if len(option_name) == 0 else False
        self.formated_option_name = "Main Option" if self.is_primary else option_name
        self.LEVEL_NAMES = levels
        self._dedicated_department = dedicated_department

        # Set area scheme names
        self.OVERALL_AREA_SCHEME_NAME = overall_area_scheme_name
        self.DEPARTMENT_AREA_SCHEME_NAME = department_area_scheme_name

        # Set parameter names
        self.DEPARTMENT_KEY_PARA = department_key_para_name
        self.PROGRAM_TYPE_KEY_PARA = program_type_key_para_name
        self.PROGRAM_TYPE_DETAIL_KEY_PARA = program_type_detail_key_para_name

        # Set department mappings
        self.DEPARTMENT_PARA_MAPPING = department_para_mapping
        self.DEPARTMENT_IGNORE_PARA_NAMES = department_ignore_para_names

class OptionValidation:
    """Validates department option configuration and related Revit elements.
    
    Args:
        doc (Document): Revit document
        option (DepartmentOption): Department option to validate
        show_log (bool): Whether to show detailed logging
    """

    def __init__(self, doc, option, show_log):
        if doc is None:
            raise ValueError("Document cannot be None in OptionValidation")
        self.doc = doc
        self.option = option
        self.output = script.get_output()
        self.show_log = show_log


    def validate_family_data_holder(self):
        """Validates and updates family data holder parameters."""
        fam_doc = self.doc.EditFamily(REVIT_FAMILY.get_family_by_name(self.option.CALCULATOR_FAMILY_NAME, self.doc))
        fam_manager = fam_doc.FamilyManager

        all_fam_para_dict = {para.Definition.Name: para for para in fam_manager.GetParameters()}
        T = DB.Transaction(fam_doc, "Validate Family Data Holder")
        T.Start()

        family_changed = False
        # Remove parameters not in collection
        for para_name in all_fam_para_dict:
            if para_name not in self.option.FAMILY_PARA_COLLECTION:
                print ("Removing parameter [{}] in family [{}]".format(para_name, self.option.CALCULATOR_FAMILY_NAME))
                fam_manager.RemoveParameter(all_fam_para_dict[para_name])
                family_changed = True

        # Add missing parameters
        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name not in all_fam_para_dict:
                print ("Adding parameter [{}] in family [{}]".format(para_name, self.option.CALCULATOR_FAMILY_NAME))
                fam_manager.AddParameter(para_name, DB.GroupTypeId.Data, DB.SpecTypeId.Area, False)
                family_changed = True

        T.Commit()
        if family_changed:
            REVIT_FAMILY.load_family(fam_doc, self.doc)
        
        FamilyDocToClose.add_family_doc(fam_doc)
        fam_doc.Close(False)
        return True

    def validate_all(self):
        """Validates all aspects of the department option."""
        self.show_logic()
        if not self.is_area_scheme_valid():
            print("Area scheme validation failed")
            return False
        if not self.validate_family():
            print("Family validation failed")
            return False
        if not self.validate_family_data_holder():
            print("Family data holder validation failed")
            return False
        if not self.validate_container_view():
            print("Container view validation failed")
            return False
        if not self.validate_schedule_view():
            print("Schedule view validation failed")
            return False
        if not self.is_family_types_valid():
            print("Family types validation failed")
            return False
        return True

    def show_logic(self):
        """Shows validation logic if logging is enabled."""
        if not self.show_log:
            return

        output = script.get_output()
        output.print_md("## Logic for [{}]".format(self.option.formated_option_name))
        
        note = []
        note.append("The AreaScheme used for department data is [{}]".format(self.option.DEPARTMENT_AREA_SCHEME_NAME))
        note.append("The parameter used in getting category is [{}]".format(self.option.DEPARTMENT_KEY_PARA))
        note.append("The AreaScheme used for overall data is [{}]".format(self.option.OVERALL_AREA_SCHEME_NAME))
        note.append("Any valid area will count toward overall area.")
        note.append("The family used in checking is [{}]".format(self.option.CALCULATOR_FAMILY_NAME))

        container_view = REVIT_VIEW.get_view_by_name(self.option.CALCULATOR_CONTAINER_VIEW_NAME, doc=self.doc)
        if container_view:
            note.append("The view used to contain all calculator is [{}]".format(
                output.linkify(container_view.Id, title=self.option.CALCULATOR_CONTAINER_VIEW_NAME)))

        schedule_view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)
        if schedule_view:
            note.append("The view used to contain final schedule is [{}]".format(
                output.linkify(schedule_view.Id, title=self.option.FINAL_SCHEDULE_VIEW_NAME)))

        note.append("\nThe level names used in checking is below:")
        for x in self.option.LEVEL_NAMES:
            note.append("   -[{}]".format(x))

        note.append("\nThe value of area should fall in to one of below so it can match the excel table:")
        for para, nick_name in self.option.PARA_TRACKER_MAPPING.items():
            note.append("   -[{}]-->[{}]".format(para, nick_name))

        note.append("\nWhen the department category of area is not part of the above mapping table, it should alert exception. HOWEVER, category in below list will silent the alert, and they will NOT count toward department calculation.")
        for para in self.option.DEPARTMENT_IGNORE_PARA_NAMES:
            note.append("   -Ignore [{}]".format(para))

        note.append("\nUnder the hood, Here is how the script logic is handled:")
        note.append("1. Search through all the area in area scheme [{}], ignoring area on levels that not part of the defined Level Names".format(self.option.DEPARTMENT_AREA_SCHEME_NAME))
        note.append("2. Look at the parameter [{}] of the area, map that value to the Excel version, and add the area to the related field of the level".format(self.option.DEPARTMENT_KEY_PARA))
        note.append("3. Search through all the area in area scheme [{}], add any area to the overall area of this level".format(self.option.OVERALL_AREA_SCHEME_NAME))
        note.append("4. Search through all the calculator types in the family [{}], get the predefined Factor in this level, apply that factor to each blue column data. Overall GFA and MERS are excluded in this act, they use factor 1 always".format(self.option.CALCULATOR_FAMILY_NAME))
        note.append("5. The unfactored sum of blue column is filled to [{0}], and [{1}] is completed by {0}x{2}".format(
            self.option.DESIGN_SF_PARA_NAME, self.option.ESTIMATE_SF_PARA_NAME, self.option.FACTOR_PARA_NAME))
        note.append("6. After all the level based data is filled out, a dummy summary is filled by summing up the similar parameter names above.")
        note.append("7. The target data is left untouched. THE TEAM IS EXPECTED TO FILL IN THOSE INFO BASED ON YOUR DESIRED TARGET. The delta is calculated by looking up the difference between dummy summary and manual target.")
        note.append("8. After main option is processed, option is look into to primary area scheme and copy over data that is not BEDS.")

        print("\n".join(note))

    def validate_family(self):
        """Validates calculator family exists."""
        default_sample_family_path = SAMPLE_FILE.get_file("{}.rfa".format(self.option.CALCULATOR_FAMILY_NAME_BASE))
       
        fam = REVIT_FAMILY.get_family_by_name(self.option.CALCULATOR_FAMILY_NAME, doc=self.doc, load_path_if_not_exist=default_sample_family_path)
        return fam is not None

    def validate_container_view(self):
        """Validates and creates container view if needed."""
        view = REVIT_VIEW.get_view_by_name(self.option.CALCULATOR_CONTAINER_VIEW_NAME, doc=self.doc)
        if view:
            self.update_view_organization(view)
            return True

        t = DB.Transaction(self.doc, "Making Container View")
        t.Start()
        view = DB.ViewDrafting.Create(self.doc, REVIT_VIEW.get_default_view_type("drafting").Id)
        view.Name = self.option.CALCULATOR_CONTAINER_VIEW_NAME
        view.Scale = 250
        t.Commit()
        self.update_view_organization(view)
        return True

    def update_view_organization(self, view):
        """Updates the organization of the view."""
        t = DB.Transaction(self.doc, "Updating View Organization")
        t.Start()
        try:
            view.LookupParameter("Views_$Group").Set("EnneadTab")
            view.LookupParameter("Views_$Series").Set("AreaTracking")
        except:
            pass
        t.Commit()

    def validate_schedule_view(self):
        """Validates and creates schedule view if needed."""
        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)
        if not view:
            t = DB.Transaction(self.doc, "Making Final Schedule View")
            t.Start()
            view = DB.ViewSchedule.CreateNoteBlock(self.doc, 
                REVIT_FAMILY.get_family_by_name(self.option.CALCULATOR_FAMILY_NAME, self.doc).Id)
            view.Name = self.option.FINAL_SCHEDULE_VIEW_NAME
            t.Commit()
            
        self.format_schedule()
        self.update_view_organization(view)
        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)
        if self.show_log:
            print("Schedule view at [{}]".format(self.output.linkify(view.Id, title=self.option.FINAL_SCHEDULE_VIEW_NAME)))
        return True

    def is_family_types_valid(self):
        """Validates family types match level names."""
        self.validate_singular_instance()
        self.remove_unrelated_types()
        self.set_type_order_index()
        return True

    def validate_singular_instance(self):
        """Ensures each type has exactly one instance."""
        for type_name in self.option.TYPE_NAME_COLLECTION:
            calcs = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(
                self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
            
            if calcs is None:
                self.make_new_calcualtor(type_name)
                continue

            foot_note = "level [{}]".format(type_name) if type_name in self.option.LEVEL_NAMES else "dummy data block [{}]".format(type_name)
            
            if calcs is not None and len(calcs) == 1:
                continue

            if len(calcs) > 1:
                print("Too many calculator found for {}. Resetting now...".format(foot_note))
            else:
                print("No calculator found for {}. Creating now...".format(foot_note))

            self.purge_type_by_name(type_name)
            self.make_new_calcualtor(type_name)

    def purge_type_by_name(self, type_name):
        """Removes a family type by name."""
        calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
        if calc_type:
            t = DB.Transaction(self.doc, "Purge Useless Type")
            t.Start()
            self.doc.Delete(calc_type.Id)
            t.Commit()

    def make_new_calcualtor(self, type_name):
        """Creates a new calculator instance."""
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
                                        REVIT_VIEW.get_view_by_name(self.option.CALCULATOR_CONTAINER_VIEW_NAME, doc=self.doc))
        t.Commit()

    def remove_unrelated_types(self):
        """Removes family types not in the type collection."""
        for calc_type in REVIT_FAMILY.get_all_types_by_family_name(self.option.CALCULATOR_FAMILY_NAME, self.doc):
            type_name = calc_type.LookupParameter("Type Name").AsString()
            if type_name not in self.option.TYPE_NAME_COLLECTION:
                print("Extra type [{}] found. Deleting now...".format(type_name))
                t = DB.Transaction(self.doc, "Delete extra type [{}]".format(type_name))
                t.Start()
                self.doc.Delete(calc_type.Id)
                t.Commit()

    def set_type_order_index(self):
        """Sets order index for each type."""
        for calc_type in REVIT_FAMILY.get_all_types_by_family_name(self.option.CALCULATOR_FAMILY_NAME, self.doc):
            type_name = calc_type.LookupParameter("Type Name").AsString()
            if type_name in self.option.LEVEL_NAMES:
                order_index = len(self.option.LEVEL_NAMES) - self.option.LEVEL_NAMES.index(type_name)
            elif type_name in self.option.DUMMY_DATA_HOLDER:
                order_index = self.option.DUMMY_DATA_HOLDER[::-1].index(type_name) - 100
            else:
                print("!!!!!!!!!!!!!!!!![{}], is not a valid type name".format(type_name))
                continue
                
            current_index = calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["order"]).AsInteger()
            current_level_display = calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["title"]).AsString()
            
            if current_index != order_index or current_level_display != type_name:
                print("Fixing order index/title display of [{}]".format(type_name))
                t = DB.Transaction(self.doc, "Set order index for [{}]".format(type_name))
                t.Start()
                calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["title"]).Set(type_name)
                calc_type.LookupParameter(self.option.INTERNAL_PARA_NAMES["order"]).Set(order_index)
                t.Commit()

    def is_area_scheme_valid(self):
        """Validates area schemes exist."""
        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.OVERALL_AREA_SCHEME_NAME, self.doc)
        if not area_scheme:
            self.output.print_md("## Area scheme [{}] not found for overall area scheme, please create it first".format(
                self.option.OVERALL_AREA_SCHEME_NAME))
            return False

        area_scheme = REVIT_AREA_SCHEME.get_area_scheme_by_name(self.option.DEPARTMENT_AREA_SCHEME_NAME, self.doc)
        if not area_scheme:
            self.output.print_md("## Area scheme [{}] not found for departmental scheme, please create it first".format(
                self.option.DEPARTMENT_AREA_SCHEME_NAME))
            return False

        return True

    def format_schedule(self):
        """Format the schedule view with proper field order and formatting.
        
        This method formats the schedule view with:
        - Fields ordered according to FAMILY_PARA_COLLECTION
        - Internal fields hidden
        - Group order set to descending
        - Numeric fields formatted with:
          - Rounding to nearest 10
          - Digit grouping
          - Right alignment
        - Cell shading for different field types, using department color mapping from Excel
        """
        view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, doc=self.doc)

        if not REVIT_SELECTION.is_changable(view):
            owner = REVIT_SELECTION.get_owner(view)
            self.output.print_md("## Schedule view [{}] is owned by [{}]".format(self.option.FINAL_SCHEDULE_VIEW_NAME, owner))
            return False

        t = DB.Transaction(self.doc, "Format schedule contents")
        t.Start()

        # Add required fields and hide internal fields
        REVIT_SCHEDULE.add_fields_to_schedule(view, self.option.FAMILY_PARA_COLLECTION)
        REVIT_SCHEDULE.hide_fields_in_schedule(view, self.option.INTERNAL_PARA_NAMES["order"])

        # Set group order descending
        REVIT_SCHEDULE.set_group_order(view, self.option.INTERNAL_PARA_NAMES["order"], descending=True)

        # Sort fields
        REVIT_SCHEDULE.sort_fields_in_schedule(view, self.option.FAMILY_PARA_COLLECTION)

        # Format numeric fields
        REVIT_SCHEDULE.format_numeric_fields(view, self.option.FAMILY_PARA_COLLECTION)

        # Shade cells based on field type and department color mapping
        color_dict = {
            self.option.OVERALL_PARA_NAME: (230, 230, 230),  # Light gray for GSF
            "MERS": (220, 220, 220),  # Slightly darker gray for MERS
            self.option.DESIGN_SF_PARA_NAME: (240, 240, 240),  # Very light gray for design SF
            self.option.ESTIMATE_SF_PARA_NAME: (240, 240, 240),  # Very light gray for estimate SF
        }
        # Load department color mapping from Excel (project data)
        proj_data = REVIT_PROJ_DATA.get_revit_project_data(self.doc)
        excel_path = proj_data.get("color_update", {}).get("setting", {}).get("excel_path", None)
        if excel_path and os.path.exists(excel_path):
            from EnneadTab import COLOR
            color_template = COLOR.get_color_template_data(excel_path)
            dept_color_map = color_template.get("department_color_map", {})
            # Add department colors by nickname
            for dept, nickname in self.option.DEPARTMENT_PARA_MAPPING.items():
                color_info = dept_color_map.get(dept) or dept_color_map.get(nickname)
                if color_info and "color" in color_info:
                    color_dict[nickname] = color_info["color"]
        REVIT_SCHEDULE.shade_cells_by_field(view, color_dict)

        # Conditional formatting: if 'order' is smaller than 0, color all its fields dark grey
        try:
            order_field = REVIT_SCHEDULE.get_field_by_name(view, self.option.INTERNAL_PARA_NAMES["order"])
            if order_field:
                try:
                    table_data = view.GetTableData()
                    section = table_data.GetSection(DB.SectionType.Body)
                    row_count = section.NumberOfRows
                    col_count = section.NumberOfColumns
                    for row in range(row_count):
                        try:
                            order_val = section.GetCellText(row, order_field.FieldId)
                            if order_val is not None and str(order_val).strip() != "":
                                try:
                                    order_val_num = float(order_val)
                                    if order_val_num < 0:
                                        for col in range(col_count):
                                            cell_style = section.GetCellStyle(row, col)
                                            cell_style.BackgroundColor = DB.Color(80, 80, 80)  # dark grey
                                            section.SetCellStyle(row, col, cell_style)
                                except Exception as e:
                                    ERROR_HANDLE.print_note("Could not parse 'order' value: {}".format(e))
                        except Exception as e:
                            ERROR_HANDLE.print_note("Error processing row {}: {}".format(row, e))
                except AttributeError:
                    # If GetSection is not available, skip conditional formatting
                    pass
        except Exception as e:
            ERROR_HANDLE.print_note("Conditional formatting error: {}".format(e))

        t.Commit()

        if self.show_log:
            print("Schedule view at [{}]".format(self.output.linkify(view.Id, title=self.option.FINAL_SCHEDULE_VIEW_NAME)))
        return True

class AreaData:
    """Class for holding area data on each level.
    
    This class maintains a collection of area data for different levels and provides
    methods to update and retrieve this data.
    
    Class Attributes:
        data_collection (dict): Dictionary storing area data for each level
    """
    data_collection = dict()

    def __init__(self, type_name):
        """Initialize area data for a specific type.
        
        Args:
            type_name (str): Name of the type/level
        """
        self.title = type_name

    @classmethod
    def purge_data(cls):
        """Clear all stored area data."""
        cls.data_collection.clear()
        
    @classmethod
    def get_data(cls, type_name):
        """Get or create area data for a specific type.
        
        Args:
            type_name (str): Name of the type/level
            
        Returns:
            AreaData: Area data instance for the specified type
        """
        key = type_name
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = AreaData(type_name)
        cls.data_collection[key] = instance

        
        return instance

    def update(self, area_name, area):
        """Update area data for a specific area name.
        
        Args:
            area_name (str): Name of the area
            area (float): Area value to add
        """
        if not hasattr(self, area_name):
            setattr(self, area_name, area)
            return

        current_area = getattr(self, area_name)

        setattr(self, area_name, current_area + area)

    @classmethod
    def print_detail(cls):
        for key, value in cls.data_collection.items():
            print ("printing detail for [{}]".format(key))
            for attr_key in value.__dict__.keys():
                print ("- {}: {}".format(attr_key, getattr(value, attr_key)))

class InternalCheck:
    """Main class for handling area summary calculations.
    
    This class manages the collection and processing of area data, including
    department-specific areas and overall areas.
    
    Args:
        doc (Document): Revit document
        option (DepartmentOption): Department option configuration
        show_log (bool): Whether to show detailed logging
    """

    def __init__(self, doc, option, show_log):
        if doc is None:
            raise ValueError("Document cannot be None in InternalCheck")
        if option is None:
            raise ValueError("Option cannot be None in InternalCheck")
            
        self.doc = doc
        self.option = option
        self.show_log = show_log
        self.output = script.get_output()
        self._found_bad_area = False
        self._owner_holding = set()
        self._has_changes = False
        AreaData.purge_data()

    def collect_area_data_action(self, area_scheme_name, search_key_name, para_mapping):
        """Collect area data for a specific area scheme.
        
        Args:
            area_scheme_name (str): Name of the area scheme
            search_key_name (str): Parameter name to use as key
            para_mapping (dict): Mapping of parameter names to nicknames
        """
        if not self.doc:
            ERROR_HANDLE.print_note("Document is None in collect_area_data_action")
            return

        # Get all areas in the scheme
        all_areas = DB.FilteredElementCollector(self.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Areas)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name == area_scheme_name, all_areas)

        # Process each area
        for area in all_areas:
            level = area.Level
            if level.Name not in self.option.LEVEL_NAMES:
                if self.show_log:
                    print("Area is on [{}], which is not a tracking level....{}".format(
                        level.Name, self.output.linkify(area.Id)))
                continue

            if not level:
                if self.show_log:
                    print("Area has no level, might not be placed....{}".format(
                        self.output.linkify(area.Id)))
                continue

            if self.option._dedicated_department:
                if area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString() != self.option._dedicated_department:
                    continue

  

            if REVIT_SPATIAL_ELEMENT.is_element_bad(area):
                if self.show_log:
                    status = REVIT_SPATIAL_ELEMENT.get_element_status(area)
                    print("\nArea has no size!\nIt is {}....{} @ Level [{}] @ [{}]".format(
                        status, self.output.linkify(area.Id, 
                        area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString()),
                        level.Name, area_scheme_name))
                else:
                    info = DB.WorksharingUtils.GetWorksharingTooltipInfo(self.doc, area.Id)
                    editor = info.LastChangedBy
                    print("\nArea has no area number! [{}] @ Level [{}] at [{}]....Last edited by [{}]\nIt might not be enclosed or placed. Run in detail mode to find out more detail.".format(area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString(), level.Name, area_scheme_name, editor))
                self._found_bad_area = True
                continue

            level_data = AreaData.get_data(level.Name)

            if search_key_name:
                department_name = area.LookupParameter(search_key_name).AsString()
                if department_name in self.option.DEPARTMENT_IGNORE_PARA_NAMES:
                    print("Ignore {} for calculation at [{}]".format(
                        self.output.linkify(area.Id, title=department_name), level.Name))
                    continue

                department_nickname = para_mapping.get(department_name)
                if not department_nickname:
                    all_department_names = sorted(para_mapping.keys())
                    error_msg = "Area has department value [{}] not matched in project setup (CASE SENSITIVE)".format(department_name)
                    
                    if self.show_log:
                        error_msg += "....{}@{}".format(self.output.linkify(area.Id), level.Name)
                    
                    print(error_msg)
                    print("Available departments: [{}]".format(", ".join(all_department_names)))
                    continue

                # ERROR_HANDLE.print_note (" finding {} with area of {}, going to add.".format(department_nickname, area.Area))
                level_data.update(department_nickname, area.Area)
                # ERROR_HANDLE.print_note (" {} now has area of {}".format(department_nickname, getattr(level_data, department_nickname)))
                # ERROR_HANDLE.print_note("DEBUG: id of data is {}".format(id(level_data)))
            else:
                # For GSF scenario, count everything
                level_data.update(self.option.OVERALL_PARA_NAME, area.Area)


    def collect_all_area_data(self):
        """Collect area data for both department details and overall areas."""
        # Collect department-specific data
        self.collect_area_data_action(self.option.DEPARTMENT_AREA_SCHEME_NAME, 
                                    self.option.DEPARTMENT_KEY_PARA if not self.option._dedicated_department else self.option.PROGRAM_TYPE_KEY_PARA, 
                                    self.option.PARA_TRACKER_MAPPING)

        # Collect overall area data
        self.collect_area_data_action(self.option.OVERALL_AREA_SCHEME_NAME, 
                                    None, 
                                    None)

        if self.option._dedicated_department == "CLASSROOM":
            AreaData.print_detail()
        if not self.option.is_primary:
            self.copy_data_from_primary()

    def copy_data_from_primary(self):
        """Copy non-BEDS data from primary option to current option."""
        if self.show_log:
            print("Copying all data from primary option except BEDS, talk to Sen if you do not want this behavior")

        # Reset non-BEDS data to zero
        for type_name, data in AreaData.data_collection.items():
            if type_name not in self.option.LEVEL_NAMES:
                continue
            for attr_key in self.option.PARA_TRACKER_MAPPING.values():
                if attr_key != "BEDS":
                    setattr(data, attr_key, 0)

        # Copy non-BEDS data from primary option
        all_areas = DB.FilteredElementCollector(self.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Areas)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name == self.option.DEPARTMENT_AREA_SCHEME_NAME, all_areas)

        for area in all_areas:
            level = area.Level
            if level.Name not in self.option.LEVEL_NAMES:
                continue

            if not level or area.Area <= 0:
                continue

            department_name = area.LookupParameter(self.option.DEPARTMENT_KEY_PARA).AsString()
            if department_name in self.option.DEPARTMENT_IGNORE_PARA_NAMES:
                continue

            department_nickname = self.option.PARA_TRACKER_MAPPING.get(department_name)
            if department_nickname is not None and department_nickname != "BEDS":
                level_data = AreaData.get_data(level.Name)
                level_data.update(department_nickname, area.Area)

    def update_main_calculator_family_types(self):
        """Update calculator family types with collected area data."""
        t = DB.Transaction(self.doc, "_Part 1_update main calculator family types")
        t.Start()
        
        for type_name in sorted(self.option.LEVEL_NAMES):
            if self.show_log:
                print("Processing data for Level: [{}]".format(type_name))
                
            level_data = AreaData.get_data(type_name)
            calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)

            if not REVIT_SELECTION.is_changable(calc_type):
                print("Cannot update [{}] due to ownership by {}.. Skipping".format(
                    type_name, REVIT_SELECTION.get_owner(calc_type)))
                self._owner_holding.add(REVIT_SELECTION.get_owner(calc_type))
                continue

            # Process content
            factor = calc_type.LookupParameter(self.option.FACTOR_PARA_NAME).AsDouble()
            level_data.factor = factor

            # Fill in department related data
            design_GSF_before_factor = 0
            for family_para_name in self.option.PARA_TRACKER_MAPPING.values() + [self.option.OVERALL_PARA_NAME]:
                # ERROR_HANDLE.print_note("log: working on {} checking {}".format(type_name, family_para_name))
                if not hasattr(level_data, family_para_name):
                    # ERROR_HANDLE.print_note("log: not having {} in {}, its id is {}, will set level data area to 0 for {}".format(family_para_name, level_data, id(level_data),family_para_name))
                    setattr(level_data, family_para_name, 0)

                if family_para_name in self.option.PARA_TRACKER_MAPPING.values():
                    if family_para_name != "MERS":
                        design_GSF_before_factor += getattr(level_data, family_para_name)

                para = calc_type.LookupParameter(family_para_name)
                if para:
                    local_factor = 1 if family_para_name in [self.option.OVERALL_PARA_NAME, "MERS"] else level_data.factor
                    factored_area = getattr(level_data, family_para_name) * local_factor
                    if self.option._dedicated_department == "CLASSROOM":
                        ERROR_HANDLE.print_note("1.DEBUG: para is [{}]".format(family_para_name))
                        ERROR_HANDLE.print_note("2.DEBUG: para.AsDouble() is [{}]".format(para.AsDouble()))
                        ERROR_HANDLE.print_note("3.DEBUG: factored_area is [{}]".format(factored_area))
                        ERROR_HANDLE.print_note("4.DEBUG: factor is [{}]".format(local_factor))
                    if para.AsDouble() != factored_area:
                        self._has_changes = True
                        para.Set(factored_area)
                        ERROR_HANDLE.print_note("!!!!!!!!!!!!!!!DEBUG: set [{}] to [{}] at type [{}]".format(family_para_name, factored_area, type_name))
                else:
                    print("No para found for [{}], please edit the family..".format(family_para_name))

            # Fill in GSF data
            design_SF_para = calc_type.LookupParameter(self.option.DESIGN_SF_PARA_NAME)
            if design_SF_para.AsDouble() != design_GSF_before_factor:
                self._has_changes = True
                design_SF_para.Set(design_GSF_before_factor)
                
            estimate_SF_para = calc_type.LookupParameter(self.option.ESTIMATE_SF_PARA_NAME)
            estimate_value = design_GSF_before_factor * level_data.factor
            if estimate_SF_para.AsDouble() != estimate_value:
                self._has_changes = True
                estimate_SF_para.Set(estimate_value)

        t.Commit()

    def update_summery_calculator_family_types(self):
        """Update summary calculator family types with aggregated data."""
        t = DB.Transaction(self.doc, "_Part 2_update summary calculator family types")
        t.Start()
        
        for i, type_name in enumerate(self.option.DUMMY_DATA_HOLDER):
            if self.show_log:
                print("Processing data for Summary Data Block [{}]".format(type_name))

            calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
            if not REVIT_SELECTION.is_changable(calc_type):
                note = "Cannot update [{}] due to ownership by {}.. Skipping".format(
                    type_name, REVIT_SELECTION.get_owner(calc_type))
                print(note)
                self._owner_holding.add(REVIT_SELECTION.get_owner(calc_type))
                NOTIFICATION.messenger(note)
                continue

            if i == 0:
                self.fill_dummy_sum(type_name)
            elif i == 1:
                self.fetch_dummy_target(type_name)
            elif i == 2:
                self.fill_delta_data(type_name)

        t.Commit()

    def fill_dummy_sum(self, type_name):
        """Fill dummy summary data."""
        dummy_sum_data = AreaData.get_data(type_name)

        for level in self.option.LEVEL_NAMES:
            level_calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, level, self.doc)
            for para_name in self.option.FAMILY_PARA_COLLECTION:
                if para_name == self.option.FACTOR_PARA_NAME:
                    setattr(dummy_sum_data, para_name, 1)
                    continue
                if para_name in self.option.INTERNAL_PARA_NAMES.values():
                    continue

                if level_calc_type.LookupParameter(para_name):
                    value = level_calc_type.LookupParameter(para_name).AsDouble()
                    dummy_sum_data.update(para_name, value)
                else:
                    print("No para found for [{}], please edit the family..".format(para_name))

        dummy_calc_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)
        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue
            para = dummy_calc_type.LookupParameter(para_name)
            if para:
                if para.AsDouble() != getattr(dummy_sum_data, para_name):
                    self._has_changes = True
                    para.Set(getattr(dummy_sum_data, para_name))
            else:
                print("No para found for [{}], please edit the family..".format(para_name))

    def fetch_dummy_target(self, type_name):
        """Fetch target data for dummy summary."""
        dummy_target_data = AreaData.get_data(type_name)
        dummy_target_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)

        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name == self.option.FACTOR_PARA_NAME:
                setattr(dummy_target_data, para_name, 1)
                continue
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue
            if dummy_target_type.LookupParameter(para_name):
                value = dummy_target_type.LookupParameter(para_name).AsDouble()
                dummy_target_data.update(para_name, value)
            else:
                print("No para found for [{}], please edit the family..".format(para_name))

    def fill_delta_data(self, type_name):
        """Fill delta data between actual and target values."""
        dummy_sum_data = AreaData.get_data(self.option.DUMMY_DATA_HOLDER[0])
        dummy_target_data = AreaData.get_data(self.option.DUMMY_DATA_HOLDER[1])
        dummy_delta_data = AreaData.get_data(type_name)
        dummy_delta_type = REVIT_FAMILY.get_family_type_by_name(self.option.CALCULATOR_FAMILY_NAME, type_name, self.doc)

        for para_name in self.option.FAMILY_PARA_COLLECTION:
            if para_name == self.option.FACTOR_PARA_NAME:
                setattr(dummy_delta_data, para_name, 1)
                if dummy_delta_type.LookupParameter(para_name).AsDouble() != 1:
                    self._has_changes = True
                    dummy_delta_type.LookupParameter(para_name).Set(1)
                continue
            if para_name in self.option.INTERNAL_PARA_NAMES.values():
                continue

            if hasattr(dummy_sum_data, para_name) and hasattr(dummy_target_data, para_name):
                value_real = getattr(dummy_sum_data, para_name)
                value_manual = getattr(dummy_target_data, para_name)
                delta = value_real - value_manual
                dummy_delta_data.update(para_name, delta)

            if dummy_delta_type.LookupParameter(para_name):
                if dummy_delta_type.LookupParameter(para_name).AsDouble() != delta:
                    self._has_changes = True
                    dummy_delta_type.LookupParameter(para_name).Set(delta)
            else:
                print("No para found for [{}], please edit the family..".format(para_name))

    def update_schedule_last_update_date(self):
        """Update schedule with last update date only if changes were made."""
        if not self._has_changes:
            return
            
        schedule_view = REVIT_VIEW.get_view_by_name(self.option.FINAL_SCHEDULE_VIEW_NAME, self.doc)
        if not REVIT_SELECTION.is_changable(schedule_view):
            return

        t = DB.Transaction(self.doc, "update schedule last update date")
        t.Start()
        para_name = "Last_Update_Date"
        REVIT_PARAMETER.confirm_shared_para_exist_on_category(self.doc, para_name, DB.BuiltInCategory.OST_Schedules)
        
        if self._owner_holding:
            note = "[Syncing Needed from: {}]".format(", ".join(self._owner_holding))
        else:
            note = TIME.get_formatted_current_time()
            
        schedule_view.LookupParameter(para_name).Set(note)
        t.Commit()

    def update_dgsf_chart(self):
        """Update DGSF chart with current data."""
        T = DB.TransactionGroup(self.doc, "update_dgsf_chart")
        T.Start()

        try:
            self.collect_all_area_data()
            self.update_main_calculator_family_types()
            self.update_summery_calculator_family_types()
            self.update_schedule_last_update_date()
            T.Commit()
        except:
            print(traceback.format_exc())
            T.RollBack()

        if self.show_log:
            NOTIFICATION.messenger(main_text="Program schedule calculator update done!")

        if self._owner_holding:
            NOTIFICATION.messenger(main_text="{} need to sync to display more accurate schedule.".format(
                ", ".join(self._owner_holding)))
        if self._found_bad_area:
            NOTIFICATION.duck_pop(main_text="Attention, there are some un-enclosed area in area plans that might affect your accuracy.\nSee output window for details.")



#########################################################################################








def dgsf_chart_update(doc, show_log=True, dedicated_department=None):
    """Update DGSF chart with current project data.
    
    Args:
        doc (Document): Revit document
        show_log (bool): Whether to show detailed logging
        dedicated_department (str): Department name to filter by, if any
    """
    if USER.IS_DEVELOPER:
        reload(REVIT_SCHEDULE) #pyright: ignore
    if doc is None:
        ERROR_HANDLE.print_note("Document is None in dgsf_chart_update")
        return

    if not dedicated_department:
        # we adoing for general update and should get fresh start
        output = script.get_output()
        output.close_others(True)


    proj_data = REVIT_PROJ_DATA.get_revit_project_data(doc)
    if not proj_data:
        NOTIFICATION.messenger(main_text="No project data found, please initialize the project first.")
        return

    # Get parameter names from project data
    department_key_para_name = proj_data["area_tracking"]["para_dict"]["DEPARTMENT_KEY_PARA"]
    program_type_key_para_name = proj_data["area_tracking"]["para_dict"]["PROGRAM_TYPE_KEY_PARA"]
    program_type_detail_key_para_name = proj_data["area_tracking"]["para_dict"]["PROGRAM_TYPE_DETAIL_KEY_PARA"]

    # Get department mappings
    department_para_mapping = OrderedDict(proj_data["area_tracking"]["table_setting"]["DEPARTMENT_PARA_MAPPING"])
    department_ignore_para_names = proj_data["area_tracking"]["table_setting"]["DEPARTMENT_IGNORE_PARA_NAMES"]

    # Process each option
    for internal_option_name, option_setting in proj_data["area_tracking"]["option_setting"].items():
        level_names = option_setting["levels"]
        option_name = option_setting["option_name"]
        overall_area_scheme_name = option_setting["OVERALL_AREA_SCHEME_NAME"]
        department_area_scheme_name = option_setting["DEPARTMENT_AREA_SCHEME_NAME"]

        # Create and validate option
        option = DepartmentOption(internal_option_name,
                                department_para_mapping,
                                department_ignore_para_names,
                                level_names,
                                option_name,
                                overall_area_scheme_name,
                                department_area_scheme_name,
                                department_key_para_name,
                                program_type_key_para_name,
                                program_type_detail_key_para_name,
                                dedicated_department,
                                doc)

        if not OptionValidation(doc, option, show_log).validate_all():
            print("Validation failed")
            NOTIFICATION.messenger(main_text="Validation failed")
            return

        InternalCheck(doc, option, show_log).update_dgsf_chart()

        if not USER.IS_DEVELOPER:
            continue
        try:
            if dedicated_department is None:
                # if dedicated_department is None, then we are doing all departments as sub chart
                for index, dept in enumerate([x[0] for x in proj_data["area_tracking"]["table_setting"]["DEPARTMENT_PARA_MAPPING"]]):
                    # print("working on sub-chart for department [{}]".format(dept))
                    dgsf_chart_update(doc, show_log=show_log, dedicated_department=dept)
                    if index > 3:
                        print ("TEST: only do max 3 departments for now")
                        break
        except Exception as e:
            ERROR_HANDLE.print_note(traceback.format_exc())

     
        # output = script.get_output()
        # output.close_others(True)
    if dedicated_department is None:
        # only close family docs if we are done doing all departments as sub chart and return as main chart
        FamilyDocToClose.close_family_docs()




if __name__ == "__main__":
    pass