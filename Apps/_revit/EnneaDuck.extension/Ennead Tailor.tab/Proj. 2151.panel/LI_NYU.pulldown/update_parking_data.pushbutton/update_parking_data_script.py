#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Update tehe parking dataso it make sense in schedeul"
__title__ = "Update Parking Data"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

DOC_NAME_MAP = {
    "2151_A_EA_NYULI_Site": "Site",
    "2151_A_EA_NYULI_Parking East":"Parking East",
    "2151_A_EA_NYULI_Parking West":"Parking West",
    "2151_A_EA_NYULI_CUP_EXT": "CUP",
    "2151_A_EA_NYULI_HOSPITAL_EXT": "Hospital"


}

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_parking_data(doc, show_log = False):
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
            parking.LookupParameter("ParkingLevel").Set("to use group")

        parking.LookupParameter("BldgId").Set(DOC_NAME_MAP.get(doc.Title, doc.Title))
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    update_parking_data(DOC)







