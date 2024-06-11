import pickle

from pyrevit import script
from pyrevit import revit
from pyrevit import forms


__context__ = 'Selection'
__title__ = "Mark As Ref Tag"

__doc__ = 'Pick a reference tag forits head and elbow position. Store the ID of the selected Tag in a project-dependent memory.\nWorks with the Align Tags tools below.'


datafile = script.get_document_data_file("SelList", "pym")

selection = revit.get_selection()

if len(selection) > 1:
    forms.alert("Please select 1 tags only.")
    script.exit()

 
 
if "Tags" not in selection[0].Category.Name:
    forms.alert("This is not a tag.")
    script.exit()


elid = selection.element_ids
#print elid
#print elid[0]
#print elid[0].IntegerValue
data = elid[0].IntegerValue
#print data
f = open(datafile, 'w')
pickle.dump(data, f)
f.close()
forms.alert("Ref Tag Captured.")
