#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Update door marks based on their To Room parameter values. If multiple doors lead to the same room, append A, B, C etc. to make them unique."
__title__ = "Room To Door Mark"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PHASE, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import script

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def room_to_door_mark(doc):
    output = script.get_output()
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # Get all doors in the project
    doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    
    # Get the Renovation 1 phase
    phase = REVIT_PHASE.get_phase_by_name("Renovation 1", doc)
    if not phase:
        output.print_md("**Error**: Could not find phase 'Renovation 1'")
        t.RollBack()
        return
    
    # Dictionary to track room numbers and their associated doors
    room_doors = {}
    
    # First pass: collect all doors and their target room numbers
    for door in doors:
        if "NEST" in door.Symbol.LookupParameter("Type Mark").AsString():
            continue
        
        # Get the room from the Renovation 1 phase
        room = door.ToRoom[phase]
        if not room:
            continue
            
        # Get room number parameter
        room_number_param = room.LookupParameter("Number")
        if not room_number_param:
            output.print_md("**Warning**: Room {} has no Number parameter".format(output.linkify(room.Id)))
            continue
            
        room_number = room_number_param.AsString()
        if not room_number:
            output.print_md("**Warning**: Room {} has empty Number value".format(output.linkify(room.Id)))
            continue
            
        if room_number not in room_doors:
            room_doors[room_number] = []
        room_doors[room_number].append(door)
    
    # Second pass: update door marks, handling duplicates
    for room_number, doors in room_doors.items():
        if len(doors) == 1:
            # Single door to room - just use room number
            change_door_mark(doors[0], room_number)
        else:
            # Multiple doors to same room - append A, B, C etc.
            for i, door in enumerate(doors):
                suffix = chr(65 + i)  # 65 is ASCII for 'A'
                mark = room_number + suffix
                change_door_mark(door, mark)
                
    t.Commit()


def change_door_mark(door, mark):
    output = script.get_output()
    
    # Check if door is changeable
    if not REVIT_SELECTION.is_changable(door):
        output.print_md("**Warning**: Door {} is not changeable, skipping".format(output.linkify(door.Id)))
        return
        
    # Check if door is in a design option
    design_option = door.DesignOption
    if design_option is not None:
        if not REVIT_SELECTION.is_changable(design_option):
            output.print_md("**Warning**: Door {} is in a non-changeable design option {}, skipping".format(output.linkify(door.Id), output.linkify(design_option.Id, title=design_option.Name)))
            return
            
    print ("setting mark to {}".format(mark))
    door.LookupParameter("Mark").Set(mark)


################## main code below #####################
if __name__ == "__main__":
    room_to_door_mark(DOC)







