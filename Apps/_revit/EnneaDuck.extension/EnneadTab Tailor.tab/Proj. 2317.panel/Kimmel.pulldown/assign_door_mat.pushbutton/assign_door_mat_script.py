#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Assign materials to door panels and frames in the current phase using instance parameters Door_$Panel_Material and Door_$Frame_Material"
__title__ = "Assign Door Mat"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PHASE, REVIT_DESIGN_OPTION, REVIT_MATERIAL, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def assign_door_mat(doc):
    # Get latest phase
    phases = REVIT_PHASE.get_all_phases(doc)
    if not phases:
        NOTIFICATION.messenger(main_text="No phases found in document!")
        return
        
    current_phase = phases[-1]  # Get the latest phase
    
    # Get all doors in current phase
    doors = REVIT_PHASE.get_elements_in_phase(doc, current_phase, DB.BuiltInCategory.OST_Doors)
    doors = REVIT_DESIGN_OPTION.filter_main_and_primary_elements(doors)
    
    if not doors:
        NOTIFICATION.messenger(main_text="No doors found in phase {}!".format(current_phase.Name))
        return
        
    # Get materials from selection
    panel_mat = REVIT_SELECTION.pick_material(doc, title="Select Panel Material")
    if not panel_mat:
        return
        
    frame_mat = REVIT_SELECTION.pick_material(doc, title="Select Frame Material")
    if not frame_mat:
        return

    t = DB.Transaction(doc, __title__)
    t.Start()
    
    updated_count = 0
    for door in doors:
        # Assign panel material using instance parameter
        panel_param = door.LookupParameter("Door_$Panel_Material")
        if panel_param and not panel_param.IsReadOnly:
            panel_param.Set(panel_mat.Id)
            updated_count += 1
            
        # Assign frame material using instance parameter
        frame_param = door.LookupParameter("Door_$Frame_Material")
        if frame_param and not frame_param.IsReadOnly:
            frame_param.Set(frame_mat.Id)
            
    t.Commit()
    NOTIFICATION.messenger(main_text="Successfully assigned materials to {} doors in phase {}!".format(updated_count, current_phase.Name))

################## main code below #####################
if __name__ == "__main__":
    assign_door_mat(DOC)







