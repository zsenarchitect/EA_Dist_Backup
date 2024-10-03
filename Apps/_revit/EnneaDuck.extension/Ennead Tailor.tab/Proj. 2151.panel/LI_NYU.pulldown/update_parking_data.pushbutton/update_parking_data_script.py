#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Update tehe parking dataso it make sense in schedeul"
__title__ = "Update Parking Data"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

DOC_NAME_MAP = {
    "2151_A_EA_NYULI_Site": "Site",
    "2151_A_EA_NYULI_Parking East":"Parking East",
    "2151_A_EA_NYULI_Parking West":"Parking West",
    "2151_A_EA_NYULI_CUP_EXT": "CUP Surface",
    "2151_A_EA_NYULI_HOSPITAL_EXT": "Hospital"
}

FAMILY_DATA = {
    "Parking Stall": {
        "Standard": {
            "Width": 9,
            "Length": 18,
            "Type Comments": "Standard",
            "is_ADA": False,
        },
        "ADA": {
            "Width": 9,
            "Length": 18,
            "Type Comments": "ADA",
            "is_ADA": True,
        },
        "Ambulance": {
            "Width": 12,
            "Length": 25,
            "Type Comments": "Ambu.",
            "is_ADA": False,
        }
    },
    "Parking Stall_Angled": {
        "Standard": {
            "W": 9,
            "L": 23,
            "Type Comments": "Standard"
        },
    }
}



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_parking_data(doc, show_log = False):
    update_type(doc, show_log)
    update_instance(doc)

def update_type(doc, show_log = False):
    t = DB.Transaction(doc, __title__)
    t.Start()
    REVIT_FAMILY.update_family_type_by_dict(doc, FAMILY_DATA, show_log=show_log)
    t.Commit()

def update_instance(doc):    
    all_parking = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements()
    all_parking = REVIT_SELECTION.filter_elements_changable(all_parking)

    if not all_parking:
        return
    


    t = DB.Transaction(doc, __title__)
    t.Start()
    for parking in all_parking:
        if not parking.LookupParameter("BldgId") or not parking.LookupParameter("ParkingLevel"):
            t.RollBack()
            break

        
        level = parking.LookupParameter("Level").AsValueString()
        if level:
            parking.LookupParameter("ParkingLevel").Set(level)
        else:
            parking.LookupParameter("ParkingLevel").Set("on a ramp, to be figured out")

        parking.LookupParameter("BldgId").Set(DOC_NAME_MAP.get(doc.Title, doc.Title))

        if parking.Symbol.LookupParameter("Type Comments").AsString() == "Ambu.":
            parking.LookupParameter("ParkingUser").Set("Ambu.")

        if parking.LookupParameter("is_flipped_symbol"):
            parking.LookupParameter("is_flipped_symbol").Set(parking.HandFlipped)
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    update_parking_data(DOC, show_log=True)







