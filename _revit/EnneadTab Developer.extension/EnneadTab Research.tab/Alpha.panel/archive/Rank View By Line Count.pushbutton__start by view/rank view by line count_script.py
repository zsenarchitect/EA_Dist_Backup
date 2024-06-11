
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
output = script.get_output()

__title__ = "Rank Views\nBy Line Count"
__doc__ = 'show the view with most detail lines first, .'


def get_line_count(view):
	try:
		lines = DB.FilteredElementCollector(revit.doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
	except:
		lines = DB.FilteredElementCollector(revit.doc, view.ViewId).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
	count = 0
	for line in lines:
		if line.CurveElementType.ToString() == "DetailCurve":
			count += 1
	return count

class view_item():
	def __init__(self, view, line_count):
		self.view_name = view.Name
		self.id = view
		self.line_count = line_count
		if self.line_count > 50:
			self.critical_level = "Critical"
		else:
			self.critical_level = ""



###############  main code below  ##############

#get all the views
all_views = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()


#make a view_collection list to hold all the view item
view_item_collection = []

#for each view, get the line count
limit = len(all_views)
#limit = 40#save tim e when debug
counter  = 0
pb_step =  limit/10
with forms.ProgressBar(title = "Counting lines, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
	for view in all_views:
		if view.IsTemplate or view.ViewType == "ThreeD":#do not count template or 3d view
			continue

		'''
		print("~~~~~")
		print(view.Name)
		print(view.IsTemplate)
		print(view.ViewType)
		'''
		line_count = get_line_count(view)
		#print line_count
		#initiate a class for that view, that keep view id, line count,critical_level then append to a view_item_collection list
		#view_item_collection.append(view_item(view, line_count))

		counter +=1
		if counter > limit:
			break

		if pb.cancelled:
			script.exit()
		pb.update_progress(counter, limit)



#sort the view_collection list by line count values
#view_item_collection.sort()

#convert to a slect list with {line num}. Critical level try to make as emoji indecater at front."thinking_face"?

#let user select

#break down the selection
#view_item_collection.clear()
#view_item_collection.append(xxx)

#output info data for those selected Views as a table. It show view name, line count, clickable

#output a summery
