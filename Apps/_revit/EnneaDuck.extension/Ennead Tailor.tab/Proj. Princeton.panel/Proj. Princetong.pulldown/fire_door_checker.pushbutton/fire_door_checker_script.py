#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Find rated walls and doors in the model and highlight them in schedules.

Main Steps:
1. Locate all rated walls based on fire rating parameter
2. Find doors hosted on rated walls
3. Cross reference with door schedule
4. Highlight rated doors in schedule by changing text color to red

Optional:
- Creates a report of findings
- Allows for parameter verification
"""
__title__ = "Fire Door Checker"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

def get_rated_wall_dict(doc):
    """Find all walls with fire rating in the model and organize them by rating value.
    
    Returns:
        dict: Dictionary with fire rating as key and list of walls as value
    """
    walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    rated_walls_by_rating = {}
    
    for wall in walls:
        wall_type = wall.WallType
        fire_rating = wall_type.LookupParameter("Fire Rating")
        if fire_rating and fire_rating.AsString():
            rating_value = fire_rating.AsString()
            if rating_value not in rated_walls_by_rating:
                rated_walls_by_rating[rating_value] = []
            rated_walls_by_rating[rating_value].append(wall)
    
    return rated_walls_by_rating

def get_hosted_door_dict(doc, walls):
    """Find all doors hosted on the given walls.
    
    Uses Revit API to find dependent elements of category Doors that
    are hosted by the provided walls.
    """

    rated_doors_by_rating = {}
    for wall in walls:
        # Get dependent elements of the wall
        dependent_elements_ids = wall.GetDependentElements(None)
        for element_id in dependent_elements_ids:
            element = doc.GetElement(element_id)
            if element and element.Category and element.Category.Id.IntegerValue == int(DB.BuiltInCategory.OST_Doors):
                door_type = doc.GetElement(element.GetTypeId())
                door_type_fire_rating = door_type.LookupParameter("Fire Rating")
                if door_type_fire_rating and door_type_fire_rating.AsString():
                    rating_value = door_type_fire_rating.AsString()
                    if rating_value not in rated_doors_by_rating:
                        rated_doors_by_rating[rating_value] = []
                    rated_doors_by_rating[rating_value].append(element)
            
    return rated_doors_by_rating

def update_door_schedule(doc, rated_doors):
    """Update door schedule to highlight rated doors."""
    for door in rated_doors:
        door.LookupParameter("Fire Rating").Set(door.LookupParameter("Fire Rating").AsInteger())

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def fire_door_checker(doc):
    """Main function to check and highlight fire-rated doors."""
    
    print("Starting Fire Door Check...")
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # Find rated walls
    rated_wall_dict = get_rated_wall_dict(doc)
    print("Found {} rated walls".format(len(rated_wall_dict)))
    
    # Find doors on rated walls
    for wall_rating, walls in rated_wall_dict.items():
        print ("\nChecking Walls with Rating: [{}]".format(wall_rating))
        rated_door_dict = get_hosted_door_dict(doc, walls)
        for door_rating, doors in rated_door_dict.items():
            print("Found {} potentially rated doors on walls with door fire rating [{}]".format(len(doors), door_rating))
            for door in doors:
                door.LookupParameter("Comments").Set("Rated")
    # # Update door schedule
    # update_door_schedule(doc, rated_doors)
    # print("Door schedule updated")
    
    t.Commit()
    print("Fire Door Check Complete!")

################## main code below #####################
if __name__ == "__main__":
    fire_door_checker(DOC)







