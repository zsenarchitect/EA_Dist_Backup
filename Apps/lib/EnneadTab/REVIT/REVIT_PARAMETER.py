"""
Helper functions for managing Revit parameters.

Provides utilities for:
- Creating and managing shared parameters
- Adding parameters to family and project documents
- Parameter binding and verification
- Parameter value retrieval and modification
"""

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import NOTIFICATION
import SAMPLE_FILE
import DATA_FILE
import FOLDER
import ENVIRONMENT
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    import REVIT_UNIT
except:
    pass


def get_project_info_para_by_name(doc, para_name):
    """Retrieve a parameter from project information by its name.
    
    Args:
        doc: Current Revit document
        para_name: Name of the parameter to find
        
    Returns:
        Parameter: Found parameter object or None if not found
    """
    proj_info = doc.ProjectInformation
    for para in proj_info.Parameters:
        if para.Definition.Name == para_name:
            return para
    return None

def create_shared_parameter_in_txt_file(doc,
                            para_name,
                            para_type,
                            para_group_name = "EnneadTab"):
    """Creates a new shared parameter definition in the shared parameter file.

    Args:
        doc (Document): Active Revit document
        para_name (str): Name of the parameter to create
        para_type (SpecTypeId): Parameter data type (e.g., DB.SpecTypeId.Boolean.YesNo)
        para_group_name (str, optional): Group name in shared parameter file. Defaults to "EnneadTab"

    Returns:
        ExternalDefinition: The created parameter definition
    """
    # make a dict about para_type lookup? or maybe REVIT_UNIT has something already?
    
    option = DB.ExternalDefinitionCreationOptions (para_name, para_type)
    definition_group = get_shared_para_group_by_name_in_txt_file(doc,para_group_name,create_if_not_exist=True)
        
    definition = definition_group.Definitions.Create(option)
    
    return definition

    
def get_shared_para_group_by_name_in_txt_file(doc, 
                                   para_group_name,
                                   create_if_not_exist=False):
    """Retrieves or creates a parameter group in the shared parameter file.

    Args:
        doc (Document): Active Revit document
        para_group_name (str): Name of the parameter group to find/create
        create_if_not_exist (bool): Create group if not found. Defaults to False

    Returns:
        DefinitionGroup: The parameter group, or None if not found and not created
    """
    for definition_group in doc.Application.OpenSharedParameterFile().Groups:
        if definition_group.Name == para_group_name:
            return definition_group
    
    if create_if_not_exist:
        return doc.Application.OpenSharedParameterFile().Groups.Create(para_group_name)
    
    
    
    NOTIFICATION.messenger(main_text="Cannot find [{}] in shared parameter file.\nIs this loaded correctly?".format(para_group_name))
    return None

def get_shared_para_definition_in_txt_file_by_name(doc, 
                                       para_name):
    """Retrieves a shared parameter definition by name.

    Args:
        doc (Document): Active Revit document
        para_name (str): Name of the parameter to find

    Returns:
        ExternalDefinition: The parameter definition, or None if not found
        
    Note:
        Will attempt to use default EnneadTab shared parameter file if none is loaded
    """
    shared_para_file = doc.Application.OpenSharedParameterFile()
    if not shared_para_file:
  
        NOTIFICATION.messenger(main_text='[{}]\nneed to have a valid shared parameter file. \nI am going to use default EnneadTab shared parameter file.\nBut you nned to save it to a better place.'.format(doc.Title))
        filepath = SAMPLE_FILE.get_file("DefaultSharedParameter.txt")
        doc.Application.SharedParametersFilename = filepath
        
        shared_para_file = doc.Application.OpenSharedParameterFile()

    for definition_group in shared_para_file.Groups:
        for definition in definition_group.Definitions:
            if definition.Name == para_name:
                return definition



    NOTIFICATION.messenger(main_text="Cannot find [{}] in shared parameter file.\nIs this loaded correctly?".format(para_name))
    
    
    return None


