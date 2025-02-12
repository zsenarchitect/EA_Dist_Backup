#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Batch rename family names to follow Ennead standard naming convention.

Format: 
    CATEGORY_Description_INTENDED[_DESIGNATOR][_HOSTING]

Examples:
    DOOR_SingleFlush_PE_GEN_WH
    WIND_Casement_PE_EXT
    FURN_ConferenceTable_PE
    
Notes:
    - CATEGORY: 2-4 uppercase letters (e.g., DOOR, WIND, FURN)
    - Description: CamelCase (e.g., SingleFlush, Casement)
    - INTENDED: 2-4 uppercase letters (e.g., PE for Production)
    - DESIGNATOR: Optional, 2-4 uppercase letters (e.g., GEN, EXT)
    - HOSTING: Optional, 2 letters for hosting type (e.g., WH for Wall Hosted)
"""
__title__ = "Batch Format\nFamily Name"

import re
from Autodesk.Revit import DB  # pyright: ignore
from pyrevit import forms, script
import proDUCKtion  # pyright: ignore
from EnneadTab import ERROR_HANDLE, LOG, UI, NOTIFICATION, OUTPUT, FOLDER, EXCEL
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY

# Initialize Revit document
proDUCKtion.validify()
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

# Add after imports, before class definitions
def show_naming_rules():
    """Display the naming convention rules image."""
    import os
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, "naming_rule.png")
    if os.path.exists(image_path):
        OUTPUT.get_output().write(image_path)
    else:
        print("Warning: naming_rule.png not found in script directory")



class HostingMethodMapper:
    """Maps and validates family hosting methods.
    
    Features:
        - Maps standard hosting methods to abbreviations
        - Validates family hosting against name suffix
        - Analyzes document-wide hosting behaviors
    """
    def __init__(self):
        self.mapping = {
            "Wall": "WA",
            "Ceiling": "CE",
            "Floor": "FL",
            "Face": "FC",
            "OneLevelBased": "LH",
            "OneLevelBasedHosted": "LH",
            "TwoLevelsBased": "TL",
            "ViewBased": "VB",
            "WorkPlaneBased": "WP",
            "CurveBased": "CV",
            "CurveBasedDetail": "CD",
            "CurveDrivenStructural": "CS",
            "Adaptive": "AD",
            
            # Non-hosted cases
            "Not Hosted": None,
            "Invalid": None,
            None: None  # Handle cases where hosting parameter doesn't exist
        }
    
    @staticmethod
    def get_abbreviation(hosting_method):
        """
        Get abbreviation for a hosting method
        Args:
            hosting_method (str): The hosting method from family parameter
        Returns:
            str or None: Corresponding abbreviation or None if not hosted
        """
        return HostingMethodMapper.mapping.get(hosting_method)

    @staticmethod
    def validate_hosting_method(family, family_name, name_match, show_log = False):
        """
        Validates if the family's hosting method matches its name
        Args:
            family: Revit family element
            family_name (str): Name of the family
            name_match: Regex match object from family name pattern
        Returns:
            bool: True if hosting method is valid, False otherwise
        """
        try:
            # Get actual hosting method from family
            hosting_param = family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
            if not hosting_param:
                if show_log:
                    print("[{}]: No hosting parameter found".format(family_name))
                    return True  # No hosting parameter means non-hosted family
                
            actual_hosting = hosting_param.AsValueString()
           
            actual_abbr = HostingMethodMapper.get_abbreviation(actual_hosting)
            
            # Get hosting method from name (last group in regex)
            groups = name_match.groups()
            name_hosting_abbr = groups[-1][1:] if groups[-1] else None  # Remove leading underscore if exists
            
            # Compare actual vs name-specified hosting
            if actual_abbr != name_hosting_abbr:
                if actual_abbr:  # If family is hosted but name doesn't match
                    if show_log:
                        print("[{}]: Hosting method mismatch - Name: {}, Actual: {} ({})".format(
                            family_name,
                            name_hosting_abbr or "None",
                            actual_abbr,
                            actual_hosting
                        ))
                    return False
                elif name_hosting_abbr:  # If name suggests hosting but family isn't hosted
                    if show_log:
                        print("[{}]: Family is not hosted but name suggests {} hosting".format(
                            family_name,
                            name_hosting_abbr
                        ))
                    return False
                    
            return True
            
        except Exception as e:
            if show_log:
                print("[{}]: Error checking hosting method: {}".format(family_name, str(e)))
            return False

        
    @staticmethod
    def print_desired_mapping():
        """Prints the desired mapping of hosting methods to abbreviations"""
        output = OUTPUT.get_output()
        output.write("Desired Mapping of Hosting Methods to Abbreviations:", OUTPUT.Style.Title)
        output.write(["{} -> {}".format(k, v) for k, v in sorted(HostingMethodMapper.mapping.items())])
        output.plot()


    @staticmethod
    def analyze_hosting_behaviors(doc):
        """Analyze and display all unique family hosting behaviors in the document.
        
        Args:
            doc: Current Revit document
            
        Returns:
            dict: Mapping of hosting behaviors to lists of family names
        """
        output = OUTPUT.get_output()
        output.write("Analyzing Family Hosting Behaviors:", OUTPUT.Style.Title)
        
        hosting_dict = {}
        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
        
        for family in families:
            hosting_param = family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
            hosting_type = hosting_param.AsValueString() if hosting_param else "Not Hosted"
            
            if hosting_type not in hosting_dict:
                hosting_dict[hosting_type] = []
            hosting_dict[hosting_type].append(family.Name)
        
        for hosting_type, family_names in sorted(hosting_dict.items()):
            output.write("\n{} ({} families):".format(hosting_type, len(family_names)), OUTPUT.Style.SubTitle)
            output.write(sorted(family_names))
        
        output.plot()
        return hosting_dict

class CategoryMapper:
    """Maps Revit categories to standardized abbreviations.
    
    Features:
        - Maintains standard category abbreviations (e.g., DOOR, WIND)
        - Automatically adds TAG prefix for any tag-related categories
        - Validates family category against name prefix
    """
    
    def __init__(self, doc):
        self.doc = doc
        self.mapping = {
            "Casework": "CSWK",
            "Ceilings": "CLNG", 
            "Columns": "CLMN",
            "Curtain Panels": "CRTN",
            "Curtain Wall Mullions": "MULL",
            "Doors": "DOOR",
            "Electrical Equipment": "ELEC",
            "Electrical Fixtures": "ELFX",
            "Entourage": "ETRG",
            "Fire Alarm Devices": "FIRE",
            "Floors": "FLOR",
            "Furniture": "FURN",
            "Furniture Systems": "FSYS",
            "Generic Models": "GMOD",
            "Generic Annotation": "SYMBOL",
            "Lighting Fixtures": "LITE",
            "Mass": "MASS",
            "Mechanical Equipment": "MECH",
            "Nurse Call Devices": "NRSE",
            "Parking": "PARK",
            "Planting": "PLNT",
            "Plumbing": "PLBG",
            "Profile": "PRFL",
            "Railings": "RAIL",
            "Roads": "ROAD",
            "Roofs": "ROOF",
            "Security Devices": "SECU",
            "Site": "SITE",
            "Specialty Equipment": "SEQP",
            "Stairs": "STAIR", 
            "Structural Columns": "SCLM",
            "Structural Foundations": "FNDN",
            "Structural Framing": "STRX",
            "Walls": "WALL",
            "Windows": "WIND",
        }
        self._add_tag_categories()
    
    def _add_tag_categories(self):
        """Add TAG abbreviation for any category containing 'Tag'"""
        all_families = DB.FilteredElementCollector(self.doc).OfClass(DB.Family).ToElements()
        for family in all_families:
            if not family.FamilyCategory:
                continue
            category_name = family.FamilyCategory.Name
            if "Tag" in category_name and category_name not in self.mapping:
                self.mapping[category_name] = "TAG"
  
    
    @staticmethod
    def get_abbreviation(category_name):
        """Get abbreviation for a category name"""
        return CategoryMapper.mapping.get(category_name)

    @staticmethod
    def validate_category(family_or_family_name):
        """
        Validates if family category is supported and matches the name prefix
        Args:
            family: Revit family element
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if isinstance(family_or_family_name, DB.Family):
            family = family_or_family_name
        else:
            family = REVIT_FAMILY.get_family_by_name(family_or_family_name, REVIT_APPLICATION.get_doc())

        family_name = family.Name
        if not family.FamilyCategory:
            return False, "[{}]: Category is None, not supported.".format(family_name)
            
        family_category = family.FamilyCategory.Name
        abbreviation = CategoryMapper.get_abbreviation(family_category)
        if not abbreviation:
            return False, "[{}] category [{}] not supported.".format(family_name, family_category)

        actual_prefix = family_name.split("_")[0]
        if actual_prefix != abbreviation:
            return False, "[{}]: Category prefix should be [{}], found [{}]".format(
                family_name, abbreviation, actual_prefix)

        return True, ""

    @staticmethod
    def print_desired_mapping():

        """Prints the desired mapping of categories to abbreviations"""
        output = OUTPUT.get_output()
        output.write("Desired Mapping of Categories to Abbreviations:", OUTPUT.Style.Title)
        output.write(["{} -> {}".format(k, v) for k, v in sorted(CategoryMapper.mapping.items())])
        output.plot()

