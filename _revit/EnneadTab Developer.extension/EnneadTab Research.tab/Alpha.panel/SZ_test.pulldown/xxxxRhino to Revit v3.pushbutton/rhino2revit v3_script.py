
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script



__doc__ = "try to convert rhino shape"
__title__ = "Rhino2Revit legacy"

output = script.get_output()
output.self_destruct(60)

if revit.doc.IsFamilyDocument == False:
    forms.alert("It needs to be a family document environment.\nIn-place family in project is not accepted.", exitscript=True)


forms.alert( "Pick your Rhino or SAT file in the next window.")
source_file = forms.pick_file(file_ext = "*")


"""
print(source_file)

import_option = DB.SATImportOptions()
print(import_option.GetLayerSelection())
print(import_option.ColorMode)
print(DB.ShapeImporter.IsServiceAvailable())
import_option.VisibleLayersOnly = True
print(import_option.VisibleLayersOnly)

"""
with revit.Transaction("Rhino2Revit"):
    converted_els = []
    geos =  DB.ShapeImporter().Convert(revit.doc, source_file)
    for geo in geos:
        converted_els.append(DB.FreeFormElement.Create(revit.doc, geo))

for x in converted_els:
    print(x)




'''
 delete raw input, promt to ask for subcatefgory, select from list, if not availble, promt to make and assign.    if possible, read rhino 3dm layer
'''
