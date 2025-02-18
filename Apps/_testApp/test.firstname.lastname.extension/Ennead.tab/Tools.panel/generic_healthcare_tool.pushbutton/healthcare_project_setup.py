from EnneadTab import NOTIFICATION, FOLDER, ENVIRONMENT # pyright: ignore   
from EnneadTab.REVIT import REVIT_PARAMETER, REVIT_COLOR_SCHEME
from Autodesk.Revit import DB # pyright: ignore
import os
from pyrevit import forms

############ data template
TEMPLATE_DATA = {
    "container_file": None,
    "is_update_view_name_format": False,
    "parking_data": {
        "auto_update_enabled": False,
        "setting": {}
    },
    "area_tracking": {
        "auto_update_enabled": True,
        "para_dict": {
            "DEPARTMENT_KEY_PARA": "Area_$Department",
            "PROGRAM_TYPE_KEY_PARA": "Area_$Department_Program Type",
            "PROGRAM_TYPE_DETAIL_KEY_PARA": "Area_$Department_Program Type Detail"
        },
        "table_setting": {
            "DEPARTMENT_PARA_MAPPING": [
                            ("DIAGNOSTIC AND TREATMENT", "D&T"),
                            ("EMERGENCY DEPARTMENT", "ED"),
                            ("INPATIENT CARE", "BEDS"),
                            ("PUBLIC SUPPORT", "PUBLIC SUPPORT"),
                            ("ADMINISTRATION AND STAFF SUPPORT", "ADMIN"),
                            ("CLINICAL SUPPORT", "CLINICAL SUPPORT"),
                            ("BUILDING SUPPORT", "BUILDING SUPPORT"),
                            ("UNASSIGNED", "UNASSIGNED")
                            ],
            "DEPARTMENT_IGNORE_PARA_NAMES": ["PUBLIC CIRCULATION",
                                            "SERVICE CIRCULATION"]
        },

        "option_setting": {
            "primary_option": {
                "option_name": "",
                "levels": [],
                "OVERALL_AREA_SCHEME_NAME": "GFA Scheme",
                "DEPARTMENT_AREA_SCHEME_NAME": "DGSF Scheme"
            }
        }


    },
    "wall_type_update": {
        "auto_update_enabled": False,
        "setting": {}
    },
    "parking_update": {
        "auto_update_enabled": False,
        "setting": {}
    },
    "color_update": {
        "auto_update_enabled": False,
        "setting": {
            "excel_path": None,
            "naming_map": {
                "department_color_map":["Department Category_Primary"],
                "program_color_map":["Department Program Type_Primary"]
            }
        }
    }
}

############### MAIN SETUP FUNCTIONS ###############
def setup_healthcare_project(doc):
    t = DB.Transaction(doc, "setup healthcare project")
    t.Start()

    proj_data = REVIT_PARAMETER.get_revit_project_data(doc)
    if not proj_data:
        proj_data = TEMPLATE_DATA

    update_project_levels_in_project_data(doc, proj_data)
    setup_pim_number_parameter(doc)
    if not setup_area_tracking_parameters(doc, proj_data):
        return t.RollBack()

    if not setup_schedule_update_date_parameter(doc):
        return t.RollBack()


    REVIT_PARAMETER.set_revit_project_data(doc, proj_data)
    REVIT_PARAMETER.mark_doc_to_project_data_file(doc)
    t.Commit()
    open_project_data_file(doc)
    NOTIFICATION.messenger("Healthcare project setup complete.")

def setup_schedule_update_date_parameter(doc):
    para_name = "Last_Update_Date"
    if not REVIT_PARAMETER.confirm_shared_para_exist_on_category(doc, 
                                                                 para_name,
                                                                 DB.BuiltInCategory.OST_Schedules):
        return False
    return True

