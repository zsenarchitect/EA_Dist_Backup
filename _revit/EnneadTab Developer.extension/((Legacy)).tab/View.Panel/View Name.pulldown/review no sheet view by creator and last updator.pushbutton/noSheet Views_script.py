__doc__ = "Find the history behidn who make those no sheet view and ask them what should be deleted"


__title__ = "NoSheet Views History By Creator And Last Editor"

from pyrevit import DB,revit, script, forms



all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

existing_names = [x.Name for x in all_views]
no_sheet_views = []

for view in all_views:
    if view.IsTemplate:
        continue
    if "{3D" in view.Name:
        continue


    sheetnum = view.LookupParameter("Sheet Number").AsString()

    if sheetnum == "---":
        no_sheet_views.append(view)
        #print view.Name

no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)

table_data = []
output = script.get_output()
output.set_title(__title__)

max_value = len(no_sheet_views)
for i, view in enumerate(no_sheet_views):
    view_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, view.Id)

    temp_list = [output.linkify(view.Id, title = view.Name),\
                view.ViewType,\
                view_history.Creator, \
                view_history.Owner, \
                view_history.LastChangedBy]

    table_data.append(temp_list)
    output.update_progress(i + 1, max_value)#progress bar show from 1 to 100 when i is 0 to 99

output.freeze()
output.print_table(table_data=table_data,\
                title="No Sheet View History ",\
                columns=[ "View Name:", "View Type:","Created By:", "Currently Owned By:", "Last Changed By:"])

output.unfreeze()




"""

selected_views = forms.SelectFromList.show(no_sheet_views,
                                multiselect=True,
                                name_attr='Name',
                                title = "Those views are not on sheet",
                                button_name= "Mark them with 'NoSheet-' prefix",
                                filterfunc=lambda x: x.ViewType not in [DB.ViewType.Legend, DB.ViewType.Schedule])

if selected_views == None:
    script.exit()

with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:
        new_name = "NoSheet-" + view.Name
        if new_name in existing_names:
            new_name += "_another"
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(new_name)
"""