def add_parameter_to_family_doc(family_doc, 
                                para_name, 
                                para_group,
                                default_value, 
                                is_instance_parameter = False):
    """Adds a parameter to a family document.

    Args:
        family_doc (Document): The family document
        para_name (str): Name of the parameter to add
        para_group (str): Parameter group ("Data" or "Set")
        default_value (varies): Default parameter value
        is_instance_parameter (bool): True for instance parameter. Defaults to False
    """
    pass

def add_shared_parameter_to_project_doc(project_doc,
                                 para_definition,
                                 para_group,
                                 binding_cates,
                                 is_instance_parameter = True):
    """Adds a shared parameter to the project document with specified bindings.

    Args:
        project_doc (Document): Active Revit project document
        para_definition (ExternalDefinition): Parameter definition to add
        para_group (str): Parameter group ("Data" or "Set")
        binding_cates (list): List of Revit categories to bind the parameter to
        is_instance_parameter (bool): True for instance parameter. Defaults to True

    Returns:
        bool: True if parameter was added successfully
    """
    # create new shared para to avoid adding same definiation twice
    try:
        DB.SharedParameterElement.Create(project_doc, para_definition)
    except Exception as e:
        print ("cannot add [{}] to doc [{}] becasue {}".format(para_definition.Name, project_doc.Title, e))

        return False
    
    cate_sets = DB.CategorySet()
    for cate in binding_cates:
        cate_sets.Insert(cate)

    binding = DB.InstanceBinding() if is_instance_parameter else DB.TypeBinding()
    binding.Categories = cate_sets
    project_doc.ParameterBindings.Insert(para_definition, binding, get_para_group(para_group))
    return True


def get_para_group(group_name = "Data"):
    """Gets the built-in parameter group by name.

    Args:
        group_name (str): Name of the parameter group ("Data" or "Set")

    Returns:
        GroupTypeId: Built-in parameter group identifier
    """
    return getattr(DB.GroupTypeId, group_name)

def get_parameter_by_name(doc, 
                          para_name):
    """Retrieves a parameter by name from document or family manager.

    Args:
        doc (Document): The Revit document to query
        para_name (str): Name of the parameter to find

    Returns:
        Parameter: The matching parameter, or None if not found
    """
    if hasattr(doc, "FamilyManager"):
        for para in doc.FamilyManager.Parameters:
            if para.Definition.Name == para_name:
                return para
    else:
        for para in doc.Parameters:
            if para.Definition.Name == para_name:
                return para
    return None

def confirm_shared_para_exist_on_category(doc, para_name, category, para_type = DB.SpecTypeId.String.Text):
    """Verifies or creates a shared parameter for a specific category.

    Args:
        doc (Document): Active Revit document
        para_name (str): Name of the parameter to verify/create
        category (BuiltInCategory): Category to check/add parameter to (e.g., OST_Areas, OST_Parking)
        para_type (SpecTypeId, optional): Parameter data type. Defaults to Text.

    Returns:
        bool: True if parameter exists or was created successfully
    
    Note:
        For project information parameters, use get_project_info_para_by_name() instead
    """
    sample_element = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().FirstElement()
    if not sample_element:
        print ("no sample element found on category [{}]. Please have at least one element on this category.".format(category))
        return False
    para = sample_element.LookupParameter(para_name)
    if para:
        return True

    definition = get_shared_para_definition_in_txt_file_by_name(doc, para_name)
    if not definition:
        definition = create_shared_parameter_in_txt_file(doc, para_name, para_type)
    add_shared_parameter_to_project_doc(doc, definition, "Data", [DB.Category.GetCategory(doc, category)])
    return True

def __override_L_drive_shared_para_file_to_OS_shared_para_file():
    L_drive_shared_para_file = os.path.join(ENVIRONMENT.L_DRIVE_HOST_FOLDER, "01_Revit", "03_Library", "EA_SharedParam.txt")
    OS_shared_para_file = "Apps\\lib\\EnneadTab\\documents\\revit\\DefaultSharedParameter.txt"
    

    # copy L to override OS
    import shutil
    shutil.copy(L_drive_shared_para_file, OS_shared_para_file)



