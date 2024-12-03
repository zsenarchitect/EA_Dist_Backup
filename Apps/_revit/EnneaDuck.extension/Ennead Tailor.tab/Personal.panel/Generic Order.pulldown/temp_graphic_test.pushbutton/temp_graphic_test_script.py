#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Temp Graphic Test"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, IMAGE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def temp_graphic_test():
    
    image = IMAGE.create_bitmap_text_image(text = "Ni Hao~")
    graphic_data = REVIT_VIEW.GraphicDataItem(DB.XYZ(400,150,50), additional_info={"description":"Hello"}, image = image)
    REVIT_VIEW.show_in_convas_graphic(graphic_data)




################## main code below #####################
if __name__ == "__main__":
    temp_graphic_test()







