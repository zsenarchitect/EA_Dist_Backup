__doc__ = "If there are dims that use global prameter in current view, this will turn on the label in view.\nUseful for 'control views' such as grids view, levels views. In there you can lock in predefined dim to avoid minor off in dims."
__title__ = "Show\nLabels"
from pyrevit import DB,forms, script, revit

dims = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfCategory(DB.BuiltInCategory.OST_Dimensions).WhereElementIsNotElementType().ToElements()

count = 0
with revit.Transaction("Turn On labels"):
    for dim in dims:
        #print dim
        #print dim.LookupParameter("Show Label in View")
        try:
            dim.LookupParameter("Show Label in View").Set(True)
            count += 1
        except Exception as e:
            #print (e)
            continue
if count > 0:
    forms.alert("{} dims show labels in current view.".format(count))
else:
    forms.alert("No dims can show label in current view.")
