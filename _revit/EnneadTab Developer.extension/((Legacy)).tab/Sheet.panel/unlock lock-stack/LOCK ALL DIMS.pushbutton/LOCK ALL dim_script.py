__doc__ = "Lock or unlock all dimensions in project."
__title__ = "(un)LOCK\nALL dim"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

dims = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Dimensions).WhereElementIsNotElementType().ToElements()
res = forms.alert(options = ["lock", "unlock"], msg = "i want to ... all dims")
output.freeze()
with revit.Transaction("lock dims"):
    #map(lambda x: x.Pinned = True, key_note_tags)
    for dim in dims:

        #print dim.GroupId


        if dim.GroupId == -1:
            print("Skip dim in group")
            continue

        if EA_UTILITY.is_owned(dim):
            print("skip element owned by other")
            continue
        try:
            if res == "lock":
                dim.Pinned = True
            else:
                dim.Pinned = False
        except:
            print(dim.NumberOfSegments)
            print(output.linkify(dim.Id))
output.unfreeze()
