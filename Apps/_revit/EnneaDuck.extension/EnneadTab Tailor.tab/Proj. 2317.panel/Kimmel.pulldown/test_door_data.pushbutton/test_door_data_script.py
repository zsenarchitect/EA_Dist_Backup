#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Process door fire rating parameters by transferring 'Bad' values to other fire rating parameters.
This script will:
1. Find all doors with 'Bad' fire rating values
2. Transfer these values to other fire rating parameters on the same door
3. Mark the original parameters as 'Transfered out'
"""
__title__ = "Test Door Data"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def test_door_data(doc):
    """Process door fire rating parameters.
    
    Args:
        doc (DB.Document): Current Revit document
    """
    # Collect all doors and prepare parameter tracking
    all_doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    
    # Dictionary to store door parameters: {door_id: {param_id: param}}
    door_params = {}
    bad_params = set()
    
    # First pass: collect all parameters and identify bad ones
    for door in all_doors:
        door_id = door.Id
        door_params[door_id] = {}
        
        for para in door.GetParameters("Fire Rating"):
            if not para:
                continue
                
            param_id = para.Definition.Id
            door_params[door_id][param_id] = para
            
            if para.AsValueString() == "Bad":
                bad_params.add(param_id)

    # Second pass: process parameters in a single transaction
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    for door in all_doors:
        door_id = door.Id
        params = door_params[door_id]
        
        # Find bad value if exists
        bad_value = None
        for param_id, para in params.items():
            if param_id in bad_params:
                bad_value = para.AsValueString()
                break
        
        if not bad_value:
            continue
            
        # Transfer value to other parameters
        for param_id, para in params.items():
            if param_id not in bad_params:
                para.Set(bad_value)
        
        # Mark original parameters
        for param_id, para in params.items():
            if param_id in bad_params:
                para.Set("Transfered out")
    
    t.Commit()


################## main code below #####################
if __name__ == "__main__":
    test_door_data(DOC)







