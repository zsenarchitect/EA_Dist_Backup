__doc__ = "Use the shaed excel file to read the correct naming for department and program type. Provide solution to batch fix."
__title__ = "Query Main Excel"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import os
import re

from EnneadTab import ERROR_HANDLE, LOG, EXCEL, NOTIFICATION, TEXT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_AREA_SCHEME, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import forms
# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

# Add path to all_in_one_checker module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'all_in_one_checker.pushbutton'))
from constants import DepartmentOption

DEPARTMENT_KEY_PARA = DepartmentOption.DEPARTMENT_KEY_PARA
PROGRAM_TYPE_KEY_PARA = DepartmentOption.PROGRAM_TYPE_KEY_PARA
PROGRAM_TYPE_DETAIL_KEY_PARA = DepartmentOption.PROGRAM_TYPE_DETAIL_KEY_PARA
AREA_SCHEME_NAME = DepartmentOption.DGSF_SCHEME_NAME


class AbstractDepartment(object):
    raw_data = {}
    secondary_data_column_letter = None
    thirdary_data_column_letter = None
    def __init__(self, begin_row, end_row):
        self.name = self.__class__.__name__
        self.begin_row = begin_row
        self.end_row = end_row
        self.revit_department_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', self.__class__.__name__).upper()
        self.get_subdata()
        self.revit_program_type_names = [self.secondary_data[pointer]["value"] for pointer in sorted(self.secondary_data.keys())]


    def get_subdata(self):
        self.secondary_data = {}
        self.thirdary_data = {}

        def process_value(self, pointer, is_thirdary=False):
            value = self.raw_data[pointer]["value"]
            if value.upper().strip() != value.upper():
                print("Check excel at {}, [{}] should be stripped.".format(pointer, value))
            value = value.upper()
            self.raw_data[pointer]["value"] = value
            return value if value not in ["", " ", None] else None

        for pointer in sorted(self.raw_data.keys()):
            row, column = pointer
            if not self.begin_row <= row <= self.end_row:
                continue
                
            col_letter = EXCEL.column_number_to_letter(column)
            
            # Handle secondary data
            if col_letter == self.__class__.secondary_data_column_letter:
                processed_value = process_value(self, pointer)
                if processed_value:
                    self.secondary_data[pointer] = self.raw_data[pointer]
                    
            # Handle thirdary data
            elif col_letter == self.__class__.thirdary_data_column_letter:
                processed_value = process_value(self, pointer)
                if processed_value:
                    # Find parent program type
                    secondary_col = EXCEL.get_column_index(self.__class__.secondary_data_column_letter)
                    for search_row in range(row, self.begin_row - 1, -1):
                        parent_pointer = (search_row, secondary_col)
                        if parent_pointer in self.secondary_data:
                            self.raw_data[pointer]["parent"] = self.secondary_data[parent_pointer]["value"]
                            break
                    else:
                        self.raw_data[pointer]["parent"] = "PARENT NOT FOUND"
                    self.thirdary_data[pointer] = self.raw_data[pointer]

    def __repr__(self):
        return "{} from row {} to row {}.\nSecondary data column: {}\nRevit department name: {}".format(self.name, self.begin_row, self.end_row, self.secondary_data_column_letter, self.revit_department_name)

class EmergencyDepartment(AbstractDepartment):
    secondary_data_column_letter = "B"
    thirdary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(EmergencyDepartment, self).__init__(begin_row, end_row)
    
class DiagnosticAndTreatment(AbstractDepartment):
    secondary_data_column_letter = "B"
    thirdary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(DiagnosticAndTreatment, self).__init__(begin_row, end_row)

class InpatientCare(AbstractDepartment):
    secondary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(InpatientCare, self).__init__(begin_row, end_row)

class ClinicalSupport(AbstractDepartment):
    secondary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(ClinicalSupport, self).__init__(begin_row, end_row)

class PublicSupport(AbstractDepartment):
    secondary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(PublicSupport, self).__init__(begin_row, end_row)

class AdministrationAndStaffSupport(AbstractDepartment):
    secondary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(AdministrationAndStaffSupport, self).__init__(begin_row, end_row)

class BuildingSupport(AbstractDepartment):
    secondary_data_column_letter = "C"
    def __init__(self, begin_row, end_row):
        super(BuildingSupport, self).__init__(begin_row, end_row)