# Regex pattern components for family name validation
FAMILY_NAME_PATTERN = re.compile(
    r"^"                     # Start of string
    r"[A-Z]{2,4}"           # Category (2-4 uppercase letters)
    r"_"                     # Separator
    r"[A-Z][a-zA-Z0-9]+"    # Description (CamelCase)
    r"_"                     # Separator
    r"[A-Z]{2,4}"           # Intended Use (2-4 uppercase letters)
    r"(?:_[A-Z]{2,4})?"     # Optional Designator
    r"(?:_[A-Z]{2,4})?"     # Optional Hosting Method
    r"$"                     # End of string
)

def validate_name_pattern(family_name):
    """Validates if the family name matches the required pattern.
    
    Pattern: CATEGORY_Description_INTENDED[_DESIGNATOR][_HOSTING]
    
    Args:
        family_name (str): Name to validate
        
    Returns:
        tuple: (bool, str, match_object) 
            - bool: True if valid, False if invalid
            - str: Error message if invalid, empty string if valid
            - match_object: regex match object if valid, None if invalid
    """
    name_match = FAMILY_NAME_PATTERN.match(family_name)
    if not name_match:
        error_msg = "[{}]: Invalid format. Use: CATEGORY_Description_INTENDED[_DESIGNATOR][_HOSTING]".format(family_name)
        return False, error_msg, None
    return True, "", name_match

