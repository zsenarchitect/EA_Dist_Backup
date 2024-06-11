from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
#from pyrevit import forms

__title__ = "Review All\nUser Keynotes"
__doc__ = 'User Keynotes do not update with component, sometimes it is left behind becasue it looks exactly like a normal tag.\nThis tool allows you to selects all User Keynote elements in the model and display preview and clickable link.\n\nKnown issue: \nCould be overwhelmed with too much tags. I am planing to change it to limit by selected sheets only.'

output = script.get_output()
keynotes_tags = DB.FilteredElementCollector(revit.doc)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()

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



user_keynotes_tags = []
for tag in keynotes_tags:
    if tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User":
        user_keynotes_tags.append(tag)

seperation = "---------------"
if len(user_keynotes_tags)>0:
    for idx, tag in enumerate(user_keynotes_tags):
        id = tag.Id
        key_value = "Key Value = " + tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
        key_text = "Keynote Text = " + tag.Parameter[DB.BuiltInParameter.KEYNOTE_TEXT].AsString()
        #parent_view_info = get_view_that_contains(tag)
        print ("{}: {}".format(idx+1,output.linkify(tag.Id)))
        print(key_value)
        print(key_text)
        #print "Found in this view:{}:{}".format(parent_view_info[0],output.linkify(parent_view_info[1]))
        print(seperation)
        
        
print('{0} USER KEYNOTE(S) FOUND IN CURRENT PROJECT.'.format(len(user_keynotes_tags)))
        
        
        
