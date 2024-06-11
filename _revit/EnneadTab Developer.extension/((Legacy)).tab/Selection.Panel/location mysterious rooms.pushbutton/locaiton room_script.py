__doc__ = "Get room by name or department, great if you want to find mysterious room in your schedule"
__title__ = "Get Room\nBy..."

from pyrevit import forms, DB, revit, script



class ListOption(forms.TemplateListItem):
    @property
    def name(self):
        if "Room Name" in res:
            room_name = self.LookupParameter("Name").AsString()
            if room_name:
                return room_name
            else:
                return "$$No Name Room"
        elif "Department" in res:
            department = self.LookupParameter("Department").AsString()
            if department:
                return department
            else:
                return "$$No Department Room"
        elif "Occupancy" in res:
            occupancy = self.LookupParameter("Occupancy").AsString()
            if occupancy:
                return occupancy
            else:
                return "$$No Occupancy Room"
        elif "Phase" in res:
            print(self.Number)
            print(self.Parameter[DB.BuiltInParameter.ROOM_PHASE].AsString())
            print(self.Parameter[DB.BuiltInParameter.ROOM_PHASE_ID].AsString())
            phase = revit.doc.GetElement(phase_id).Name

            if phase:
                return phase
            else:
                return "$$No Phase Room"
        else:
            script.exit()
            
    @property
    def count(self):
        pass
################## main code below #####################

all_rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()



res = forms.alert(options = ["Room Name", "Room Department", "Room Occupancy", "Not Placed Room And Delete Them"], msg = "I want to filter by [.....]")


if "Not Placed Room" in res:
    #room_id_to_delete = []
    with revit.Transaction("Delete Not Placed Rooms"):
        count = 0
        for room in all_rooms:
            if room.Location == None and room.Area <= 0:

                #room_id_to_delete.append(room.Id)
                revit.doc.Delete(room.Id)
                count += 1
        forms.alert("{} not placed rooms are removed from project.".format(count))
else:
    display_options = [ListOption(x) for x in all_rooms]
    display_options.sort(key = lambda x: x.name, reverse = True)
    sel_rooms = forms.SelectFromList.show(display_options,
                                    multiselect=True,
                                    button_name='Select Rooms',
                                    title = "Get Room by {}".format(res))




    revit.get_selection().set_to(sel_rooms)
