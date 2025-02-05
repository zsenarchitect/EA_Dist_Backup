
from EnneadTab import NOTIFICATION, DATA_FILE, FOLDER, USER
from EnneadTab.REVIT import REVIT_PARAMETER
from Autodesk.Revit import DB # pyright: ignore
import os


def setup_healthcare_project(doc):

    t = DB.Transaction(doc, "setup healthcare project")
    t.Start()

    # confirm is have [EnneadTab_Data] parameter in project info
    para = REVIT_PARAMETER.get_shared_para_definition_by_name(doc, "EnneadTab_Data")
    if not para:

        new_definition = REVIT_PARAMETER.create_shared_parameter(doc, "EnneadTab_Data", DB.SpecTypeId.String.Text)
        REVIT_PARAMETER.add_shared_parameter_to_project_doc(doc, new_definition, "Data", [DB.Category(DB.BuiltInCategory.OST_ProjectInformation)])
        doc.LookupParameter("EnneadTab_Data").Set(doc.Title)

    data = DATA_FILE.get_data("ProjectData_{}.sexyDuck".format(doc.Title), is_local=False)
    if not data:
        data = {
            "container_file": None,
            "is_update_view_name_format": True,
            "parking_data": {
                "auto_update_enabled": True,
                "parking_dict": {}
            },
                "area_tracking": {
                "auto_update_enabled": True,
                "area_dict": {}
            },
            "wall_type_update": {
                "auto_update_enabled": True,
                "wall_type_dict": {}
            },
            "parking_update": {
                "auto_update_enabled": True,
                "parking_dict": {}
            },
            "color_update": {
                "auto_update_enabled": True,
                "color_dict": {}
            }
        }
        DATA_FILE.set_data(data, "ProjectData_{}.sexyDuck".format(doc.Title), is_local=False)



    # add [PIM Number] parameter to project info
    para = REVIT_PARAMETER.get_shared_para_definition_by_name(doc, "PIM Number")
    if not para:

        new_definition = REVIT_PARAMETER.create_shared_parameter(doc, "PIM Number", DB.SpecTypeId.String.Text)
        REVIT_PARAMETER.add_shared_parameter_to_project_doc(doc, new_definition, "Data", [DB.Category(DB.BuiltInCategory.OST_ProjectInformation)])
        doc.LookupParameter("PIM Number").Set("123321")


    # [debug]open setup file json

    file = FOLDER.get_shared_dump_folder_file("ProjectData_{}.sexyDuck".format(doc.Title))
    os.startfile(file)




    t.Commit()
