#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Update Material Setting"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
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
    

    REVIT_MATERIAL.update_material_setting(doc, MATERIAL_MAP)

    t.Commit()
    NOTIFICATION.messenger(main_text="Material setting updated")



################## main code below #####################
if __name__ == "__main__":
    update_material_setting(DOC)







