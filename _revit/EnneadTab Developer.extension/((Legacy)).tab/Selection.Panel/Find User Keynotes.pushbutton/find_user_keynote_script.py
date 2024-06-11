from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script

__title__ = "Select User Keynotes\nIn Current View"
__doc__ = 'Selects all User Keynote elements in the current view. \nFor clickable list, try -Review User Keynotes-.'

active_view_type = str(revit.active_view.GetType())
#print active_view_type # to debug
if active_view_type not in ["Autodesk.Revit.DB.View","Autodesk.Revit.DB.View3D","Autodesk.Revit.DB.ViewPlan","Autodesk.Revit.DB.ViewSection"]:

	forms.alert("Current Active View Is A {} ViewType That Cannot Have Tags.\nAction Will Be Cancelled.".format(active_view_type.replace("Autodesk.Revit.DB.","")))
	script.exit()

keynotes = DB.FilteredElementCollector(revit.doc,revit.active_view.Id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()

selSet_Ids = []



for el in keynotes:
    
    #if str(el.GetParameters("Key Source")) == "User":
    if el.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User":
        selSet_Ids.append(el.Id)
        #print el.Id
        #print "Key Value = " + el.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
        #print "Keynote Text = " + el.Parameter[DB.BuiltInParameter.KEYNOTE_TEXT].AsString()
        #print "----------------"



#print '{0} USER KEYNOTE(S) SELECTED IN THE CURRENT VIEW.'.format(len(selSet_Ids))
forms.alert('{0} USER KEYNOTE(S) SELECTED IN THE CURRENT VIEW.'.format(len(selSet_Ids)))

revit.get_selection().set_to(selSet_Ids)


