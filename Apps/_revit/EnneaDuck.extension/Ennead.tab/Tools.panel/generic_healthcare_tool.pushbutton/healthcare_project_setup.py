
from EnneadTab import NOTIFICATION, FOLDER
from EnneadTab.REVIT import REVIT_PARAMETER
from Autodesk.Revit import DB # pyright: ignore
import os

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
        "setting": {
            "primary_option": {
                "option_name": "",
                "levels": []
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
        "setting": {}
    }
}


def setup_healthcare_project(doc):

    t = DB.Transaction(doc, "setup healthcare project")
    t.Start()

    data = REVIT_PARAMETER.get_revit_project_data(doc)
    if not data:
        levels = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements())
        levels.sort(key=lambda x: x.Elevation, reverse=True)
        level_names = [level.Name for level in levels]
        TEMPLATE_DATA["area_tracking"]["setting"]["primary_option"]["levels"] = level_names
        REVIT_PARAMETER.set_revit_project_data(doc, TEMPLATE_DATA)

    # add [PIM Number] parameter to project info
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

    REVIT_PARAMETER.get_project_info_para_by_name(doc, para_name).Set("Replace Me with the real PIM Number")
    t.Commit()

    data_file = REVIT_PARAMETER.get_project_data_file(doc)
    file = FOLDER.get_shared_dump_folder_file(data_file)
    os.startfile(file)





if __name__ == "__main__":
    pass