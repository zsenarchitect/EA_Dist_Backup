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

    output = OUTPUT.get_output()
    output.write(image_path)

    HostingMethodMapper.print_desired_mapping()
    CategoryMapper.print_desired_mapping()
    output.plot()


class BaseMapper:
    """Base class for mapping and validation functionality."""
    
    mapping = {}  # To be overridden by child classes
    
    @classmethod
    def get_abbreviation(cls, key):
        """Get abbreviation for a given key."""
        return cls.mapping.get(key, "not defined AHHHHHHH ASK Sen for help!!!!!! He is a idiot.  " + key)
    
    @classmethod
    def print_desired_mapping(cls):
        """Prints the desired mapping to abbreviations."""
        output = OUTPUT.get_output()
        output.write("Desired Mapping for {}:".format(cls.__name__), OUTPUT.Style.Title)
        output.write(["{} -> {}".format(k, v) for k, v in sorted(cls.mapping.items())])
        output.plot()


class HostingMethodMapper(BaseMapper):
    """Maps and validates family hosting methods.
    
    Features:
        - Maps standard hosting methods to abbreviations
        - Validates family hosting against name suffix
        - Analyzes document-wide hosting behaviors
    """
    
    mapping = {
        "Wall": "WA",
        "Ceiling": "CE",
        "Floor": "FL",
        "Face": "FC",
        
        # Non-hosted cases
        "Not Hosted": None,
        "Invalid": None,
        "": None,
       
    }


    @staticmethod
    def get_hosting_abbreviation(family):
        """Get hosting method from family."""
        hosting_param = family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
        if not hosting_param:
            return None
        return HostingMethodMapper.get_abbreviation(hosting_param.AsValueString())

    
    @staticmethod
    def validate_hosting_method(family, show_log = False):
        """
        Validates if the family's hosting method matches its name
        Args:
            family: Revit family element
            family_name (str): Name of the family
            name_match: Regex match object from family name pattern
        Returns:
            bool: True if hosting method is valid, False otherwise
        """
        # Get actual hosting method from family

        actual_abbr = HostingMethodMapper.get_hosting_abbreviation(family)
        if not actual_abbr:
            return True # ok to be not hosting
        
        # Get hosting method from name (last group in regex)
        name_match = FAMILY_NAME_PATTERN.match(family.Name)
        if not name_match:
            return True  # Skip validation if name doesn't match pattern, becasue it is ok to not have hosting abbreviation in the name
            
        groups = name_match.groups()
        name_hosting_abbr = groups[-1][1:] if groups[-1] else None  # Remove leading underscore if exists
        
        # Compare actual vs name-specified hosting
        if actual_abbr != name_hosting_abbr:
            # Only flag as error if:
            # 1. Family is hosted but name doesn't include correct hosting suffix
            # 2. Name includes hosting suffix but family isn't actually hosted
            if actual_abbr and show_log:  # Case 1
                print("[{}]: Hosting method mismatch - Name: {}, Actual: {} ({})".format(
                    family.Name,
                    name_hosting_abbr or "None",
                    actual_abbr,
                    family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR].AsValueString()
                ))
                return False
            elif name_hosting_abbr and show_log:  # Case 2
                print("[{}]: Family is not hosted but name suggests {} hosting".format(
                    family.Name,
                    name_hosting_abbr
                ))
                return False
                
        return True
        
    @classmethod
    def analyze_hosting_behaviors(cls):
        """Analyze hosting behaviors of families in the document."""
        doc = REVIT_APPLICATION.get_doc()
        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
        
        output = OUTPUT.get_output()
        output.write("Analyzing Family Hosting Behaviors:", OUTPUT.Style.Title)
        
        # Create dictionary to group families by hosting type
        hosting_groups = {}
        
        for family in families:
            if not family.FamilyCategory:
                continue
                
            hosting_param = family.Parameter[DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR]
            if not hosting_param:
                continue
                
            actual_hosting = hosting_param.AsValueString()
            actual_abbr = cls.get_abbreviation(actual_hosting)
            
            # Group by hosting abbreviation
            group_key = actual_hosting if actual_abbr else "Non-Hosted"
            if group_key not in hosting_groups:
                hosting_groups[group_key] = []
            
            hosting_groups[group_key].append(family.Name)
        
        # Output groups with subtitles
        for abbr, families in sorted(hosting_groups.items()):
            output.write("\n{} Families ({}):".format(
                abbr if abbr != "Non-Hosted" else "Non-Hosted",
                len(families)
            ), OUTPUT.Style.SubTitle)
            output.write(sorted(families))
            
        output.plot()


