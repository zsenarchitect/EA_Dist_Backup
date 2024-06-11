__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Transfer\nParameter Data"




from pyrevit import forms, revit, DB, script




######## main code below #########

res = forms.alert(options = ["record old para data before renaming para", "set renamed para data thrurecorded memory"], msg = "I want to [     ].")

if "record" in res:
    option = "record"
elif "set" in res:
    option = "set"
else:
    script.exit()


selection = revit.get_selection()

if len(selection) > 1 or "Panel" not in selection[0].Category.Name:
    forms.alert("Please select 1 curtain panel only.")
    script.exit()



selected_element = selection[0]
selected_parameter = forms.select_parameters(selected_element, multiple = False, title = "Old Para name to rememebr before renaming them." if option == "record" else "Renamed para to push in data from memory")
if selected_parameter == None:
        script.exit()

#get_family
family = selected_element.Symbol.Family
print(family.Name)

#select all panels with this family
all_panels = DB.FilteredElementCollector(revit.doc).ByClass(DB.Panel).WhereElementIsNotElementType().ToElements()
panels = []
for panel in all_panels:
    if panel.Symbol.Family == family:
        panels.append()


print(len(panels))

if option == "record":#if to remember para:
    write_data(panels, selected_parameter)#write data to file, element Id + parap type + para data


else:#if to set para by memeory:
    data = read_data(selected_parameter)#wead data and assign para to element
    with revit.Transaction("Set para by memory"):
        set_data(data, panels,selected_parameter)
