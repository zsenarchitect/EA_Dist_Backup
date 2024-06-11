__doc__ = "Use this tool to find and change the view name \
of views that is not on a sheet.\nThis is helpful \
after reformat the view names from above.\n\n Revit \
user 3D views( those with {} in their name), will \
be ignored by this tool.\n\nSince Revit 2023, project browser \
will display icon for no sheet view, so from this version on there \
will be no 'NoSheet' prefix."


__title__ = "Mark\nNoSheet Views"

from pyrevit import DB,revit, script, forms
import EA_UTILITY
import EnneadTab
output = script.get_output()
output.close_others()
def created_by_who(view):
    view_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, view.Id)
    return view_history.Creator

def enlongate_name_unitl_unique(name):
    while name in existing_names:
        name += "_another"
    return name

all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

existing_names = [x.Name for x in all_views]
no_sheet_views = []

for view in all_views:
    if view.IsTemplate:
        continue
    if  "_from" in view.Name:
        continue
    if "{" in view.Name:
        continue
    if "EnneadTab" in view.Name:
        continue

    sheetnum = view.LookupParameter("Sheet Number").AsString()

    if sheetnum == "---":
        no_sheet_views.append(view)
        #print view.Name

no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)

selected_views = forms.SelectFromList.show(no_sheet_views,
                                multiselect=True,
                                name_attr='Name',
                                title = "Those views are not on sheet",
                                button_name= "Append View Creator Name",
                                filterfunc=lambda x: x.ViewType not in [DB.ViewType.Legend, DB.ViewType.Schedule])
"""
for view in selected_views:
    print(view, view.Name)
"""
if selected_views == None:
    script.exit()



with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:

        if "_from" in view.Name:
            new_name = "{}".format( view.Name)
        else:
            new_name = "{}_from({})".format( view.Name, created_by_who(view))

        print(new_name)
        current_owner = view.LookupParameter("Edited by").AsString()
        if current_owner != "" and current_owner != EA_UTILITY.get_application().Username:
            print("###################skip view owned by " + current_owner)
            continue
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(enlongate_name_unitl_unique(new_name))


    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 100, tool_used = "Mark No Sheet Views", show_toast = True)
