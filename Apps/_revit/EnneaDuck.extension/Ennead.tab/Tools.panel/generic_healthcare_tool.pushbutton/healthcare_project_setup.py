from EnneadTab import NOTIFICATION 
from EnneadTab.REVIT import REVIT_PARAMETER, REVIT_PROJ_DATA
from Autodesk.Revit import DB # pyright: ignore

from pyrevit import forms

__doc__ = """Healthcare project configuration wizard that transforms your Revit project into a well-organized healthcare documentation powerhouse! 

This setup utility:
- Establishes essential project data tracking
- Configures PIM numbering parameters
- Sets up area tracking parameters
- Synchronizes project level information

Run this at the beginning of your healthcare project to ensure smooth documentation workflow and standards compliance."""


############### MAIN SETUP FUNCTIONS ###############
def setup_healthcare_project(doc):
    t = DB.Transaction(doc, "setup ennedtab project data")
    t.Start()
    REVIT_PROJ_DATA.setup_project_data(doc)
    t.Commit()

    
    t = DB.Transaction(doc, "setup healthcare project")
    t.Start()
    proj_data = REVIT_PROJ_DATA.get_revit_project_data(doc)

    update_project_levels_in_project_data(doc, proj_data)
    setup_pim_number_parameter(doc)
    if not setup_area_tracking_parameters(doc, proj_data):
        return t.RollBack()

    REVIT_PROJ_DATA.set_revit_project_data(doc, proj_data)
    t.Commit()

    NOTIFICATION.messenger("Healthcare project setup complete.")



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


############### ENTRY POINT ###############
if __name__ == "__main__":
    pass