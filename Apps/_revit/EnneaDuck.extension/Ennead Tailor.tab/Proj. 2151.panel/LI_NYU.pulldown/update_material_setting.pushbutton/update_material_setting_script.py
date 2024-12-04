#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Update Material Setting"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_MATERIAL, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


MATERIAL_MAP = {
    "Curb":{
        "Color": (147, 147, 147),
        "SurfaceForegroundPatternIsSolid": True,
        "SurfaceForegroundPatternColor": (192, 192, 192)
    } ,
    "Road":{
        "Color": (120, 120, 120),
        "SurfaceForegroundPatternIsSolid": True,
        "SurfaceForegroundPatternColor": (150, 150, 150)
    },
    "Grass":{
        "Color": (187, 255, 187),
        "SurfaceForegroundPatternColor": (116, 206, 85),
        "SurfaceBackgroundPatternIsSolid": True,
        "SurfaceBackgroundPatternColor": (238, 252, 233)
    }
}

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_material_setting(doc):

    t = DB.Transaction(doc, __title__)
    t.Start()
    

    for material_name, material_setting in MATERIAL_MAP.items():
        material = REVIT_MATERIAL.get_material_by_name(material_name, doc)
        
        if material is None:
            continue

        if not REVIT_SELECTION.is_changable(material):
            continue

        for setting_name, setting_value in material_setting.items():

            if "IsSolid" in setting_name:
                if setting_value:
                    solid_fill_pattern_id = REVIT_SELECTION.get_solid_fill_pattern_id(doc)
                attr_name = setting_name.replace("IsSolid", "Id")
                setattr(material, attr_name, solid_fill_pattern_id)
                continue
                
            if "color" in setting_name.lower():
                setting_value = DB.Color(setting_value[0], setting_value[1], setting_value[2])
            setattr(material, setting_name, setting_value)

    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    update_material_setting(DOC)







