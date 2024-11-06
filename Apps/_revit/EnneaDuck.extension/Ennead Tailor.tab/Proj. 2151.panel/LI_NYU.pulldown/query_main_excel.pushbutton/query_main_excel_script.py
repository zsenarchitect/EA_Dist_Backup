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
DEPARTMENT_KEY_PARA = "Area_$Department"
PROGRAM_TYPE_KEY_PARA = "Area_$Department_Program Type"
AREA_SCHEME_NAME = "DGSF Scheme"


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

        
        for pointer in sorted(self.raw_data.keys()):
            row, column = pointer
            if not self.begin_row <= row <= self.end_row:
                continue
            if EXCEL.column_number_to_letter(column) == self.__class__.secondary_data_column_letter:
                value = self.raw_data[pointer]["value"]
                self.raw_data[pointer]["value"] = value.upper()
                if value not in ["", " ", None]:
                    self.secondary_data[(row, column)] = self.raw_data[pointer]


            if EXCEL.column_number_to_letter(column) == self.__class__.thirdary_data_column_letter:
                value = self.raw_data[pointer]["value"]
                self.raw_data[pointer]["value"] = value.upper()
                if value not in ["", " ", None]:
                    self.thirdary_data[(row, column)] = self.raw_data[pointer]

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
    
    def get_bad_areas(self, is_program_type=False):
        """
        Creates a dictionary of areas with department names that don't match the approved list.
        
        Args:
            all_areas: List of area elements from Revit
            good_names: List of approved department names
            
        Returns:
            Dictionary where keys are incorrect department names and values are lists of area elements
        """
        bad_area_dict = {}

        if is_program_type:
            para_name = PROGRAM_TYPE_KEY_PARA
            good_names = [(department_instance.revit_department_name, value["value"]) for department_instance in self.department_instances for value in department_instance.secondary_data.values()]
        else:
            para_name = DEPARTMENT_KEY_PARA
            good_names = [department_instance.revit_department_name for department_instance in self.department_instances]


        # need to refetch so each round is fresh
        self.all_areas = REVIT_AREA_SCHEME.get_area_by_scheme_name(AREA_SCHEME_NAME, doc = DOC)
        
        for area in self.all_areas:
            key = area.LookupParameter(para_name).AsString()
            if is_program_type:
                key = (area.LookupParameter(DEPARTMENT_KEY_PARA).AsString(), key)
            if key in good_names:
                continue

            if key not in bad_area_dict:
                bad_area_dict[key] = []
            bad_area_dict[key].append(area)

        # Add finish option for UI
        if is_program_type:
            bad_area_dict[("_Finish_", "_Finish_")] = []
        else:
            bad_area_dict["_Finish_"] = []
        
        return bad_area_dict

    def fix_department_assignments(self):
        """Fix department assignments for areas"""
        while True:
            bad_area_dict = self.get_bad_areas(is_program_type=False)
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
            for area in bad_area_dict[target_department]:
                area.LookupParameter(DEPARTMENT_KEY_PARA).Set(target_department)

            NOTIFICATION.messenger("Fixed {} areas".format(len(bad_area_dict[target_department])))
            t.Commit()

    def fix_program_type_assignments(self):
        """Fix program type assignments for areas"""
        class ProgramTypeOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}] {}".format(self.department_name, self.program_type)

        class SourceOption(ProgramTypeOption):
            def __init__(self, areas, department_name, program_type):
                self.item = areas
                self.department_name = department_name
                self.program_type = program_type

        class TargetOption(ProgramTypeOption):
            def __init__(self, program_type, department_name):
                self.item = program_type
                self.department_name = department_name
                self.program_type = program_type

        while True:
            # Get bad areas and create source options
            bad_area_dict = self.get_bad_areas(is_program_type=True)
            source_options = [SourceOption(areas, dept_name, prog_type) 
                            for (dept_name, prog_type), areas in bad_area_dict.items()]
            source_options.sort(key=lambda x: x.name)
            
            # Select source program type, return a list of area
            picked_option = forms.SelectFromList.show(
                source_options,
                title="Pick a PROGRAM TYPE to fix"
            )

            if not picked_option or len(picked_option) == 0:
                break

            # Create and sort target options            target_options = [

            target_options = [
                TargetOption(prog_type, dept.revit_department_name)
                for dept in self.department_instances
                for prog_type in dept.revit_program_type_names
            ]
            target_options.sort(key=lambda x: x.name)

            # Select target program type
            picked_source_program_type_name = "[{}] {}".format(picked_option[0].LookupParameter(DEPARTMENT_KEY_PARA).AsString(), 
                                                               picked_option[0].LookupParameter(PROGRAM_TYPE_KEY_PARA).AsString())

            best_match = TEXT.fuzzy_search(picked_source_program_type_name, [option.name for option in target_options])
            target_options.sort(key=lambda x: x.name == best_match, reverse=True)

            target_option = forms.SelectFromList.show(
                target_options,
                button_name="{} ---> ?".format(picked_source_program_type_name),
                title="Pick a target PROGRAM TYPE"
            )
            if not target_option:
                break

            # Apply changes in transaction
            t = DB.Transaction(DOC, "Fix program type: {}".format(picked_source_program_type_name))
            t.Start()
            for area in picked_option:
                area.LookupParameter(PROGRAM_TYPE_KEY_PARA).Set(target_option)
            NOTIFICATION.messenger("Fixed {} areas".format(len(picked_option)))
            t.Commit()

    def fix_assignments(self, is_program_type=False):
        """Main entry point for fixing assignments"""
        if is_program_type:
            self.fix_program_type_assignments()
        else:
            self.fix_department_assignments()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def query_main_excel():
    NOTIFICATION.messenger("Reading excel file...")
    source_excel = "{}\\DC\\ACCDocs\\Ennead Architects LLP\\2151_NYULI\\Project Files\\00_EA-EC Teams Files\\4_Programming\\_Public Shared\\Web Portal Only_ACTIVE.NYULI_Program_EA.EC.xlsx".format(os.getenv("USERPROFILE"))

    raw_data = EXCEL.read_data_from_excel(source_excel, 
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

    opts = ["Fix Department Assignments", ["Fix Program Type Assignments", "..."]]
    res = REVIT_FORMS.dialogue(options = opts, main_text="What do you want to fix?")
    if not res:
        return

    solution = Solution()
    solution.department_instances = create_department_instances(raw_data, excel_section_list)

    # for department in departments:
    #     print (department, department.secondary_data)



    


    if res == opts[0]:
        solution.fix_assignments(is_program_type=False)

    if res == opts[1][0]:
        solution.fix_assignments(is_program_type=True)


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
    query_main_excel()







