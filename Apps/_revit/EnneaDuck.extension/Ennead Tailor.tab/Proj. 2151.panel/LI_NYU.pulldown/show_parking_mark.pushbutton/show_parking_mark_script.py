#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Show Parking Mark"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

import time

from EnneadTab import ERROR_HANDLE, LOG, DATA_VIZ
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def show_parking_mark(doc):

    all_parkings = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements()

    parking_by_level_dict = {}
    for parking in all_parkings:
        level = parking.LookupParameter("ParkingLevel").AsString()
        if level not in parking_by_level_dict:
            parking_by_level_dict[level] = []
        parking_by_level_dict[level].append(parking)
    
    level_used = list(parking_by_level_dict.keys())
    level_used.sort()
    
    for i, level in enumerate(level_used):
        process_parker_per_level(level, parking_by_level_dict[level])
        if i < len(level_used)-1:
            time.sleep(5)



def process_parker_per_level(level_name, parkings):

    data = []
    for parking in parkings:
        local_dict = {
            "x": parking.Location.Point.X,
            "y": parking.Location.Point.Y,
            "attributes": {
                          "primary_value": parking.LookupParameter("ParkingMarker").AsString()
                        }
        }
        data.append(local_dict)
    DATA_VIZ.show_data(data, title="Parking Mark on Level [{}]".format(level_name), show_axis=False)



################## main code below #####################
if __name__ == "__main__":
    show_parking_mark(DOC)







