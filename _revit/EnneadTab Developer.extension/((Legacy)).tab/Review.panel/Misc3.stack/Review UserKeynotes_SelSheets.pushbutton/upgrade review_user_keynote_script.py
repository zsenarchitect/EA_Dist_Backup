from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__title__ = "Review\nUser Keynotes"
__doc__ = 'User Keynotes do not update with components, and sometimes they are left behind because they look exactly like a normal tag. This tool allows you to select all User Keynote elements in the model and displays a preview with clickable links.'


sel_sheets = forms.select_sheets(title='Select Sheets That You Want To Find User Keynotes.')

output = script.get_output()

def get_user_keynotes_in_sheets(sheets):
    user_keynotes_tags = []
    for sheet in sheets:
        viewports = sheet.GetAllViewports()
        for viewport in viewports:
            view_id = revit.doc.GetElement(viewport).ViewId
            keynotes_tags = DB.FilteredElementCollector(revit.doc,view_id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()
            for tag in keynotes_tags:
                if tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User":
                    user_keynotes_tags.append(tag)
    return user_keynotes_tags

"""
all_views = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()#get all views
def get_view_that_contains(current_tag):
    for view in all_views:#get all elements "els" in each view part 1/2
        print(view,view.Id,view.viewId)
        els = DB.FilteredElementCollector(revit.doc,view.viewId).WhereElementIsNotElementType().ToElements()#get all elements "els" in each view part 2/2
        if current_tag in els:#find if tag is in "els"
            return [view.Name,view.Id]#true-->trturn  view.id
    #if the view is on sheet, true--->get sheet number and sheet.id ,false----> wirte "No Sheet"
"""


"""
user_keynotes_tags = []
for tag in keynotes_tags:
    if tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User":
        user_keynotes_tags.append(tag)
"""
seperation = "---------------"

if sel_sheets:
    if len(sel_sheets) > 0:
        user_keynotes_tags = get_user_keynotes_in_sheets(sel_sheets)
    else:
        forms.alert("No Sheet Slected. \nCancelled.")
        script.exit()
else:
    forms.alert("Cancelled")
    script.exit()


if len(user_keynotes_tags)>0:
    for idx, tag in enumerate(user_keynotes_tags):
        id = tag.Id
        key_value = "Key Value = " + tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
        key_text = "Keynote Text = " + tag.Parameter[DB.BuiltInParameter.KEYNOTE_TEXT].AsString()
        parent_view = tag.OwnerViewId
        print ("{}: tag Id = {}-->{}".format(idx+1,tag.Id,output.linkify(tag.Id, title = "Go To Tag")))
        print(key_value)
        print(key_text)
        print("Found in this view: {} :-->{}".format(revit.doc.GetElement(parent_view).Name,output.linkify(parent_view, title = "Go To View")))
        print(seperation)


print('{0} USER KEYNOTE(S) FOUND IN SELECTED SHEETS.'.format(len(user_keynotes_tags)))

#print "Select {} Above.".format(output.linkify(user_keynotes_tags.element_ids, title = "All Tags"))
