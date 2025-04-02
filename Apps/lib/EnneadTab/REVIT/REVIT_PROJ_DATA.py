import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import NOTIFICATION
import DATA_FILE
import FOLDER
import ENVIRONMENT
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    from pyrevit import forms
    import REVIT_PARAMETER
    import REVIT_COLOR_SCHEME
except:
    pass

PROJECT_DATA_PREFIX = "ProjectData_" # this is the prefix used in the shared dump folder to identify the project data file
PROJECT_DATA_PARA_NAME = "EnneadTab_Data" # this is the name of the parameter in the project information that stores the project data file name


TEMPLATE_DATA = {
    "container_file": None,
    "is_update_view_name_format": False,
    "parking_data": {
        "auto_update_enabled": False,
        "setting": {}
    },
    "area_tracking": {
        "auto_update_enabled": False,
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
    },
    "keynote_assistant": {
        "setting": {
            "extended_db_excel_path": None
        }
    }
}

def is_setup_project_data_para_exist(doc):
    """Check if the EnneadTab_Data parameter exists in project information.
    
    Args:
        doc: Current Revit document
        
    Returns:
        bool: True if parameter exists, False otherwise
    """
    para = REVIT_PARAMETER.get_project_info_para_by_name(doc, PROJECT_DATA_PARA_NAME)
    if para:
        return True
    return False


def setup_project_data(doc):
    if is_setup_project_data_para_exist(doc):
        return

    proj_data = get_revit_project_data(doc)
    if not proj_data:
        proj_data = TEMPLATE_DATA



    setup_schedule_update_date_parameter(doc)


    set_revit_project_data(doc, proj_data)
    mark_doc_to_project_data_file(doc)


    NOTIFICATION.messenger("Healthcare project setup complete.")

def setup_schedule_update_date_parameter(doc):
    para_name = "Last_Update_Date"
    if not REVIT_PARAMETER.confirm_shared_para_exist_on_category(doc, 
                                                                 para_name,
                                                                 DB.BuiltInCategory.OST_Schedules):
        return False
    return True

def get_project_data_name(doc):
    """Get or create the project data identifier parameter.
    
    Creates the shared parameter if it doesn't exist and initializes it
    with the document title.
    
    Args:
        doc: Current Revit document
        
    Returns:
        str: Value of the project data parameter
    """
    # Check if parameter exists using the helper function
    if not is_setup_project_data_para_exist(doc):
        definition = REVIT_PARAMETER.get_shared_para_definition_in_txt_file_by_name(doc, PROJECT_DATA_PARA_NAME)
        if not definition:
            definition = REVIT_PARAMETER.create_shared_parameter_in_txt_file(doc, PROJECT_DATA_PARA_NAME, DB.SpecTypeId.String.Text)
        REVIT_PARAMETER.add_shared_parameter_to_project_doc(doc, 
                                                        definition, 
                                                        "Data", 
                                                        [DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_ProjectInformation)])

        para = REVIT_PARAMETER.get_project_info_para_by_name(doc, PROJECT_DATA_PARA_NAME)
        para.Set(doc.Title)  # Set initial value to document title

    # Get the parameter value
    return REVIT_PARAMETER.get_project_info_para_by_name(doc, PROJECT_DATA_PARA_NAME).AsString()

def get_project_data_file(doc):
    """Generate the project data file name based on project identifier.
    
    Args:
        doc: Current Revit document
        
    Returns:
        str: Full filename for project data storage
    """
    project_data_name = get_project_data_name(doc)
    return "{}{}.sexyDuck".format(PROJECT_DATA_PREFIX, project_data_name)


def mark_doc_to_project_data_file(doc):
    """Record current document in the list of documents using this project data.
    
    Args:
        doc: Current Revit document
    """
    data = get_revit_project_data(doc)
    if "docs_attaching" not in data:
        data["docs_attaching"] = []
    data["docs_attaching"].append(doc.Title)
    set_revit_project_data(doc, data)

def reattach_project_data(doc):
    """Reattach project data from an existing setup file.
    
    Allows user to select from available project data files in the shared
    drive and updates the current document's project data reference.
    
    Args:
        doc: Current Revit document
    """
    # Print current project data file
    current_data_name = get_project_data_name(doc)
    print("Current project data file: {}".format(current_data_name))

    # Get all project data files from shared dump folder
    data_files = [f for f in os.listdir(FOLDER.SHARED_DUMP_FOLDER) if f.startswith(PROJECT_DATA_PREFIX) and f.endswith(".sexyDuck")]
    
    # Extract XXX parts for display (without extension)
    display_options = [f.replace(PROJECT_DATA_PREFIX, "").replace(".sexyDuck", "") for f in data_files]
    
    if not display_options:
        NOTIFICATION.messenger("No project data files found in L drive.")
        return
    
    # Let user pick from the list
    selected = forms.SelectFromList.show(
        display_options,
        multiselect=False,
        title="Select Project Data File to Attach",
        button_name="Select"
    )
        
    if not selected:
        return
    
    # Update project data file reference
    try:
        REVIT_PARAMETER.get_project_info_para_by_name(doc, PROJECT_DATA_PARA_NAME).Set("{}".format(selected))
        mark_doc_to_project_data_file(doc)
        NOTIFICATION.messenger("Successfully reattached project data.")
    except Exception as e:
        NOTIFICATION.messenger("Failed to reattach project data: {}".format(str(e)))


def get_revit_project_data(doc):
    """Retrieve project data from shared storage.
    
    Args:
        doc: Current Revit document
        
    Returns:
        dict: Project data dictionary from storage
    """
    ENVIRONMENT.alert_l_drive_not_available()
    return DATA_FILE.get_data(get_project_data_file(doc), is_local=False)


def set_revit_project_data(doc, data):
    """Save project data to shared storage.
    
    Args:
        doc: Current Revit document
        data: Dictionary containing project data to save
    """
    DATA_FILE.set_data(data, get_project_data_file(doc), is_local=False)


############### FILE OPERATIONS ###############
def open_project_data_file(doc):
    if not ENVIRONMENT.alert_l_drive_not_available(play_sound=True):
        return 
    data_file = get_project_data_file(doc)
    file = FOLDER.get_shared_dump_folder_file(data_file)
    os.startfile(file)

def edit_project_data_file(doc):
    editor = ProjectDataEditor(doc)
    editor.edit_project_data()

############### PROJECT DATA EDITOR CLASS ###############
class ProjectDataEditor:
    def __init__(self, doc):
        self.doc = doc
        self.project_data = get_revit_project_data(doc)
        
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

        if not ENVIRONMENT.alert_l_drive_not_available(play_sound=True):
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
                files_filter="Excel Files (*.xls;*.xlsx)|*.xls;*.xlsx"
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
        set_revit_project_data(self.doc, self.project_data)
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
        reattach_project_data(self.doc)
        t.Commit()
