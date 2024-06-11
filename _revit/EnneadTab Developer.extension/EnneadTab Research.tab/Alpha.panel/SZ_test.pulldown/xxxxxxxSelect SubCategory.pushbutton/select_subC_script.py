__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Set\nSubCategory"

from pyrevit import DB, script, revit, forms
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
selection = revit.get_selection()

options = ["Generic Models", "Curtain Panels"]
parent_category = forms.SelectFromList.show(options, title = "Confirm your current family category", button_name='Select C',multiselect  = False)


subCs = find_c(parent_category).SubCategories
subC_names = []
for item in subCs:
    subC_names.append(item.Name)

selected_name = user_select(subC_names)
if "Create New" in selected_name:
    print("will create new")
    new_subc_name = forms.ask_for_string( default = "New SubC Name", prompt = "Name the new sub-c that will be used", title = "What is it called?")

    with revit.Transaction("convert to sub-c newly created"):
        new_subc = revit.doc.Settings.Categories.NewSubcategory(find_c(parent_category), new_subc_name)
        for element in selection:
            element.Subcategory = new_subc

elif "Use Rhino" in selected_name:
    print("will take rhino name and create new")
elif "Use Parent" in selected_name:
    print("will use parent name and do nothing")
else:
    print("will use selected sub c")
    with revit.Transaction("convert to sub-c selected"):
        for element in selection:
            element.Subcategory = find_subc(selected_name)
