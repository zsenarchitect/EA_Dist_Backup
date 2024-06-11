__doc__ = "DO NOT USE, feature not needed."
__title__ = "old_13_who is owning what"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

output.freeze()
safety = 0
for element in DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().ToElements():
    safety += 1
    if safety > 110000:
        break
    detail = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc,element.Id)
    # wti.Creator, wti.Owner, wti.LastChangedBy
    user_name = detail.Owner
    #user_name = revit.query.get_history(element).owner
    #print user_name
    if len(user_name) > 1:

        print("{} owning {}----{}".format(user_name, element.GetType(), output.linkify(element.Id, title = "go to element")))
output.unfreeze()
