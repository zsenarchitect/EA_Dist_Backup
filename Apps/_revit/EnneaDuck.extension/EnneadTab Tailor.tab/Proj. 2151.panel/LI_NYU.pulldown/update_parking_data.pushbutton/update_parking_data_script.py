#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Update tehe parking dataso it make sense in schedeul.

Note: this tool is to be run so first all parking stall update instance parameter.
For the Site file it do the additional super summery."""
__title__ = "Update Parking Data"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, USER
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_FAMILY, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore 


# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

DOC_NAME_MAP = {
    "2151_A_EA_NYULI_Site": "Site",
    "2151_A_EA_NYULI_Parking East":"Garage East",
    "2151_A_EA_NYULI_Parking West":"Garage West",
    "2151_A_EA_NYULI_CUP_EXT": "CUP",
    "2151_A_EA_NYULI_Hospital_EXT": "Hospital",
    "2151_A_EA_NYU Melville_Garage North":"Garage North"
}

FAMILY_DATA = {
    "Parking Stall": {
        "Standard": {
            "Width": 9,
            "Length": 18,
            "Type Comments": "Standard",
            "is_ADA": False,
            "is_perpendicular": True,
            "is_layback":False
        },
        "ADA": {
            "Width": 9,
            "Length": 18,
            "Type Comments": "ADA",
            "is_ADA": True,
            "is_perpendicular": True,
            "is_layback":False
        },
        "Ambulance": {
            "Width": 12,
            "Length": 25,
            "Type Comments": "Ambu.",
            "is_ADA": False,
            "is_perpendicular": True,
            "is_layback":False
        },
        "Truck": {
            "Width": 12,
            "Length": 55,
            "Type Comments": "Truck",
            "is_ADA": False,
            "is_perpendicular": True,
            "is_layback":False
        },
        "Waste Truck": {
            "Width": 12,
            "Length": 35,
            "Type Comments": "Waste Truck",
            "is_ADA": False,
            "is_perpendicular": True,
            "is_layback":False
        },
        "Layback": {
            "Width": 9,
            "Length": 22,
            "Type Comments": "Layback",
            "is_ADA": False,
            "is_perpendicular": False,
            "is_layback":True
        },
    },
    "Parking Stall_Angled": {
        "Standard": {
            "W": 9,
            "L": 23,
            "Type Comments": "Standard"
        },
    }
}


import sys
import os
script_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_folder)
import parking_calculator as PC #pyrevit: ignore
import parking_tag_manager as PTM #pyrevit: ignore

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_parking_data(doc, show_log = False, is_from_sync_hook = False):

    if doc.Title not in DOC_NAME_MAP:
        NOTIFICATION.messenger("This doc is not registered")
        return

    update_type(doc, show_log)
    update_instance(doc)

    PTM.manage_parking_tags(doc, show_log)

    if doc.Title == "2151_A_EA_NYULI_Site":
        if not USER.IS_DEVELOPER and is_from_sync_hook:
            options = ["Yes, update the data calculator", "No, skip updating and return to working immediately."]
            res = REVIT_FORMS.dialogue(main_text="Do you want to update the data calculator?", 
                                       sub_text="This might take extra 15 secs to run, but make the total count schedule more accurate.", 
                                       options=options)
            if res == options[1] or res is None:
                return
        PC.update_calc_parking_data(doc)

    NOTIFICATION.messenger("Pakring Data Updated.")


def update_type(doc, show_log = False):
    t = DB.Transaction(doc, __title__)
    t.Start()
    REVIT_FAMILY.update_family_type_by_dict(doc, FAMILY_DATA, show_log=show_log)
    t.Commit()

def update_instance(doc):    
    all_parkings = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements()
    all_parkings = REVIT_SELECTION.filter_elements_changable(all_parkings)

    if not all_parkings:
        return
    
    t = DB.Transaction(doc, __title__)
    t.Start()

    
    for parking in all_parkings:
        if not parking.LookupParameter("BldgId") or not parking.LookupParameter("ParkingLevel") or not parking.LookupParameter("ParkingZone"):
            print("{} is missing BldgId, ParkingLevel, or ParkingZone".format(parking.Name))
            t.RollBack()
            break

        parking_level = set_parking_level(parking)
        parking.LookupParameter("ParkingLevel").Set(parking_level)

        bldg_id = DOC_NAME_MAP.get(doc.Title, doc.Title)
        parking.LookupParameter("BldgId").Set(bldg_id)

        if parking.Symbol.LookupParameter("Type Comments").AsString() == "Ambu.":
            parking.LookupParameter("ParkingUser").Set("Ambu.")

        # make sure it is never empty
        if parking.LookupParameter("ParkingUser").AsString() in ["", None]:
            parking.LookupParameter("ParkingUser").Set("Undefined")

        if REVIT_SELECTION.is_outside_multi_group(parking):            
            if parking.LookupParameter("is_flipped_symbol"):
                parking.LookupParameter("is_flipped_symbol").Set(parking.Mirrored )

        if parking.LookupParameter("ParkingZone").AsString() in ["", "zone not defined.", None]:
            parking.LookupParameter("ParkingZone").Set(bldg_id)

        if parking.LookupParameter("ParkingMarker").AsString() in ["", None]:
            parking.LookupParameter("ParkingMarker").Set("Undefined")
    t.Commit()


def set_parking_level(parking):
    level = parking.LookupParameter("Level").AsValueString()
    if level:
        return level
    host = parking.Host
    if host:
        level = host.LookupParameter("Level").AsValueString()
        if level:
            return level
    return "maybe lost host association"

################## main code below #####################
if __name__ == "__main__":
    update_parking_data(DOC, show_log=True)