def check_family_name_format(family_or_family_name, show_log=False):
    """Validates if family name follows the naming convention"""
    if isinstance(family_or_family_name, DB.Family):
        family = family_or_family_name
        family_name = family.Name
        
        if not family.FamilyCategory:
            if show_log:
                print("[{}]: Category is None, not supported.".format(family_name))
            return False
            
        family_category_name = family.FamilyCategory.Name
        prefix = CategoryMapper.get_abbreviation(family_category_name)
        if not prefix:
            if show_log:
                print("[{}] category [{}] not supported.".format(family_name, family_category_name))
            return False
    
    elif isinstance(family_or_family_name, str):
        family_name = family_or_family_name
        
    # Validate name pattern
    is_valid, error_msg, name_match = validate_name_pattern(family_name)
    if not is_valid:
        if show_log:
            print(error_msg)
        return False

    if not CategoryMapper.validate_category(family_name):
        return False

    # Validate hosting method using the mapper
    if not HostingMethodMapper.validate_hosting_method(family, family_name, name_match, show_log):
        return False

    return True

def get_existing_family_names(doc):
    """Gets all existing family names in the document"""
    return set(f.Name for f in DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements())

class FamilyOption(forms.TemplateListItem):
    @property
    def name(self):
        category = self.item.FamilyCategory.Name if self.item.FamilyCategory else "No Category"
        return "[{}]     {}".format(category, self.item.Name)

