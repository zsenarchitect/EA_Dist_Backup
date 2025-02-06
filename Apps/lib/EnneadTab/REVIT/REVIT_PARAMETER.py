"""many helper func that help to dynamically add/pick project parameter, shared paramenter, """

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import NOTIFICATION
import SAMPLE_FILE
import DATA_FILE

try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
except:
    pass


def get_project_info_para_by_name(doc, para_name):
    proj_info = doc.ProjectInformation
    for para in proj_info.Parameters:
        if para.Definition.Name == para_name:
            return para
    return None

def get_project_data_name(doc):
    para_name = "EnneadTab_Data"
    para = get_project_info_para_by_name(doc, para_name)
    if not para:
        definition = get_shared_para_definition_in_txt_file_by_name(doc, para_name)
        if not definition:
            definition = create_shared_parameter_in_txt_file(doc, para_name, DB.SpecTypeId.String.Text)
        add_shared_parameter_to_project_doc(doc, 
                                            definition, 
                                            "Data", 
                                            [DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_ProjectInformation)])

        para = get_project_info_para_by_name(doc, para_name)
        para.Set(doc.Title)

    return get_project_info_para_by_name(doc, para_name).AsString()

def get_project_data_file(doc):
    project_data_name = get_project_data_name(doc)
    return "ProjectData_{}.sexyDuck".format(project_data_name)

def get_revit_project_data(doc):
    return DATA_FILE.get_data(get_project_data_file(doc), is_local=False)


def set_revit_project_data(doc, data):
    DATA_FILE.set_data(data, get_project_data_file(doc), is_local=False)


def create_shared_parameter_in_txt_file(doc,
                            para_name,
                            para_type,
                            para_group_name = "EnneadTab"):
    """This will create parameter in the shared parameter text file, but not yet bind to anytthing

    Args:
        doc (_type_): _description_
        para_name (_type_): _description_
        para_type (_type_): DB.SpecTypeId.Boolean.YesNo, etc
        para_group (_type_): _description_

    Returns:
        _type_: _description_
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
    """add shared parameter to project doc
    para_definition: definition object
    para_group: Data, Set
    binding_cates: list of category
    default_value: None
    is_instance_parameter: False. Not for project info it MUST be instance para
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
    """
    Data,
    Set
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