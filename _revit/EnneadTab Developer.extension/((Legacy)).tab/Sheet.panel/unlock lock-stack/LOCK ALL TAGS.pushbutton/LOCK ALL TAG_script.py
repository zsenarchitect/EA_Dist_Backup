__doc__ = "Lock or unlock all keynote tags in the documents."
__title__ = "(un)LOCK\nALL keynoteTAG"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

key_note_tags = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_KeynoteTags).WhereElementIsNotElementType().ToElements()
res = forms.alert(options = ["lock", "unlock"], msg = "i want to ... all keynote tags")
with revit.Transaction("lock keynote tags"):
    #map(lambda x: x.Pinned = True, key_note_tags)
    for tag in key_note_tags:

        if EA_UTILITY.is_owned(tag):
            print("skip element owned by other")
            continue

        if res == "lock":
            tag.Pinned = True
        else:
            tag.Pinned = False
