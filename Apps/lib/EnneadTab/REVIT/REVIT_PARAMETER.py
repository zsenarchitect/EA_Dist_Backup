"""
Helper functions for managing Revit parameters.
Provides utilities for:
- Creating and managing shared parameters
- Adding parameters to family and project documents
- Parameter binding and verification
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
    from pyrevit import forms
except:
    pass




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
    
    for definition_group in doc.Application.OpenSharedParameterFile().Groups:
        if definition_group.Name == para_group_name:
            return definition_group
    
    if create_if_not_exist:
        return doc.Application.OpenSharedParameterFile().Groups.Create(para_group_name)
    
    
    
    NOTIFICATION.messenger(main_text="Cannot find [{}] in shared parameter file.\nIs this loaded correctly?".format(para_group_name))
    return None

def get_shared_para_definition_in_txt_file_by_name(doc, 
                                       para_name):
    

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
        is_instance_parameter (bool, optional): True for instance parameter, False for type parameter. Defaults to True.

    Returns:
        bool: True if parameter was added successfully, False otherwise
    """
    # create new shared para to avoid adding same definiation twice
    try:
        DB.SharedParameterElement.Create(project_doc, para_definition)
    except Exception as e:
        print ("cannot add to doc [{}] becasue {}".format(project_doc.Title, e))

        return False
    
    cate_sets = DB.CategorySet()
    for cate in binding_cates:
        cate_sets.Insert(cate)

    binding = DB.InstanceBinding() if is_instance_parameter else DB.TypeBinding()
    binding.Categories = cate_sets
    project_doc.ParameterBindings.Insert(para_definition, binding, get_para_group(para_group))
    return True


def get_para_group(group_name):
    """Gets the built-in parameter group by name.

    Args:
        group_name (str): Name of the parameter group ("Data" or "Set")

    Returns:
        GroupTypeId: Built-in parameter group identifier
    """
    return getattr(DB.GroupTypeId, group_name)

def get_parameter_by_name(doc, 
                          para_name):
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
    L_drive_shared_para_file = "L:\\4b_Applied Computing\\01_Revit\\03_Library\\EA_SharedParam.txt"
    OS_shared_para_file = "Apps\\lib\\EnneadTab\\documents\\revit\\DefaultSharedParameter.txt"
    

    # copy L to override OS
    import shutil
    shutil.copy(L_drive_shared_para_file, OS_shared_para_file)


if __name__ == "__main__":
    __override_L_drive_shared_para_file_to_OS_shared_para_file()