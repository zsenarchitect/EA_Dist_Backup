
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
	def __init__(self, view_id):
		view = revit.doc.GetElement(view_id)
		self.view_name = view.Name
		self.id = view_id
		self.line_count = 1
		self.critical_level_text = "Ok"
		self.critical_level_value = 0
		self.emoji = ':OK_hand:'
		self.creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc,self.id).Creator
		#print "initiate: {}".format(self.view_name)

	def update_data(self):
		self.line_count += 1
		if self.line_count > 50:
			self.critical_level_text = "Bad"
			self.critical_level_value = 1
			self.emoji = ':broken_heart:'
			#self.emoji = ':fire:'

		if self.line_count > 200:
			self.critical_level_text = "Critical"
			self.critical_level_value = 2
			#self.emoji = ':fire:'
			self.emoji = ':radioactive:'
		#print "Update: {}, lines = {}".format(self.view_name,self.line_count)




def user_select(list_raw):

	#convert to a slect list with {line num}. Critical level try to make as emoji indecater at front."thinking_face"?
	select_list = []
	for item in list_raw:
		## DEBUG: print item.critical_level
		if item.critical_level_text != "Ok":
			select_list.append("{" + item.critical_level_text + "}-[" + str(item.line_count) + "]: " + item.view_name)
		else:
			select_list.append("[" + str(item.line_count) + "]: " + item.view_name)
	#let user select
	selected_raw = forms.SelectFromList.show(select_list, title = "Select the views you want to expand.", button_name='Select views',multiselect  = True)

	if not selected_raw:
		script.exit()


	#break down the selection
	#view_item_collection.clear()
	#view_item_collection.append(abc)
	select_list = []
	for item in selected_raw:
		try:
			select_list.append(item.split(": ")[-1])
		except:
			select_list.append(item)

	return select_list



def final_print():
	for item in view_item_collection:
		if item.view_name in view_item_collection_selected:
			print("~~~~~")

			print("View '{}' has {} lines.". format(item.view_name, item.line_count))

			print("This view was created by {}".format(item.creator))
			if item.critical_level_text != "":
				print("{} Its condition is {}.".format(item.emoji, item.critical_level_text))

			print("{}".format(output.linkify(item.id, title = "Go To View")))


def final_print_table():
	table_data = []
	for item in view_item_collection:
		if item.view_name in view_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.view_name, item.line_count, output.linkify(item.id, title = "Go To View"), item.creator]
			table_data.append(temp_list)



	output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link", "View Creator"],formats=['', '{}', '{} Lines', '{}'])







###############  main code below  ##############
if __name__ == '__main__':
		
	#get all the lines
	all_lines = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()

	#make a view_collection list to hold all the view item
	view_item_collection = []
	unique_view = []

	global_counter = 0
	limit = len(all_lines)
	#limit = 400
	pb_step =  limit/50
	forms.alert("Found {} lines instance in the project.\nReady to shortlist, this will take a few seconds.".format(len(all_lines)))

	with forms.ProgressBar(title = "Counting lines, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
	#keep only detail lines, and initiate the class collection.
		for line in all_lines:
			if line.CurveElementType.ToString() == "DetailCurve":
				view_id = line.OwnerViewId

				if view_id not in unique_view:
					view_item_collection.append(view_item(view_id))
					unique_view.append(view_id)
				else:
					for item in view_item_collection:
						if item.id == view_id:
							item.update_data()
							break


			global_counter += 1
			if global_counter > limit:
				break

			if pb.cancelled:
				script.exit()
			pb.update_progress(global_counter, limit)



	#sort the view_collection list by line count values
	view_item_collection.sort(key = lambda x: x.line_count, reverse = True)

	view_item_collection_selected = user_select(view_item_collection)

	final_print()

	output.print_md("#Same content below, but in table chart.")

	final_print_table()