class CategoryMapper(BaseMapper):
    """Maps Revit categories to standardized abbreviations.
    
    Features:
        - Maintains standard category abbreviations (e.g., DOOR, WIND)
        - Automatically adds TAG prefix for any tag-related categories
        - Validates family category against name prefix
    """
    
    mapping = {
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

    @classmethod
    def add_tag_categories(cls):
        """Add TAG abbreviation for any category containing 'Tag'"""
        doc = REVIT_APPLICATION.get_doc()
        all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
        for family in all_families:
            if not family.FamilyCategory:
                continue
            category_name = family.FamilyCategory.Name
            if "Tag" in category_name and category_name not in cls.mapping:
                cls.mapping[category_name] = "TAG"

    @staticmethod
    def validate_category(family, show_log=False):
        """Validates if family category is supported and matches the name prefix"""
        family_name = family.Name
        if not family.FamilyCategory:
            if show_log:
                print("[{}]: Category is None, not supported.".format(family_name))
            return False
            
        family_category = family.FamilyCategory.Name
        abbreviation = CategoryMapper.get_abbreviation(family_category)
        if not abbreviation:
            if show_log:
                print("[{}] category [{}] not supported.".format(family_name, family_category))
            return False

        actual_prefix = family_name.split("_")[0]
        if actual_prefix != abbreviation:
            if show_log:
                print("[{}]: Category prefix should be [{}], found [{}]".format(
                    family_name, abbreviation, actual_prefix))
            return False

        return True

# Initialize CategoryMapper by calling class method after class definition
CategoryMapper.add_tag_categories()

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



def check_family_name_format(family, show_log=False):
    """Validates if family name follows the naming convention"""

    if not CategoryMapper.validate_category(family, show_log):
        return False
    # Validate hosting method using the mapper
    if not HostingMethodMapper.validate_hosting_method(family, show_log):
        return False

    return True

def get_existing_family_names(doc):
    """Gets all existing family names in the document"""
    return set(f.Name for f in DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements())

class FamilyOption(forms.TemplateListItem):
    @property
    def name(self):
        category = self.item.FamilyCategory.Name if self.item.FamilyCategory else "No Category"
        return "[{}]   {}".format(category, self.item.Name)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_rename_families():
    """Interactive batch rename process for families."""

    options = [
        "Analyze hosting behaviors",
        "Show Naming Rules",
        "Fix by Excel"
    ]
    
    selection = forms.SelectFromList.show(
        options, 
        title="Batch Fix Family Names"
    )
    
    if not selection:
        return
        
    actions = {
        options[0]: HostingMethodMapper.analyze_hosting_behaviors,
        options[1]: show_naming_rules,
        options[2]: fix_by_excel
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

def fix_by_excel():
    """Fix family names by reading from Excel file."""
    options = {"1_Exporting Family Name":export_bad_family_name_to_excel,
               "2_Importing Family Name":import_family_name_from_excel}

    selection = forms.SelectFromList.show(
        sorted(options.keys()),
        title="Fix Family Names by Excel"
    )
    
    if not selection:
        return
    
    options[selection]()


def export_bad_family_name_to_excel():
    """Export problematic family names to Excel file."""
    doc = REVIT_APPLICATION.get_doc()
    bad_families = forms.SelectFromList.show(
        [FamilyOption(f) for f in get_problematic_families(doc)],
        title="Select Families to Export",
        multiselect=True,
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
        data.append(EXCEL.ExcelDataItem(header, current_row, i, border_style=6, cell_color=(200, 200, 200)))
    current_row += 1
    for i, family in enumerate(bad_families):
        data.append(EXCEL.ExcelDataItem(family.Name, current_row, "A"))
        data.append(EXCEL.ExcelDataItem(CategoryMapper.get_abbreviation(family.FamilyCategory.Name), current_row, "B"))
        data.append(EXCEL.ExcelDataItem("---", current_row, "C"))
        data.append(EXCEL.ExcelDataItem("---", current_row, "D"))
        data.append(EXCEL.ExcelDataItem(None, current_row, "E"))
        data.append(EXCEL.ExcelDataItem(HostingMethodMapper.get_hosting_abbreviation(family), current_row, "F"))
        current_row += 1
    EXCEL.save_data_to_excel(data, excel_file, freeze_row=2)

    


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
        if designator:
            user_defined_name = "{}_{}".format(user_defined_name, designator)
        if hosting:
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





if __name__ == "__main__":
    batch_rename_families()







