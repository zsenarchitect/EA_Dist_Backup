__doc__ = "If room height is between 150mm and 3201mm, set it to 3200mm."
__title__ = "fix room height"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab

################## main code below #####################
output = script.get_output()
output.close_others()

rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

with revit.Transaction("fix room height"):
    for room in rooms:
        room_height = EA_UTILITY.ft_to_mm(room.LookupParameter("Limit Offset").AsDouble())
        if 150 < room_height < 3201:
            height = EA_UTILITY.mm_to_ft(3200)
            if room.GroupId.IntegerValue  > 0:
                print("skipping room {} becasue it is in group [{}]. Level = {}".format(output.linkify(room.Id),revit.doc.GetElement(room.GroupId).Name, room.Level.Name))
                continue
            room.LookupParameter("Limit Offset").Set(height)
