
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
output = script.get_output()

__title__ = "Track Ref Planes"
__doc__ = 'show the ref plane info.'



def print_para(element):
	print('------')
	for para in element.Parameters:
		print("{}--->{}".format(para.Definition.Name, para.AsValueString()))
	print("-----------\n\n")



class ref_plane_item():
	def __init__(self, ref_plane):
		#print_para(ref_plane)

		name_text = ref_plane.Name
		if name_text == "Reference Plane":
			self.ref_plane_name = "Unnamed Ref Plane <{}>".format(ref_plane.Id)
		else:
			self.ref_plane_name = ref_plane.Name


		self.sample = ref_plane


		workset_text = ref_plane.LookupParameter("Workset").AsValueString()
		self.workset = workset_text


		#print self.workset

		scope_box_text = ref_plane.LookupParameter("Scope Box").AsValueString()
		if scope_box_text == "<None>":
			self.scope_box = "N/A"
		else:
			self.scope_box = scope_box_text


		subcategory_text = ref_plane.LookupParameter("Subcategory").AsValueString()
		if subcategory_text == "<None>":
			self.subcategory = "N/A"
		else:
			self.subcategory = subcategory_text



		self.critical_level_text = "Ok"
		self.critical_level_value = 0
		self.emoji = ':OK_hand:'

		if name_text == "Unnamed Ref Plane" or self.scope_box == "N/A":
			self.critical_level_text = "Bad"
			self.critical_level_value = 1
			self.emoji = ':broken_heart:'

		if name_text == "Unnamed Ref Plane" and self.scope_box == "N/A":
			self.critical_level_text = "Critical"
			self.critical_level_value = 2
			self.emoji = ':radioactive:'


def user_select(list_raw):

	select_list = []
	for item in list_raw:

		if item.critical_level_text != "Ok":
			select_list.append("{" + item.critical_level_text + "}-[" + item.scope_box + "][" + item.subcategory + "]: " + item.ref_plane_name)
		else:
			select_list.append("[" + item.scope_box + "][" + item.subcategory + "]: " + item.ref_plane_name)
	#let user select
	selected_raw = forms.SelectFromList.show(select_list, title = "Select the ref planes you want to expand.", button_name='Select RPs',multiselect  = True, prompt = "The percentage that will remain afterward.")

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
	for item in ref_plane_item_collection:
		if item.ref_plane_name in ref_plane_item_collection_selected:
			print("~~~~~")

			if item.ref_plane_name == "Unnamed Ref Plane":
				print("{} is in workset:<{}>".format(item.ref_plane_name,item.workset))
			else:
				print("Ref Plane {} is in workset:<{}>".format(item.ref_plane_name,item.workset))
			if "View" in item.workset:
				print("This Ref Plane is view specific.")


			if item.subcategory != "N/A":
				print("It is in {} subcategory.". format(item.subcategory))
			else:
				print("It is not assigned in any subcategory.")

			if item.scope_box != "N/A":
				print("It is in scope box {}.". format(item.scope_box))
			else:
				print("It is not in scope box.")

			print("{} Its health condition is {}.".format(item.emoji, item.critical_level_text))
			print("{}".format(output.linkify(item.sample.Id, title = "Go To RP")))


def final_print_table():
	table_data = []
	for item in ref_plane_item_collection:
		if item.ref_plane_name in ref_plane_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.ref_plane_name, item.ref_plane_size, output.linkify(item.sample, title = "Go To View")]
			table_data.append(temp_list)



	output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])







###############  main code below  ##############
if __name__== "__main__":

	#get all the ref_plane
	all_ref_planes = DB.FilteredElementCollector(revit.doc).OfClass(DB.ReferencePlane).WhereElementIsNotElementType().ToElements()
	all_ref_planes = [x for x in all_ref_planes if not x.LookupParameter("Workset").IsReadOnly]


	#make a ref_plane_collection list to hold all the ref_plane item
	ref_plane_item_collection = []


	global_counter = 0
	limit = len(all_ref_planes)
	#limit = 200
	pb_step =  limit/100
	forms.alert("Found {} reference planes in the project.\nReady to shortlist, this will take a few seconds.".format(len(all_ref_planes)))

	with forms.ProgressBar(title = "Checking Reference Planes, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
	# initiate the class collection.
		for ref_plane in all_ref_planes:
			ref_plane_item_collection.append(ref_plane_item(ref_plane))

			global_counter += 1
			if global_counter > limit:
				break

			if pb.cancelled:
				script.exit()
			pb.update_progress(global_counter, limit)



	#sort the ref_plane_collection list by size values
	ref_plane_item_collection.sort(key = lambda x: x.critical_level_value, reverse = True)

	ref_plane_item_collection_selected = user_select(ref_plane_item_collection)

	output.freeze()
	final_print()
	output.unfreeze()

	#final_print_table()
