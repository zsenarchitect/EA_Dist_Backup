#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Update door marks based on their To Room parameter values. If multiple doors lead to the same room, append A, B, C etc. to make them unique."
__title__ = "Room To Door Mark"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PHASE, REVIT_SELECTION, REVIT_DESIGN_OPTION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import script # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

class DoorMarker:
    def __init__(self, doc):
        self.doc = doc
        self.output = script.get_output()
        self.phase = REVIT_PHASE.get_phase_by_name("Renovation 1", doc)
        if not self.phase:
            self.output.print_md("**Error**: Could not find phase 'Renovation 1'")
            return

    def get_room_number(self, room):
        """Get the room number from a room element."""
        room_number = room.LookupParameter("Number").AsString()
        if not room_number:
            self.output.print_md("**Warning**: Room {} has empty Number value".format(self.output.linkify(room.Id)))
        return room_number

    def get_room_for_door(self, door):
        """Get the associated room for a door in the given phase."""
        room = door.ToRoom[self.phase]
        if not room:
            self.output.print_md("**Info**: No ToRoom found for door {}".format(self.output.linkify(door.Id)))
            room = door.FromRoom[self.phase]
            if not room:
                self.output.print_md("**Warning**: No FromRoom found for door {}".format(self.output.linkify(door.Id)))
        return room

    def change_door_mark(self, door, mark):
        """Change the mark of a door if it's changeable and the mark is different."""
        mark = str(mark).strip()
        
        if not REVIT_SELECTION.is_changable(door):
            self.output.print_md("**Warning**: Door {} is not changeable, skipping".format(self.output.linkify(door.Id)))
            return False
            
        design_option = door.DesignOption
        if design_option is not None and not REVIT_SELECTION.is_changable(design_option):
            self.output.print_md("**Warning**: Door {} is in a non-changeable design option {}, skipping".format(
                self.output.linkify(door.Id), 
                self.output.linkify(design_option.Id, title=design_option.Name)))
            return False
                
        current_mark = door.LookupParameter("Mark").AsString()
        if current_mark != mark:
            door.LookupParameter("Mark").Set(mark)
            return True
        return False

    def process_doors(self):
        """Process all doors and update their marks."""
        if not self.phase:
            return

        t = DB.Transaction(self.doc, __title__)
        t.Start()
        
        # Get all doors in the project
        doors = REVIT_PHASE.get_elements_in_phase(self.doc, self.phase, DB.BuiltInCategory.OST_Doors)
        doors = REVIT_DESIGN_OPTION.filter_main_and_primary_elements(doors)
        doors = [door for door in doors if "NEST" not in door.Symbol.LookupParameter("Type Mark").AsString()]
        
        # Dictionary to track room numbers and their associated doors
        room_doors = {}
        
        # Process each door
        for door in doors:
            room = self.get_room_for_door(door)
            if not room:
                self.change_door_mark(door, "no ToRoom or FromRoom assigned")
                continue
            
            room_number = self.get_room_number(room)
            if not room_number:
                self.change_door_mark(door, "no room Number for the ToRoom")
                continue
            
            # Track door for this room number
            if room_number not in room_doors:
                room_doors[room_number] = []
            room_doors[room_number].append(door)
        
        # Update door marks, handling duplicates
        for room_number, doors in room_doors.items():
            if len(doors) == 1:
                self.change_door_mark(doors[0], room_number)
            else:
                for i, door in enumerate(doors):
                    suffix = chr(65 + i)  # 65 is ASCII for 'A'
                    self.change_door_mark(door, room_number + suffix)
        
        t.Commit()
        self.output.print_md("**Success**: Door marks updated successfully")

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def room_to_door_mark(doc):
    """Main function to update door marks based on room numbers."""
    marker = DoorMarker(doc)
    marker.process_doors()

if __name__ == "__main__":
    room_to_door_mark(DOC)