def get_parameter_group(para_group = "General"):
    """_summary_

    Args:
        para_group (_type_): General, Data, AdskModelProperties

    Returns:
        _type_: _description_
    """
    print ("DEPRECIATED func")
    try:
        para_group = getattr(DB.BuiltInParameterGroup, "PG_{}".format(para_group.upper()))
    except:
        para_group = getattr(DB.GroupTypeId, para_group.title())

    return para_group


def get_parameter_type(para_type = "YesNo"):
    """_summary_

    Args:
        para_type (_type_): YesNo, Length, Text

    Returns:
        _type_: _description_
    """
    try:
        
        parameter_type = getattr(DB.ParameterType, para_type)
        
    except:
        
        parameter_type = REVIT_UNIT.lookup_unit_spec_id(para_type.lower())
    return parameter_type


def get_parameter_type_from_string(para_type_str):
    """Convert string parameter type to DB.SpecTypeId using fuzzy text matching
    
    Args:
        para_type_str (str): Parameter type as string (e.g., "Text", "YesNo", "Number", "Length", "Integer", "MultilineText")
    
    Returns:
        SpecTypeId: Revit parameter type
    """
    from EnneadTab import TEXT
    
    para_type_mapping = {
        # Text parameter types
        "text": DB.SpecTypeId.String.Text,
        "string": DB.SpecTypeId.String.Text,
        "multilinetext": DB.SpecTypeId.String.MultilineText,
        "multiline text": DB.SpecTypeId.String.MultilineText,
        "multiline_text": DB.SpecTypeId.String.MultilineText,
        "multitext": DB.SpecTypeId.String.MultilineText,
        "multi text": DB.SpecTypeId.String.MultilineText,
        
        # Boolean parameter types
        "yesno": DB.SpecTypeId.Boolean.YesNo,
        "yes no": DB.SpecTypeId.Boolean.YesNo,
        "yes_no": DB.SpecTypeId.Boolean.YesNo,
        "boolean": DB.SpecTypeId.Boolean.YesNo,
        "bool": DB.SpecTypeId.Boolean.YesNo,
        "true false": DB.SpecTypeId.Boolean.YesNo,
        "truefalse": DB.SpecTypeId.Boolean.YesNo,
        
        # Numeric parameter types
        "number": DB.SpecTypeId.Number,
        "numeric": DB.SpecTypeId.Number,
        "decimal": DB.SpecTypeId.Number,
        "float": DB.SpecTypeId.Number,
        "double": DB.SpecTypeId.Number,
        
        # Integer parameter types
        "integer": DB.SpecTypeId.Int.Integer,
        "int": DB.SpecTypeId.Int.Integer,
        "whole number": DB.SpecTypeId.Int.Integer,
        "wholenumber": DB.SpecTypeId.Int.Integer,
        
        # Length and dimensional types
        "length": DB.SpecTypeId.Length,
        "distance": DB.SpecTypeId.Length,
        "dimension": DB.SpecTypeId.Length,
        "area": DB.SpecTypeId.Area,
        "volume": DB.SpecTypeId.Volume,
        "angle": DB.SpecTypeId.Angle,
    }
    
    # First try exact match (case-insensitive)
    para_type_lower = para_type_str.lower().strip()
    
    if para_type_lower in para_type_mapping:
        return para_type_mapping[para_type_lower]
    
    # Use TEXT.fuzzy_search for fuzzy matching
    possible_types = list(para_type_mapping.keys())
    
    try:
        best_match = TEXT.fuzzy_search(para_type_lower, possible_types)
        
        if best_match:
            print("Fuzzy matched '{}' to '{}'".format(para_type_str, best_match))
            return para_type_mapping[best_match]
    except Exception as e:
        print("Error in fuzzy search: {}".format(e))
    
    # If still no match, default to Text but warn user
    print("Warning: Could not match parameter type '{}' to any known type. Defaulting to Text.".format(para_type_str))
    return DB.SpecTypeId.String.Text


if __name__ == "__main__":
    __override_L_drive_shared_para_file_to_OS_shared_para_file()