def batch_rename_families(doc):
    """Interactive batch rename process for families.
    
    Provides multiple options for renaming:
    - Force prefix by script
    - Fix by keyword search
    - Fix by filling info
    - Analyze hosting behaviors
    """
    # Show naming rules at start
    show_naming_rules()

    options = [
        "Force prefix family name by script",
        "Fix by keyword",
        "Fix by filling info",
        "Analyze hosting behaviors",
        "Fix by Excel"
    ]
    
    selection = forms.SelectFromList.show(
        options, 
        title="Batch Fix Family Names"
    )
    
    if not selection:
        return
        
    actions = {
        options[0]: lambda: force_fix_family_name(doc),
        options[1]: lambda: fix_by_keyword(doc),
        options[2]: lambda: fix_by_filling_info(doc),
        options[3]: lambda: HostingMethodMapper.analyze_hosting_behaviors(doc),
        options[4]: lambda: fix_by_excel(doc)
    }
    
    actions[selection]()

def get_problematic_families(doc):
    """Get list of families with incorrect naming format.
    
    Args:
        doc: Current Revit document
        
    Returns:
        list: Families that don't match naming convention
    """
    return [
        f for f in DB.FilteredElementCollector(doc)
        .OfClass(DB.Family)
        .ToElements() 
        if not check_family_name_format(f, show_log=False)
    ]

def fix_by_excel(doc):
    """Fix family names by reading from Excel file."""
    options = {"Exporting Family Name":export_bad_family_name_to_excel,
               "Importing Family Name":import_family_name_from_excel}

    selection = forms.SelectFromList.show(
        options,
        title="Fix Family Names by Excel"
    )
    
    if not selection:
        return
    
    options[selection]()


def export_bad_family_name_to_excel(doc):
    """Export problematic family names to Excel file."""
    bad_families = forms.SelectFromList.show(
        [FamilyOption(f) for f in get_problematic_families(doc)],
        title="Select Families to Export",
        button_name="Export Families"
    )
    
    if not bad_families:
        return
    
    # Create Excel file
    excel_file = FOLDER.get_EA_dump_folder_file("FamilyRenameLittleHelper.xls")
    if not excel_file:
        return
    
    # Create Excel file
    data = []
    current_row = 0
    data.append(EXCEL.ExcelDataItem("Fill in forms below where ever make sense to you. Edited Row will be taken account.", current_row, 0))
    current_row += 1
    headers = ["Current Family Name", "Category Abbr", "Description", "Intended Use", "Designator(Optional)", "Hosting(Optional)"]
    for i, header in enumerate(headers):
        data.append(EXCEL.ExcelDataItem(header, current_row, i))
    current_row += 1
    for i, family in enumerate(bad_families):
        data.append(EXCEL.ExcelDataItem(family.Name, current_row, EXCEL.letter_to_index("A")))
        data.append(EXCEL.ExcelDataItem(CategoryMapper.get_abbreviation(family.FamilyCategory.Name), current_row, EXCEL.letter_to_index("B")))
        data.append(EXCEL.ExcelDataItem("---", current_row, EXCEL.letter_to_index("C")))
        data.append(EXCEL.ExcelDataItem("---", current_row, EXCEL.letter_to_index("D")))
        data.append(EXCEL.ExcelDataItem("", current_row, EXCEL.letter_to_index("E")))
        data.append(EXCEL.ExcelDataItem("", current_row, EXCEL.letter_to_index("F")))
        current_row += 1
    EXCEL.save_data_to_excel(data, excel_file)

    


def import_family_name_from_excel(doc):
    """Import family names from Excel file."""
    excel_file = FOLDER.get_EA_dump_folder_file("FamilyRenameLittleHelper.xls")
    if not excel_file:
        return
    
    data = EXCEL.read_data_from_excel(excel_file)

    # remove the first two rows
    data = data[2:]
    print(data)
    print ("-------------")


    t = DB.Transaction(doc, "Batch Fix Family Names")
    t.Start()
    for row in data:
        current_family_name = row[0]
        
        category_abbr = row[1]
        description = row[2]
        intended_use = row[3]

        # check if the description is empty
        if description == "---":
            continue
        # check if the intended use is empty
        if intended_use == "---":
            continue
        designator = row[4]
        hosting = row[5]
        user_defined_name = "{}_{}_{}".format(category_abbr, description, intended_use)
        if designator != "":
            user_defined_name = "{}_{}".format(user_defined_name, designator)
        if hosting != "":
            user_defined_name = "{}_{}".format(user_defined_name, hosting)
        
        if not check_family_name_format(user_defined_name, show_log=True):
            continue
        if user_defined_name != current_family_name:
            print("Renamed: {} -> {}".format(current_family_name, user_defined_name))
            # update the family name
            family = REVIT_FAMILY.get_family_by_name(current_family_name, doc)
            if family:
                family.Name = user_defined_name
    t.Commit()


