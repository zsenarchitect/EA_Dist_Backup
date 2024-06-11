
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script


__doc__ = "try to convert rhino shape"
__title__ = "test Rhino2Revit Importer"

output = script.get_output()
output.self_destruct(60)


def find_c(category_name):
    for category in revit.doc.Settings.Categories:
        if category.Name == category_name:
            return category

def find_subc(name):
    for item in subCs:
        if item.Name == name:
            return item

def user_select(select_list):
	#let user select
	select_list.append("<Create New SubCategory>")
	select_list.append("<Use Rhino file name as new subC name>")
	select_list.insert(0, "<Use Parent Category>")
	selected = forms.SelectFromList.show(select_list, title = "Select a subcategory from currently available list.", button_name='Select SubC',multiselect  = False)

	if not selected:
		script.exit()
	return selected



###########################################################################



if revit.doc.IsFamilyDocument == False or True:
    forms.alert("It needs to be a family document environment.\nIn-place family in project is not accepted.", exitscript=True)


forms.alert( "Pick your Rhino or SAT file in the next window.")
source_file = forms.pick_file(file_ext = "*")
if not source_file:
    script.exit()


with revit.Transaction("Rhino2Revit"):
    converted_els = []
    geos =  DB.ShapeImporter().Convert(revit.doc, source_file)
    for geo in geos:
        converted_els.append(DB.FreeFormElement.Create(revit.doc, geo))
"""
for x in converted_els:
    print(x)
"""




"""

options = ["Generic Models", "Curtain Panels", "Columns", "Doors", "Furniture", "Mass", "Lighting Fixture", "Parking", "Planting", "Railings", "Site", "Windows"]
#parent_category = forms.SelectFromList.show(options, title = "Confirm your current family category", button_name='Select Category in the current document',multiselect  = False)

parent_category = forms.ask_for_one_item(options, title = "What is your family category?", button_name='Yes, Go',default = options[0], prompt = "Please confirm your current family category.")
subCs = find_c(parent_category).SubCategories

"""

parent_category = revit.doc.OwnerFamily.FamilyCategory
subCs = parent_category.SubCategories


"""
subCs = converted_els[0].Category.SubCategories
"""

subC_names = []
for item in subCs:
    subC_names.append(item.Name)

selected_name = user_select(subC_names)
if "Create New" in selected_name:
    #print "will create new"
    new_subc_name = forms.ask_for_string( default = "New SubC Name", prompt = "Name the new sub-c that will be used", title = "What is it called?")

    with revit.Transaction("Convert to User Created Sub-C"):
        try:
            new_subc = revit.doc.Settings.Categories.NewSubcategory(parent_category, new_subc_name)
        except:
            #maybe there is already this names
            new_subc = find_subc(new_subc_name)

        for element in converted_els:
            element.Subcategory = new_subc

elif "Use Rhino" in selected_name:
    #print "will take rhino name and create new"

    new_subc_name = source_file.split('\\')[-1].split(".")[0]

    with revit.Transaction("Convert to newly created Sub-C using rhino name"):
        try:
            new_subc = revit.doc.Settings.Categories.NewSubcategory(parent_category, new_subc_name)
        except:
            #maybe there is already this names
            new_subc = find_subc(new_subc_name)

        for element in converted_els:
            element.Subcategory = new_subc


elif "Use Parent" in selected_name:
    #print "will use parent name and do nothing"
    pass

else:
    #print "will use selected sub c"
    with revit.Transaction("Convert to Sub-C selected"):
        for element in converted_els:
            element.Subcategory = find_subc(selected_name)
