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
from EnneadTab import ERROR_HANDLE, LOG, UI, NOTIFICATION, OUTPUT, FOLDER, EXCEL, COLOR
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
    output.write("HealthCare Family Naming Rules:", OUTPUT.Style.Title)
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
        "Wall": "WH",
        "Ceiling": "CH",
        "Floor": "FH",
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
        # print ("family.Name", family.Name)
        # print ("name_match", name_match)
        # print ("groups", groups)
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
        
        # Output groups with subTitles - hosted families first, then non-hosted
        # Get all groups except "Non-Hosted"
        hosted_groups = {k: v for k, v in hosting_groups.items() if k != "Non-Hosted"}
        
        # Print hosted families first
        for abbr, families in sorted(hosted_groups.items()):
            output.write("\n{} Hosted Families ({}):".format(
                abbr,
                len(families)
            ), OUTPUT.Style.Subtitle)
            output.write(sorted(families))
        
        # Print non-hosted families last
        if "Non-Hosted" in hosting_groups:
            output.write("\nNon-Hosted Families ({}):".format(
                len(hosting_groups["Non-Hosted"])
            ), OUTPUT.Style.Subtitle)
            output.write(sorted(hosting_groups["Non-Hosted"]))
            
        output.plot()


class CategoryMapper(BaseMapper):
    """Maps Revit categories to standardized abbreviations."""
    
    mapping = {
        # Architectural Core Elements
        "Walls": "WALL",
        "Floors": "FLOR",
        "Ceilings": "CLNG", 
        "Roofs": "ROOF",
        "Doors": "DOOR",
        "Windows": "WIND",
        
        # Architectural Circulation
        "Stairs": "STAIR", 
        "Ramps": "RAMP",
        "Railings": "RAIL",
        "Balusters": "BLST",
        
        # Structural Elements
        "Columns": "CLMN",
        "Structural Columns": "SCLM",
        "Structural Foundations": "FNDN",
        "Structural Framing": "STRX",
        "Structural Connections": "SCON",
        "Structural Rebar": "RBAR",
        "Structural Stiffeners": "STIF",
        "Structural Tendons": "TEND",
        "Structural Trusses": "TRUS",
        
        # Bridge Components
        "Abutments": "ABUT",
        "Bearings": "BEAR",
        "Bridge Cables": "BCBL",
        "Bridge Decks": "BDCK",
        "Piers": "PIER",
        
        # Interior Elements
        "Casework": "CSWK",
        "Furniture": "FURN",
        "Furniture Systems": "FSYS",
        "Spaces": "SPCE",
        "Supports": "SUPP",
        
        # Equipment
        "Food Service Equipment": "FOOD",
        "Medical Equipment": "MEQP",
        "Specialty Equipment": "SEQP",
        "Nurse Call Devices": "NRSE",
        
        # MEP - Electrical
        "Electrical Equipment": "ELEC",
        "Electrical Fixtures": "ELFX",
        "Lighting Fixtures": "LITE",
        "Lighting Devices": "LDEV",
        "Security Devices": "SECU",
        "Communication Devices": "COMM",
        "Data Devices": "DATA",
        "Audio Visual Devices": "AVDV",
        "Fire Alarm Devices": "FIRE",
        "Wires": "WIRE",
        
        # MEP - Mechanical
        "Air Terminals": "ATRM",
        "Duct Accessories": "DACC",
        "Duct Fittings": "DFIT",
        "Duct Insulations": "DINS",
        "Duct Linings": "DLIN",
        "Ducts": "DUCT",
        "Mechanical Equipment": "MECH",
        "Mechanical Control Devices": "MCTL",
        "Zone Equipment": "ZEQP",
        
        # MEP - Plumbing
        "Plumbing": "PLBG",
        "Plumbing Equipment": "PEQP",
        "Plumbing Fixtures": "PFIX",
        "Pipe Accessories": "PACC",
        "Pipe Fittings": "PFIT",
        "Pipe Insulations": "PINS",
        "Pipes": "PIPE",
        "Sprinklers": "SPNK",
        
        # Distribution Systems
        "Cable Trays": "CTRY",
        "Conduits": "COND",
        "Curtain Panels": "CRTN",
        "Curtain Systems": "CSYS",
        "Curtain Wall Mullions": "MULL",
        
        # Site and Exterior
        "Entourage": "ETRG",
        "Hardscape": "HARD",
        "Parking": "PARK",
        "Planting": "PLNT",
        "Roads": "ROAD",
        "Site": "SITE",
        
        # Annotation Elements
        "Callout Heads": "CALL",
        "Detail Items": "DETL",
        "Elevation Marks": "ELEV",
        "Generic Annotations": "ANNO",
        "Generic Models": "GMOD",
        "Generic Annotation": "SYMBOL",
        "Grid Heads": "GRID",
        "Level Heads": "LEVL",
        "Section Marks": "SECT",
        "Span Direction Symbol": "SPAN",
        "Spot Elevation Symbols": "SPOT",
        "Title Blocks": "TITL",
        "View Reference": "VREF",
        "View Titles": "VTIT",
        
        # Special Elements
        "Expansion Joints": "EXPJ",
        "Mass": "MASS",
        "Parts": "PART",
        "Profiles": "PRFL",
        "Signage": "SIGN",
        "Temporary Structures": "TEMP",
        "Vibration Management": "VIBR",
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

    @staticmethod
    def analyze_category_map():
        """Analyze and display category mapping status based on document families."""
        output = OUTPUT.get_output()
        output.write("Category Mapping Analysis:", OUTPUT.Style.Title)
        
        # Group categories
        registered_categories = {}  # Dict to store category counts
        unregistered_categories = {}
        
        all_families = DB.FilteredElementCollector(REVIT_APPLICATION.get_doc()).OfClass(DB.Family).ToElements()
        for family in all_families:
            if not family.FamilyCategory:
                continue
                
            category_name = family.FamilyCategory.Name
            
            # Skip if category name contains "Tag"
            if "Tag" in category_name:
                continue
                
            if category_name in CategoryMapper.mapping:
                registered_categories[category_name] = registered_categories.get(category_name, 0) + 1
            else:
                unregistered_categories[category_name] = unregistered_categories.get(category_name, 0) + 1
        
        # Output registered categories
        output.write("\nRegistered Categories ({}):".format(len(registered_categories)), 
                    OUTPUT.Style.Subtitle)
        for category_name in sorted(registered_categories.keys()):
            output.write("    {} -> {} ({} families)".format(
                category_name, 
                CategoryMapper.mapping[category_name],
                registered_categories[category_name]
            ))
            
        # Output unregistered categories
        output.write("\nUnregistered Categories ({}):".format(len(unregistered_categories)), 
                    OUTPUT.Style.Subtitle)
        for category_name in sorted(unregistered_categories.keys()):
            output.write("    {} ({} families)".format(
                category_name,
                unregistered_categories[category_name]
            ))
            
        output.plot()

# Initialize CategoryMapper by calling class method after class definition
CategoryMapper.add_tag_categories()

# Regex pattern components for family name validation
FAMILY_NAME_PATTERN = re.compile(
    r"^"                     # Start of string
    r"([A-Z]{2,6})"         # Required: Category (2-6 uppercase letters)
    r"_"                     # Required: Separator
    r"([A-Z][a-zA-Z0-9]+)"  # Required: Description (CamelCase)
    r"_"                     # Required: Separator
    r"([A-Z]+)"             # Required: Intended Use (uppercase letters)
    r"(?:_([^_]+))?"        # Optional: Any non-empty characters after underscore
    r"(?:_([A-Z]{2}))?"     # Optional: Exactly 2 uppercase letters after underscore
    r"$"                     # End of string
)



def check_family_name_format(family, show_log=False):
    """Validates if family name follows the naming convention"""
    family_name = family.Name
    
    # Debug output for problematic names
    if show_log:
        match = FAMILY_NAME_PATTERN.match(family_name)
        if match:
            print("Groups found:", match.groups())
        else:
            print("No match for:", family_name)
            
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
        "Analyze category map",
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
        options[1]: CategoryMapper.analyze_category_map,
        options[2]: show_naming_rules,
        options[3]: fix_by_excel
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
    options = {"1_Exporting Family Name First":export_bad_family_name_to_excel,
               "2_Transfer Edited Family Names":import_family_name_from_excel}

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
        sorted([FamilyOption(f) for f in get_problematic_families(doc)], key=lambda x: x.name),
        title="Select Families to Export",
        multiselect=True,
        button_name="Export Families"
    )
    
    if not bad_families:
        return
    

    excel_file = FOLDER.get_EA_dump_folder_file("FamilyRenameLittleHelper.xlsx")


    cate_color_dict = {}
    # Create Excel file
    data = []
    current_row = 0
    headers = ["Current Family Name", 
               "Category Abbr/CSI Div No.", 
               "ItemDescription/ItemSubfields(CamelCase)", 
               "Intended Use/Practive Area/Office abbr/Client abbr", 
               "(Optional)Model Designator/Attanla Num/CSI Master format", 
               "Hosting Method"]
    for i, header in enumerate(headers):
        data.append(EXCEL.ExcelDataItem(header, current_row, i, border_style=6, cell_color=(200, 200, 200)))
    
    current_row += 1

    for i, family in enumerate(bad_families):
        is_row_highlighted = i%2 == 0

        
        cate_abbr = CategoryMapper.get_abbreviation(family.FamilyCategory.Name)
        if cate_abbr not in cate_color_dict:
            cate_color_dict[cate_abbr] = COLOR.get_random_color()
            
        cell_color = cate_color_dict[cate_abbr]
        top_border_style = 1
        side_border_style = 1
        if is_row_highlighted:
            cell_color = COLOR.lighten_color(cell_color, 0.5)


     
        data.append(EXCEL.ExcelDataItem(family.Name, current_row, "A", cell_color=cell_color, border_style=2))
        data.append(EXCEL.ExcelDataItem(cate_abbr, current_row, "B", cell_color=cell_color, top_border_style=top_border_style, side_border_style=side_border_style))
        data.append(EXCEL.ExcelDataItem("---", current_row, "C", cell_color=cell_color, top_border_style=top_border_style, side_border_style=side_border_style))
        data.append(EXCEL.ExcelDataItem("---", current_row, "D", cell_color=cell_color, top_border_style=top_border_style, side_border_style=side_border_style))
        data.append(EXCEL.ExcelDataItem(None, current_row, "E", cell_color=cell_color, top_border_style=top_border_style, side_border_style=side_border_style))
        data.append(EXCEL.ExcelDataItem(HostingMethodMapper.get_hosting_abbreviation(family), current_row, "F", cell_color=cell_color, top_border_style=top_border_style, side_border_style=side_border_style))
        current_row += 1
  
       
    EXCEL.save_data_to_excel(data, excel_file, worksheet="FamilyRenameLittleHelper", freeze_row=1)


    show_naming_rules()
    