def fix_by_filling_info(doc):
    """Fix family names by filling in missing information interactively."""
    category_mapper = CategoryMapper(doc)
    hosting_mapper = HostingMethodMapper()
    existing_names = get_existing_family_names(doc)
    
    while True:
        problematic_families = get_problematic_families(doc)
        
        if not problematic_families:
            NOTIFICATION.messenger("All family names are in correct format!")
            break
            
        # Select family to fix
        selected_family = forms.SelectFromList.show(
            [FamilyOption(f) for f in problematic_families],
            title="Select Family to Rename",
            button_name="Select Family"
        )
        
        if not selected_family:
            break
            
        # Get suggested values
        category = selected_family.FamilyCategory.Name if selected_family.FamilyCategory else ""
        suggested_prefix = category_mapper.get_abbreviation(category) or ""
        
        host_param = selected_family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
        host_method = host_param.AsValueString() if host_param else "Not Hosted"
        suggested_hosting = hosting_mapper.get_abbreviation(host_method) or ""
        
        # Get user inputs
        user_inputs = create_input_form(
            selected_family.Name,
            suggested_prefix,
            suggested_hosting
        )
        
        if not user_inputs:
            continue
            
        # Build new name
        new_name = build_family_name(user_inputs, existing_names)
        
        # Update family name
        try:
            with DB.Transaction(doc, "Rename Family") as t:
                t.Start()
                print("Renamed: {} -> {}".format(selected_family.Name, new_name))
                selected_family.Name = new_name
                existing_names.add(new_name)
                t.Commit()
        except Exception as e:
            print("Failed to rename {}: {}".format(selected_family.Name, str(e)))

def build_family_name(inputs, existing_names):
    """Build family name from components and ensure uniqueness.
    
    Args:
        inputs (dict): User input components
        existing_names (set): Existing family names
        
    Returns:
        str: Unique family name
    """
    name_parts = [
        inputs["Category"],
        inputs["Description"],
        inputs["Intended Use"]
    ]
    
    if inputs["Designator"]:
        name_parts.append(inputs["Designator"])
    if inputs["Hosting"]:
        name_parts.append(inputs["Hosting"])
        
    new_name = "_".join(filter(None, name_parts))
    
    # Ensure uniqueness
    while new_name in existing_names:
        new_name = "{}_conflict".format(new_name)
        
    return new_name

def force_fix_family_name(doc):
    """Force update family names with correct category prefix and hosting suffix.
    
    Args:
        doc: Current Revit document
        
    Returns:
        int: Number of families renamed
    """
    category_mapper = CategoryMapper(doc)
    hosting_mapper = HostingMethodMapper()
    
    # Get problematic families
    problematic_families = [f for f in DB.FilteredElementCollector(doc)
                          .OfClass(DB.Family)
                          .ToElements() 
                          if not check_family_name_format(f, doc, show_log=False)]
    
    if not problematic_families:
        NOTIFICATION.messenger("All family names are already in correct format!")
        return 0
        
    renamed_count = 0
    t = DB.Transaction(doc, "Batch Fix Family Names")
    t.Start()

    for family in problematic_families:
            # Skip families without category
            if not family.FamilyCategory:
                continue
                
            family_name = family.Name
            category = family.FamilyCategory.Name
            prefix_abbr = category_mapper.get_abbreviation(category)
            
            # Skip if no valid prefix found for category
            if not prefix_abbr:
                continue
                
            # Build new name
            name_parts = family_name.split('_')
            if name_parts[0] != prefix_abbr:
                new_name = "{}_{}".format(prefix_abbr, family_name)
            else:
                new_name = family_name
            
            # Add hosting suffix if needed
           
            host_param = family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
            if host_param:
                host_method = host_param.AsValueString()
                host_abbr = hosting_mapper.get_abbreviation(host_method)
                if host_abbr and not new_name.endswith(host_abbr):
                    new_name = "{}_{}".format(new_name, host_abbr)

            
            # Update name if changed
            if new_name != family_name:
                family.Name = new_name
                print("Renamed: {} -> {}".format(family_name, new_name))
                renamed_count += 1
                
    t.Commit()
    NOTIFICATION.messenger("Successfully renamed {} families".format(renamed_count))

            
    return renamed_count

