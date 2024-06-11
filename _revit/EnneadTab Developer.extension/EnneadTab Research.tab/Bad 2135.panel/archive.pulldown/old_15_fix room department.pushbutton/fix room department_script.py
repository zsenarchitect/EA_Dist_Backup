__doc__ = "DO NOT USE, use new fix room department."
__title__ = "[obsolete]15_fix room department"

from pyrevit import forms, DB, revit, script
import random

def get_all_rooms():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

def is_department_in_checklist(room):
    global department_checklist
    if room.LookupParameter("Department").AsString() in department_checklist:
        return True
    return False


def set_rm_department(room, department):
    global in_group_rm_found
    if room.GroupId.IntegerValue  > 0:
        print("skipping room {} becasue it is in group [{}]. Level = {}".format(output.linkify(room.Id),revit.doc.GetElement(room.GroupId).Name, room.Level.Name))
        in_group_rm_found = True
        return
    try:
        room.LookupParameter("Department").Set(department)
    except Exception as e:
        print("*"*10)
        print("skipping room {} ".format(output.linkify(room.Id)))
        print (e)
        print("*"*10)

def try_to_fix_rm(room):
    global is_finish_tool
    global department_checklist

    current_department = room.LookupParameter("Department").AsString()
    try:
        level = revit.doc.GetElement(room.LevelId).Name
    except:
        level = "N/A"
    room_name = room.LookupParameter("Name").AsString()
    res = forms.alert("Find room with a department [{}], you want to ...".format(current_department), title=None, sub_msg="level = {}\nroom name = {}".format(level, room_name), options=["fix this one only", "fix similar room with same department", "keep it as current and find next", "finish tool"])
    if res == "keep it as current and find next":
        return
    if res == "finish tool":
        is_finish_tool = True
        return

    #target = forms.alert("pick a target department from below.", options = department_checklist)
    target = forms.SelectFromList.show(button_name = "pick a target department", \
                                    context = department_checklist, \
                                    multiselect = False)

    if res == "fix this one only":
        set_rm_department(room, target)
        return
    if res == "fix similar room with same department":
        similar_rms = filter(lambda x: x.LookupParameter("Department").AsString() == current_department, get_all_rooms())
        map(lambda x: set_rm_department(x, target), similar_rms)
        return




################## main code below #####################
output = script.get_output()
output.close_others()
in_group_rm_found = False



department_checklist = ["ANCHOR STORE",\
                        "CIRCULATION",\
                        "CULTURE",\
                        "CULTURE CORE AND RESTROOM",\
                        "ELEVATOR FREIGHT AND FIRE",\
                        "ELEVATOR OFFICE HIGH ZONE",\
                        "ELEVATOR OFFICE MID ZONE",\
                        "ELEVATOR OFFICE LOW ZONE",\
                        "ELEVATOR RETAIL",\
                        "ELEVATOR VIP",\
                        "ELEVATOR VISITOR CENTER",\
                        "FOOD AND BEVERAGE",\
                        "OFFICE",\
                        "OFFICE CONFERENCE",\
                        "OFFICE CORE AND RESTROOM",\
                        "OFFICE LOBBY",\
                        "RETAIL",\
                        "RETAIL CORE AND RESTROOM",\
                        "SUPPORT CIRCULATION",\
                        "SUPPORT GYM",\
                        "SUPPORT LEISURE SPACE",\
                        "SUPPORT MULTIFUNCTION HALL",\
                        "SUPPORT SERVICE CENTER",\
                        "SUPPORT TRAINING ROOM",\
                        "TERRACE",\
                        "VIP GR CONFERENCE",\
                        "VIP RECEPTION AND LOBBY",\
                        "VISITOR CENTER CORE AND RESTROOM",\
                        "VISITOR CENTER LOBBY CIRCULATION",\
                        "VISITOR CONFERENCE",\
                        "VISITOR IMAGE DISPLAY",\
                        "VISITOR ROUND THEATER",\
                        "VISITOR TRAINING"]



with revit.Transaction("fix room"):
    is_finish_tool = False
    bad_rms = filter(lambda x: not is_department_in_checklist(x), get_all_rooms())

    safety = 0
    while len(bad_rms) != 0 :
        if is_finish_tool:
            break
        if safety > 100:
            break
        safety += 1

        try_to_fix_rm(random.choice(bad_rms))
        bad_rms = filter(lambda x: not is_department_in_checklist(x), get_all_rooms())

if in_group_rm_found:
    forms.alert("some room cannot be changed becasue they are in a group. See output window for detail")
    output.show()
    output.center()