class Solution:
    
    department_instances = None
    
    def get_bad_areas(self, changed_para):
        """
        Creates a dictionary of areas with department names that don't match the approved list.
        
        Args:
            all_areas: List of area elements from Revit
            good_names: List of approved department names
            
        Returns:
            Dictionary where keys are incorrect department names and values are lists of area elements
        """
        bad_area_dict = {}

        if changed_para == DEPARTMENT_KEY_PARA:
            good_names = [department_instance.revit_department_name for department_instance in self.department_instances]
        elif changed_para == PROGRAM_TYPE_KEY_PARA:
            good_names = ["[{}] {}".format(department_instance.revit_department_name, value["value"]) for department_instance in self.department_instances for value in department_instance.secondary_data.values()]
        elif changed_para == PROGRAM_TYPE_DETAIL_KEY_PARA:
            good_names = ["[{}] [{}] {}".format(department_instance.revit_department_name, value["parent"], value["value"]) for department_instance in self.department_instances for value in department_instance.thirdary_data.values()]

        # need to refetch so each round is fresh
        self.all_areas = REVIT_AREA_SCHEME.get_area_by_scheme_name(AREA_SCHEME_NAME, doc = DOC)
        
        for area in self.all_areas:
            key = area.LookupParameter(changed_para).AsString()
            if changed_para == PROGRAM_TYPE_KEY_PARA:
                key = "[{}] {}".format(area.LookupParameter(DEPARTMENT_KEY_PARA).AsString(), key)
            elif changed_para == PROGRAM_TYPE_DETAIL_KEY_PARA:
                key = "[{}] [{}] {}".format(area.LookupParameter(DEPARTMENT_KEY_PARA).AsString(), area.LookupParameter(PROGRAM_TYPE_KEY_PARA).AsString(), key)
            if key in good_names:
                continue

            if key not in bad_area_dict:
                bad_area_dict[key] = []
            bad_area_dict[key].append(area)

        # Add finish option for UI
        bad_area_dict["_Finish_"] = []


        return bad_area_dict

    def fix_department_assignments(self):
        """Fix department assignments for areas"""
        while True:
            bad_area_dict = self.get_bad_areas(changed_para=DEPARTMENT_KEY_PARA)
            options = sorted(bad_area_dict.keys())
            
            picked_department = forms.SelectFromList.show(options,
                                                        title="Pick a DEPARTMENT to fix")  
            if not picked_department or picked_department == "_Finish_":
                break

            good_names = [department_instance.revit_department_name 
                         for department_instance in self.department_instances]
            
            target_department = forms.SelectFromList.show(sorted(good_names),
                                                        button_name="{} ---> ?".format(picked_department),
                                                        title="Pick a target DEPARTMENT")

            if not target_department:
                break

            t = DB.Transaction(DOC, "Fix department for {}".format(picked_department))
            t.Start()
            for area in bad_area_dict[picked_department]:
                area.LookupParameter(DEPARTMENT_KEY_PARA).Set(target_department)

            NOTIFICATION.messenger("Fixed {} areas".format(len(bad_area_dict[picked_department])))
            t.Commit()

    def fix_program_type_assignments(self):
        """Fix program type assignments for areas"""

        while True:
            # Get bad areas and create source options
            bad_area_dict = self.get_bad_areas(changed_para=PROGRAM_TYPE_KEY_PARA)
            options = sorted(bad_area_dict.keys(), key=lambda x: (x != "_Finish_", x))
            
            # Select source program type, return a list of area
            picked_option = forms.SelectFromList.show(
                options,
                title="Pick a PROGRAM TYPE to fix"
            )

            if not picked_option or picked_option == "_Finish_":
                break

            # Create and sort target options            target_options = [

            target_options = [
                "[{}] {}".format(dept.revit_department_name, prog_type)
                for dept in self.department_instances
                for prog_type in dept.revit_program_type_names
            ]
            target_options.sort()



            best_match = TEXT.fuzzy_search(picked_option, target_options)
            target_options.sort(key=lambda x: x == best_match, reverse=True)

            target_option = forms.SelectFromList.show(
                target_options,
                button_name="{} ---> ?".format(picked_option),
                title="Pick a target PROGRAM TYPE"
            )
            if not target_option:
                break
            

            # Apply changes in transaction
            t = DB.Transaction(DOC, "Fix program type: {}".format(picked_option))
            t.Start()
            dept_name = re.search(r"\[(.*?)\]", target_option).group(1).strip()
            prog_type = re.search(r"\](.*?)$", target_option).group(1).strip()
            for i, area in enumerate(bad_area_dict[picked_option]):
                area.LookupParameter(PROGRAM_TYPE_KEY_PARA).Set(prog_type)
                area.LookupParameter(DEPARTMENT_KEY_PARA).Set(dept_name)
                    
                print ("{}/{}: {}: {} ---> {}".format(i+1, len(bad_area_dict[picked_option]), output.linkify(area.Id), picked_option, target_option))
            NOTIFICATION.messenger("Fixed {} areas".format(len(bad_area_dict[picked_option])))
            t.Commit()

    def fix_program_type_detail_assignments(self):
        """Fix program type detail assignments for areas with a dash of fun"""
        
        while True:
            bad_area_dict = self.get_bad_areas(changed_para=PROGRAM_TYPE_DETAIL_KEY_PARA)
            options = sorted(bad_area_dict.keys(), key=lambda x: (x != "_Finish_", x))

            # Remove any options that end with " None"
            options = [x for x in options if not x.endswith(" None")]

            # Remove empty options after last ]
            options = [x for x in options if not x.strip().endswith("]")]
            
            picked_option = forms.SelectFromList.show(
                options,
                title="Pick a PROGRAM TYPE DETAIL to fix"
            )

            if not picked_option or picked_option == "_Finish_":
                break

            # Create target options with full hierarchy
            target_options = []
            for dept in self.department_instances:
                for detail in dept.thirdary_data.values():
                    full_option = "[{}] [{}] {}".format(
                        dept.revit_department_name,
                        detail["parent"],
                        detail["value"]
                    )
                    target_options.append(full_option)
            
            target_options.sort()

            # Find best fuzzy match and put it at the top
            best_match = TEXT.fuzzy_search(picked_option, target_options)
            target_options.sort(key=lambda x: x == best_match, reverse=True)

            target_option = forms.SelectFromList.show(
                target_options,
                button_name="{} ---> ?".format(picked_option),
                title="Pick a target PROGRAM TYPE DETAIL"
            )
            
            if not target_option:
                break

            # Apply changes in transaction
            t = DB.Transaction(DOC, "Fix program type detail: {}".format(picked_option))
            t.Start()
            
            # Extract department, program type, and detail from target
            matches = re.findall(r"\[(.*?)\]", target_option)
            dept_name = matches[0].strip()
            prog_type = matches[1].strip()
            detail = re.search(r"\](.*?)$", target_option).group(1).strip()

            for i, area in enumerate(bad_area_dict[picked_option]):
                area.LookupParameter(PROGRAM_TYPE_DETAIL_KEY_PARA).Set(detail)
                area.LookupParameter(PROGRAM_TYPE_KEY_PARA).Set(prog_type)
                area.LookupParameter(DEPARTMENT_KEY_PARA).Set(dept_name)
                
                print ("{}/{}: {}: {} ---> {}".format(i+1, len(bad_area_dict[picked_option]), output.linkify(area.Id), picked_option, target_option))

            NOTIFICATION.messenger("Successfully fixed {} areas!".format(
                len(bad_area_dict[picked_option])
            ))
            t.Commit()



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def query_main_excel():
    NOTIFICATION.messenger("Reading excel file...")
    

    raw_data = EXCEL.read_data_from_excel(DepartmentOption.SOURCE_EXCEL, 
                                      worksheet="EA Benchmarking DGSF Tracker", 
                                      return_dict=True,
                                      headless=True) # if have permission lock---> set it as always availble in this PC from desktop connecter.


    AbstractDepartment.raw_data = raw_data

    excel_section_list = [
        "A - EMERGENCY DEPARTMENT",
        "B - DIAGNOSTIC AND TREATMENT",
        "C - INPATIENT CARE",
        "D - CLINICAL SUPPORT",
        "E - PUBLIC SUPPORT",
        "F - ADMINISTRATION AND STAFF SUPPORT",
        "G - BUILDING SUPPORT",
        "TOTAL DEPARTMENTAL PROGRAM AREA (DGSF)"
        ]

    opts = ["Fix Department Assignments", 
            ["Fix Program Type Assignments", "..."],
            ["Fix Program Type Detail Assignments", "Work in progress"]
            ]
    res = REVIT_FORMS.dialogue(options = opts, main_text="What do you want to fix?")
    if not res:
        return

    solution = Solution()
    solution.department_instances = create_department_instances(raw_data, excel_section_list)

    # for department in departments:
    #     print (department, department.secondary_data)



    


    if res == opts[0]:
        solution.fix_department_assignments()

    if res == opts[1][0]:
        solution.fix_program_type_assignments()

    if res == opts[2][0]:
        solution.fix_program_type_detail_assignments()