def setup_pim_number_parameter(doc):
    """Sets up PIM Number parameter in project info"""
    para_name = "PIM_Number"
    para = REVIT_PARAMETER.get_project_info_para_by_name(doc, para_name)
    if not para:
        definition = REVIT_PARAMETER.get_shared_para_definition_in_txt_file_by_name(doc, para_name)
        if not definition:
            definition = REVIT_PARAMETER.create_shared_parameter_in_txt_file(doc, para_name, DB.SpecTypeId.String.Text)
        
        REVIT_PARAMETER.add_shared_parameter_to_project_doc(doc, 
                                                        definition, 
                                                        "Data", 
                                                        [DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_ProjectInformation)])
        para = REVIT_PARAMETER.get_project_info_para_by_name(doc, para_name)

    default_value = "Replace Me with the real PIM Number"
    if para.AsString() != default_value:
        para.Set(default_value)

def setup_area_tracking_parameters(doc, proj_data):
    """Ensures required area parameters exist in the project"""
    for para_name in proj_data["area_tracking"].get("para_dict").values():
        if not REVIT_PARAMETER.confirm_shared_para_exist_on_category(doc, para_name,DB.BuiltInCategory.OST_Areas):
            return False
    return True



def update_project_levels_in_project_data(doc, proj_data):
    """Updates project levels in tracking data"""
    levels = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements())
    levels.sort(key=lambda x: x.Elevation, reverse=True)

    picked_levels = forms.SelectFromList.show(levels, name_attr="Name", title="Select Levels to include in calculation", button_name="Select Levels", multiselect=True)
    level_names = [level.Name for level in picked_levels]

    for option_setting in proj_data["area_tracking"]["option_setting"].values():
        option_setting["levels"] = level_names

############### FILE OPERATIONS ###############
def open_project_data_file(doc):
    data_file = REVIT_PARAMETER.get_project_data_file(doc)
    file = FOLDER.get_shared_dump_folder_file(data_file)
    os.startfile(file)

def edit_project_data_file(doc):
    editor = ProjectDataEditor(doc)
    editor.edit_project_data()

