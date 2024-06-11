__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Set Grid Head Symbol"

from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script

output = script.get_output()
output.self_destruct(30)

all_grid_types = \
    DB.FilteredElementCollector(revit.doc)\
      .OfClass(DB.GridType)\
      .ToElements()

print("----------111111111----------------------")
for item in all_grid_types:
    print(item)

print("\n----------2222222---------")
for x in all_grid_types[0].Parameters:
    print(x.Definition.Name)

print("\n---------3333333----------")
print(all_grid_types[0].LookupParameter("Type Name").AsString())
print(all_grid_types[0].LookupParameter("Symbol").AsElementId())

for i in range(len(all_grid_types)):
    print(all_grid_types[i].LookupParameter("Type Name").AsString())

    symbol_id = all_grid_types[i].LookupParameter("Symbol").AsElementId()
    print(revit.doc.GetElement(symbol_id).FamilyName)
