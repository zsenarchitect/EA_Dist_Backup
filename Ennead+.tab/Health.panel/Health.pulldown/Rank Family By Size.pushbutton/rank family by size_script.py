
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
import os.path as OP
import math
output = script.get_output()

__title__ = "Rank Family\nBy Size"
__doc__ = 'show the family with biggest size, if file path can be Found.'

#print revit
#print revit.doc


def convert_size(size_bytes):
	if size_bytes == -1:
		return "N/A"
	size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	size = round(size_bytes / p, 2)
	return "{}{}".format(size, size_unit[i])


def print_para(element):
	print '------'
	for para in element.Parameters:
		print "{}--->{}".format(para.Definition.Name, para.AsValueString())
	print "-----------\n\n"



class family_item():
	def __init__(self, family):

		self.family_name = family.Name
		self.critical_level_text = "Ok"
		self.critical_level_value = 0
		self.emoji = ':OK_hand:'
		self.family_size_raw = 0
		self.creator = "N/A"
		self.last_editor = "N/A"


		family_doc = None
		if family.IsEditable:
			family_doc = revit.doc.EditFamily(family)
			family_path = family_doc.PathName
			self.creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, family.Id).Creator
			self.last_editor = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc, family.Id).LastChangedBy

		try:
			self.family_size_raw = int(OP.getsize(family_path))
		except:
			self.family_size_raw = -1

		self.family_size_text = convert_size(self.family_size_raw)


		if self.family_size_raw > 1024 * 1000:#bigger than 1mb
			self.critical_level_text = "Bad"
			self.critical_level_value = 1
			self.emoji = ':broken_heart:'


		if self.family_size_raw > 3 * 1024 * 1000:#bigger than 3Mb
			self.critical_level_text = "Critical"
			self.critical_level_value = 2

			self.emoji = ':radioactive:'

		self.note_InPlace = False
		self.note_UserCreated = False
		if family.IsInPlace:
			self.note_InPlace = True
		if family.IsUserCreated:
			self.note_UserCreated = True


		#print_para(family)
		#print family.LookupParameter("Workset").AsValueString()
		try:
			self.category = family.LookupParameter("Workset").AsValueString().split(": ")[1][:-1]#the last [:-1] is to remove the last space in the string
		except:
			self.category = "N/A"
		#print self.category


		if family_doc:
			family_doc.Close(False)

def user_select(list_raw):

	select_list = []
	for item in list_raw:

		if item.critical_level_text != "Ok":
			select_list.append("{" + item.critical_level_text + "}-[" + item.family_size_text + "][" + item.category + "]: " + item.family_name)
		else:
			select_list.append("[" + item.family_size_text + "]["+ item.category + "]: " + item.family_name)
	#let user select
	selected_raw = forms.SelectFromList.show(select_list, title = "Select the families you want to expand.", button_name='Select Families',multiselect  = True)

	if not selected_raw:
		script.exit()


	#break down the selection
	#view_item_collection.clear()
	#view_item_collection.append(xxx)
	select_list = []
	for item in selected_raw:
		try:
			select_list.append(item.split(": ")[-1])
		except:
			select_list.append(item)

	return select_list



def final_print():
	for item in family_item_collection:
		if item.family_name in family_item_collection_selected:
			print "~~~~~"

			if item.family_size_text != "N/A":
				print "Family '{}' takes {} Kb.". format(item.family_name, item.family_size_text)
			else:
				print "Family '{}' size info not available, usually due to being a system family, or a in-place family, or the user saved the family to a local folder.".format(item.family_name)


			if item.category == "N/A":
				print "Category info not available. Ask your ACE for assistant."
			else:
				print "It is {} category. ". format(item.category)

			if item.note_InPlace :
				print "It is a In-Place family."

			if item.note_UserCreated :
				print "It was created by {}". format(item.creator)
				print "It was last edited by {}. ". format( item.last_editor)

			if item.critical_level_text != "":
				print "{} Its size condition is {}.".format(item.emoji, item.critical_level_text)

			#print "{}".format(output.linkify(item.id, title = "Go To View"))


def final_print_table():
	table_data = []
	for item in family_item_collection:
		if item.family_name in family_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.family_name, item.family_size, output.linkify(item.sample, title = "Go To View")]
			table_data.append(temp_list)



	output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])







###############  main code below  ##############
if __name__== "__main__":
    

	#get all the family
	all_families = DB.FilteredElementCollector(revit.doc).OfClass(DB.Family).ToElements()

	#make a family_collection list to hold all the family item
	family_item_collection = []

	'''
	#pick category first
	for item in revit.doc.Settings.Categories:
		print item.Name
	'''

	global_counter = 0
	limit = len(all_families)
	#limit = 200
	pb_step =  limit/400
	forms.alert("Found {} families in the project.\nReady to shortlist, this will take a few seconds.\n\nIf encounter Revit asking to remove constraint, it is safe to remove and will not affect your loaded family in project.".format(len(all_families)))

	with forms.ProgressBar(title = "Checking Families, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
	# initiate the class collection.
		for family in all_families:

			family_item_collection.append(family_item(family))



			global_counter += 1
			if global_counter > limit:
				break

			if pb.cancelled:
				script.exit()
			pb.update_progress(global_counter, limit)



	#sort the family_collection list by size values
	family_item_collection.sort(key = lambda x: x.family_size_raw, reverse = True)

	family_item_collection_selected = user_select(family_item_collection)

	output.freeze()
	final_print()
	output.unfreeze()


	output.print_md("# If a family have been saved outside the Office network, this tool cannot find the directory of that family and cannot get size info correctly.")
	#final_print_table()