############### PROJECT DATA EDITOR CLASS ###############
class ProjectDataEditor:
    def __init__(self, doc):
        self.doc = doc
        self.project_data = REVIT_PARAMETER.get_revit_project_data(doc)
        
        # Define menu configurations
        self.main_menu = {
            "1. Reattach Project Data To Exisitng Setup": self._reattach_project_data,
            "2. Healthcare Area Tracking": self._edit_area_tracking,
            "3. Auto View Name Update": self._edit_auto_view_name_update,
            "4. Color Update": self._edit_color_update,
            "5. Save and Close": None

        }
        
        self.area_tracking_menu = {
            "1. Enable/Disable Auto Update": self._edit_auto_update_enabled,
            "2. Edit Design Option": self._edit_design_option,
            "3. Duplicate Design Option": self._duplicate_design_option,
            "4. Delete Design Option": self._delete_design_option,
            "5. Return to Previous Menu": None
        }
        


        self.design_option_menu = {
            "1. Edit Levels": lambda opt: self._edit_levels(opt),
            "2. Edit Overall Area Scheme": lambda opt: self._edit_option_setting(opt, "OVERALL_AREA_SCHEME_NAME", "Overall Area Scheme"),
            "3. Edit Department Area Scheme": lambda opt: self._edit_option_setting(opt, "DEPARTMENT_AREA_SCHEME_NAME", "Department Area Scheme"),
            "4. Edit Option Name": lambda opt: self._edit_option_setting(opt, "option_name", "Option Name"),
            "5. Return to Previous Menu": None
        }

        self.color_update_menu = {
            "1. Edit Color Update": self._edit_color_update,
            "2. Edit Excel Path": self._edit_excel_path,
            "3. Edit ColorScheme Naming Map": self._edit_naming_map,
            "4. Return to Previous Menu": None
        }

    def edit_project_data(self):
        """Main entry point for editing project data"""
        if not self.project_data:
            NOTIFICATION.messenger("No project data found.")
            return
        
        while True:
            selection = self._show_menu("Project Data Editor", self.main_menu)
            if not selection:
                break
            function = self.main_menu[selection]
            if self._is_return_option(selection):
                break
            function()



    def _show_menu(self, title, options, **kwargs):
        """Generic menu display and handling"""
        return forms.SelectFromList.show(
            sorted(options.keys()),
            multiselect=False,
            title=title,
            button_name="Select",
            **kwargs
        )

    def _is_return_option(self, selection):
        """Check if the selected option is a return option"""
        return selection is None or "Return to Previous Menu" in str(selection) or "Save and Close" in str(selection)

    def _edit_color_update(self):
        """Edit color update options"""
        while True:
            res = self._show_menu("Auto Color Update Options", self.color_update_menu)
            if self._is_return_option(res):
                break
            
            if res in self.color_update_menu:
                self.color_update_menu[res]()

    def _edit_excel_path(self):
        """Edit excel path"""
        while True:
            res = forms.pick_file(
                title="Select Excel File",
                files_filter="Excel Files (*.xls)|*.xls"
            )
            if res:
                self.project_data["color_update"]["setting"]["excel_path"] = res
                self._save_changes()
                break

    def _edit_naming_map(self):
        """Edit naming map"""
        while True:
            department_color_scheme_names = REVIT_COLOR_SCHEME.pick_color_schemes(self.doc, 
                                                                                 title="Select the [DEPARTMENT] color schemes", 
                                                                                 button_name="Select [DEPARTMENT] color schemes")
            if not department_color_scheme_names:
                NOTIFICATION.messenger(main_text="No [DEPARTMENT] color scheme selected")
                continue
            
            program_color_scheme_names = REVIT_COLOR_SCHEME.pick_color_schemes(self.doc, 
                                                                                 title="Select the [PROGRAM] color schemes", 
                                                                                 button_name="Select [PROGRAM] color schemes")
            if not program_color_scheme_names:
                NOTIFICATION.messenger(main_text="No [PROGRAM] color scheme selected")
                continue
            
            self.project_data["color_update"]["setting"]["naming_map"]["department_color_map"] = department_color_scheme_names
            self.project_data["color_update"]["setting"]["naming_map"]["program_color_map"] = program_color_scheme_names
            self._save_changes()
            break
    


    def _edit_area_tracking(self):
        """Handle area tracking editing options"""
        while True:
            res = self._show_menu("Area Tracking Options", self.area_tracking_menu)
            if self._is_return_option(res):
                break
            
            if res in self.area_tracking_menu:
                self.area_tracking_menu[res]()

    def _edit_design_option(self):
        """Edit specific design option settings"""
        selected_option = self._select_design_option("Select Design Option")
        if not selected_option:
            return

        while True:
            res = self._show_menu(
                "Editing Option: {}".format(selected_option),
                self.design_option_menu
            )
            if self._is_return_option(res):
                break
            


            if res in self.design_option_menu:
                self.design_option_menu[res](selected_option)

    def _toggle_setting(self, setting_path, title):
        """Generic toggle setting handler"""
        options = {
            "1. Enable Auto Update": True,
            "2. Disable Auto Update": False,
            "3. Return to Previous Menu": None
        }
        
        while True:
            res = self._show_menu(
                title,
                options,
                
            )
            if self._is_return_option(res):
                break
            

            if res in options and options[res] is not None:
                self._set_nested_dict_value(
                    self.project_data,
                    setting_path,
                    options[res]
                )
                self._save_changes()
                break

    def _edit_option_setting(self, option_name, setting_key, title):
        """Generic option setting editor"""
        while True:
            if option_name not in self.project_data["area_tracking"]["option_setting"]:
                NOTIFICATION.messenger("Option '{}' not found due to renaming, return to previous menu and re-select option using the new name.".format(option_name))
                break
            
            current_value = self.project_data["area_tracking"]["option_setting"][option_name][setting_key]
            new_value = forms.ask_for_string(
                default=current_value,
                prompt="Enter {} (ESC to cancel)".format(title.lower()),
                title=title
            )


            

            if new_value is None:  # User pressed ESC
                break
            
            if new_value.strip():  # Ensure non-empty value
                self.project_data["area_tracking"]["option_setting"][option_name][setting_key] = new_value

                if setting_key == "option_name":
                    self.project_data["area_tracking"]["option_setting"][new_value] = self.project_data["area_tracking"]["option_setting"][option_name].copy()
                    del self.project_data["area_tracking"]["option_setting"][option_name]

                self._save_changes()
                break


    def _select_design_option(self, title):
        """Generic design option selector"""
        options = list(self.project_data["area_tracking"]["option_setting"].keys())
        options.append("Return to Previous Menu")
        
        return forms.SelectFromList.show(
            options,
            multiselect=False,
            title=title,
            button_name="Select"
        )

    def _duplicate_design_option(self):
        """Create a copy of an existing design option"""
        while True:
            source_option = self._select_design_option("Select Option to Duplicate")
            if self._is_return_option(source_option):
                break


            design_options = self.project_data["area_tracking"]["option_setting"].keys()
            new_name = forms.ask_for_unique_string(
                reserved_values=design_options,
                title="New Option Name (ESC to cancel)",
                button_name="Create"
            )

            
            if new_name is None:  # User pressed ESC
                continue
                
            if new_name:
                self.project_data["area_tracking"]["option_setting"][new_name] = \
                    self.project_data["area_tracking"]["option_setting"][source_option].copy()

                self.project_data["area_tracking"]["option_setting"][new_name]["option_name"] = new_name
                self._save_changes()
                break

    def _edit_levels(self, option_name):
        """Edit level selection for a design option"""
        while True:
            levels = list(DB.FilteredElementCollector(self.doc)
                         .OfCategory(DB.BuiltInCategory.OST_Levels)
                         .WhereElementIsNotElementType()
                         .ToElements())
            levels.sort(key=lambda x: x.Elevation, reverse=True)
            
            
            # Add return option
            level_options = list(levels)

            picked_levels = forms.SelectFromList.show(
                level_options,
                name_attr="Name",
                title="Select Levels for Calculation",
                button_name="Confirm",
                multiselect=True
            )
            
            if not picked_levels:
                break
            
            level_names = [level.Name for level in picked_levels]
            self.project_data["area_tracking"]["option_setting"][option_name]["levels"] = level_names
            self._save_changes()
            break

    def _edit_auto_update_enabled(self):
        """Toggle auto update setting for area tracking"""
        self._toggle_setting(
            ["area_tracking", "auto_update_enabled"],
            "Toggle auto update for area tracking"
        )

    def _edit_auto_view_name_update(self):
        """Toggle auto view name update setting"""
        self._toggle_setting(
            ["is_update_view_name_format"],
            "Toggle auto view name update"
        )

    def _set_nested_dict_value(self, dictionary, path, value):
        """Helper method to set nested dictionary value using a path list
        
        Example:
        dictionary = {
            "area_tracking": {
                "auto_update_enabled": False,
                "settings": {"color": "blue"}
            }
        }
        
        # To update auto_update_enabled:
        path = ["area_tracking", "auto_update_enabled"]
        value = True
        # Result: dictionary["area_tracking"]["auto_update_enabled"] = True
        
        # To update color:
        path = ["area_tracking", "settings", "color"]
        value = "red"
        # Result: dictionary["area_tracking"]["settings"]["color"] = "red"
        """
        current = dictionary
        for key in path[:-1]:  # Navigate through all keys except the last one
            current = current[key]
        current[path[-1]] = value  # Set the value at the final key

    def _save_changes(self):
        """Save changes to project data"""
        REVIT_PARAMETER.set_revit_project_data(self.doc, self.project_data)
        NOTIFICATION.messenger("Project data updated successfully!")

    def _delete_design_option(self):
        """Delete a selected design option"""
        while True:
            option_to_delete = self._select_design_option("Select Option to Delete")
            if self._is_return_option(option_to_delete):
                break
                


            confirm = forms.alert(
                msg="Are you sure you want to delete option '{}'?".format(option_to_delete),
                title="Confirm Deletion",
                ok=False,
                yes=True,
                no=True
            )
            
            if confirm:
                del self.project_data["area_tracking"]["option_setting"][option_to_delete]
                self._save_changes()
                NOTIFICATION.messenger("Design option '{}' has been deleted.".format(option_to_delete))
                break


    def _reattach_project_data(self):
        t = DB.Transaction(self.doc, "Reattach Project Data")
        t.Start()
        REVIT_PARAMETER.reattach_project_data(self.doc)
        t.Commit()

############### ENTRY POINT ###############
if __name__ == "__main__":
    pass