def fix_by_keyword(doc):
    while True:
        output = OUTPUT.get_output()
        output.reset()
    
        CategoryMapper.print_desired_mapping()
        HostingMethodMapper.print_desired_mapping()

        
        problematic_families = [f for f in DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements() 
                              if not check_family_name_format(f, doc, show_log = False)]
        
        if not problematic_families:
            NOTIFICATION.messenger("All family names are in correct format!")
            break

        output.insert_divider()
        output.write("{} Problematic Families found:".format(len(problematic_families)), OUTPUT.Style.Title)
        output.write(["[{}] {}".format(f.FamilyCategory.Name, f.Name) for f in sorted(problematic_families, key=lambda x: (x.FamilyCategory.Name, x.Name))])
        output.plot()
            
        search_term = forms.ask_for_string(
            prompt="Enter search keyword to find families (or press Cancel to exit)",
            title="Batch Rename Families"
        )
        
        if not search_term:
            break
            
        matching_families = [f for f in problematic_families if search_term.lower() in f.Name.lower()]
        if not matching_families:
            NOTIFICATION.messenger("No families found containing '{}'".format(search_term))
            continue
            
        selected_families = forms.SelectFromList.show(
            [FamilyOption(f) for f in matching_families],
            title="Select Families to Rename",
            multiselect=True,
            button_name="Select Families"
        )
        
        if not selected_families:
            continue
            
        new_keyword = forms.ask_for_string(
            prompt="Enter the keyword to replace '{}' (or press Cancel to skip)".format(search_term),
            title="Enter New Keyword"
        )
        
        if not new_keyword:
            continue
            
        with DB.Transaction(doc, "Batch Rename Families replacing '{}' with '{}'".format(search_term, new_keyword)) as t:
            t.Start()
            existing_names = get_existing_family_names(doc)
            renamed_count = 0
            
            for family in selected_families:
                old_name = family.Name
                new_name = old_name.replace(search_term, new_keyword)
                
                while new_name in existing_names:
                    new_name = "{}_conflict".format(new_name)
                
                try:
                    family.Name = new_name
                    existing_names.add(new_name)
                    renamed_count += 1
                    print("Renamed: {} -> {}".format(old_name, new_name))
                except Exception as e:
                    print("Failed to rename {}: {}".format(old_name, str(e)))
                    
            t.Commit()
        
        NOTIFICATION.messenger("Renamed {} families".format(renamed_count))

def create_input_form(family_name, suggested_prefix, suggested_hosting):
    """Create sequential input prompts for family name components using pyrevit forms.
    
    Args:
        family_name (str): Current family name
        suggested_prefix (str): Suggested category prefix
        suggested_hosting (str): Suggested hosting suffix
        
    Returns:
        dict: Dictionary of user inputs or None if cancelled
    """
    print("Current Family Name: {}".format(family_name))
    
    inputs = {}
    prompts = [
        ("Category", suggested_prefix, "Enter category abbr or CSI Div No."),
        ("Description", "", "Enter Itemdescription in CamelCase (e.g., SingleFlush)"),
        ("Intended Use", "", "Enter intended use, firmwide abbr, practive area abbr, office abbr or client abbr (e.g., PE for Production)"),
        ("Designator", "", "Enter designator if applicable (e.g., GEN, EXT), generic item, model designator, attanla number, CSI masterformat or press Enter to skip"),
        ("Hosting", suggested_hosting, "Enter hosting method if applicable (e.g., WH) or press Enter to skip")
    ]
    
    for key, default, prompt in prompts:
        value = forms.ask_for_string(
            default=default,
            prompt=prompt,
            title=key
        )
        
        if value is None:  # User pressed Cancel
            return None
            
        inputs[key] = value.strip()
    
    return inputs

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main(doc):
    """Main entry point for the script"""

    batch_rename_families(doc)

if __name__ == "__main__":
    main(DOC)







