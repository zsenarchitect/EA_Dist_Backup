#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Export the filled region color setting to excel so you can use it elsewhere."
__title__ = "Export Filled\nRegion Types"
__tip__ = True

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, FOLDER, EXCEL
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


from EnneadTab.EXCEL import ExcelDataItem


@ERROR_HANDLE.try_catch_error
def export_filled_region_types():
    

    all_filled_region_types = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()
    all_filled_region_types = sorted(all_filled_region_types, key = lambda x: x.LookupParameter("Type Name").AsString())

    data = []
    for i, filled_region_type in enumerate(all_filled_region_types):
        type_name = filled_region_type.LookupParameter("Type Name").AsString()
        data.append(ExcelDataItem(type_name, i+1, 0))

        
        background_color = filled_region_type.BackgroundPatternColor
        color_pack = (background_color.Red,
                    background_color.Green,
                    background_color.Blue)
        # print (color_pack)
        color_text = "{}-{}-{}".format(*color_pack)
        data.append(ExcelDataItem("", i+1, 1, color_pack))
        data.append(ExcelDataItem(color_text, i+1, 2))

        
        foreground_color = filled_region_type.ForegroundPatternColor
        color_pack = (foreground_color.Red,
                    foreground_color.Green,
                    foreground_color.Blue)
        color_text = "{}-{}-{}".format(*color_pack)
        data.append(ExcelDataItem("", i+1, 4, color_pack))
        data.append(ExcelDataItem(color_text, i+1, 5))
        
    data.append(ExcelDataItem("FilledRegionType", 0, 0))
    data.append(ExcelDataItem("ForegroundColor", 0, 1))
    data.append(ExcelDataItem("ForegroundColorRGB", 0, 2))
    data.append(ExcelDataItem("BackgroundColor", 0, 4))
    data.append(ExcelDataItem("BackgroundColorRGB", 0, 5))

    filepath = FOLDER.get_EA_dump_folder_file("FilledRegionColor.xlsx")
    EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab", open_after = True)




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    export_filled_region_types()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