def import_family_name_from_excel():
    """Import family names from Excel file."""
    excel_file = FOLDER.get_EA_dump_folder_file("FamilyRenameLittleHelper.xlsx")
    if not excel_file:
        return
    
    data = EXCEL.read_data_from_excel(excel_file, worksheet="FamilyRenameLittleHelper")

    output = OUTPUT.get_output()
    # remove the header row
    data = data[1:]

    doc = REVIT_APPLICATION.get_doc()
    t = DB.Transaction(doc, "Batch Fix Family Names")
    t.Start()
    log  = []
    for row in data:
        current_family_name = row[0].get("value")
        
        category_abbr = row[1].get("value")
        description = row[2].get("value")
        intended_use = row[3].get("value")

        # check if the description is unedited
        if description == "---":
            continue
        # check if the intended use is unedited
        if intended_use == "---":
            continue
        designator = row[4].get("value")
        hosting = row[5].get("value")
        user_defined_name = "{}_{}_{}".format(category_abbr, description, intended_use)
        if designator:
            user_defined_name = "{}_{}".format(user_defined_name, designator)
        if hosting:
            user_defined_name = "{}_{}".format(user_defined_name, hosting)
        
        while not is_family_name_unique(user_defined_name):
            # print ("[{}] is not unique, adding conflect marker".format(user_defined_name))
            user_defined_name = "{}*ConflictingName".format(user_defined_name)
        if user_defined_name != current_family_name:
            # update the family name
            family = REVIT_FAMILY.get_family_by_name(current_family_name, doc)
            if family:
                try:
                    family.Name = user_defined_name
                    log.append("{} ---> {}".format(current_family_name, user_defined_name))
                    doc.Regenerate() # this is needed to refresh the doc family pool
                except Exception as e:
                    log.append("Failed to rename {} to {}. Error: {}".format(current_family_name, user_defined_name, e))

    if len(log) > 0:
        output.write("{} Family Renamed:".format(len(log)), OUTPUT.Style.Subtitle)
        output.write(log)
        output.plot()
    t.Commit()

def is_family_name_unique(family_name):
    doc = REVIT_APPLICATION.get_doc()
    return family_name not in set(f.Name for f in DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements())




if __name__ == "__main__":
    batch_rename_families()







