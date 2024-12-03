#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Update the data for dummy patient room so its data is correct in schedule."
__title__ = "Update Dummy Patient Room"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


FAMILY_NAME = "PatientRoomDummy"


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_dummy_patient_room(doc):
    t = DB.Transaction(doc, __title__)
    t.Start()

    
    all_types = REVIT_FAMILY.get_all_types_by_family_name(FAMILY_NAME,doc = doc, return_name=True)
    for family_type in all_types:
        all_instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(FAMILY_NAME, family_type, doc = doc, editable_only=True)


        for instance in all_instances:
            view_placed = doc.GetElement(instance.OwnerViewId)
            try:
                level = view_placed.GenLevel.Name
            except:
                level = "Level unknown"
            instance.LookupParameter("PatientRoomLevel").Set(level)
    
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    update_dummy_patient_room(DOC)