def create_department_instances(data, excel_section_list):
    current_section_title = None
    current_begin_row = None
    department_instances = []  # Keep track of all instances

    for pointer in sorted(data.keys()):
        row, column = pointer
        value = data[pointer]["value"]
        
        if value in excel_section_list:
            # If we already have a section in progress, create instance with previous section
            if current_section_title and current_begin_row:
                class_name = re.sub(r'^[A-Z] - ', '', current_section_title.title()).replace(" ", "")
                if class_name in globals():
                    department_class = globals()[class_name]
                    department_instances.append(
                        department_class(
                            begin_row=current_begin_row,
                            end_row=row - 1  # Previous row is the end of last section
                        )
                    )
            
            # Start tracking new section
            current_section_title = value
            current_begin_row = row
            
    # Don't forget to create instance for the last section
    if current_section_title and current_begin_row:
        class_name = re.sub(r'^[A-Z] - ', '', current_section_title.title()).replace(" ", "")
        if class_name in globals():
            department_class = globals()[class_name]
            department_instances.append(
                department_class(
                    begin_row=current_begin_row,
                    end_row=max(row for row, _ in data.keys())  # Use last row in data
                )
            )
    
    return department_instances


################## main code below #####################
if __name__ == "__main__":
    from pyrevit import script
    output = script.get_output()
    query_main_excel()







