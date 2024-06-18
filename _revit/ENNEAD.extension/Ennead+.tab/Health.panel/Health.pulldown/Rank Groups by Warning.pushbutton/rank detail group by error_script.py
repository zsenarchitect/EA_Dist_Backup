#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
output = script.get_output()

__title__ = "Rank Detail Groups\nBy Warnings"
__doc__ = 'Exam detail informationabout groups.'

"""
note to self, this need overhaul to process the critical level text display and print
"""

def get_detail_group_content_info(group_instance, print_output):
	content = group_instance.GetMemberIds()
	lines_count = 0
	textnotes_count = 0
	dimension_count = 0
	other_count = 0
	detailitem_count = 0
	generic_anno_count = 0
	sketch_count = 0
	constraint_count = 0
	nest_group_count = 0
	insulation_count = 0

	for item_id in content:
		item = revit.doc.GetElement(item_id)

		try:
			item.Category.Name
		except:
			continue

		if item.Category.Name == "Lines":
			lines_count += 1
		elif item.Category.Name == "Text Notes":
			textnotes_count += 1
		elif item.Category.Name == "Dimensions":
			dimension_count += 1
		elif item.Category.Name == "Detail Items":
			detailitem_count += 1
		elif item.Category.Name == "Generic Annotations":
			generic_anno_count += 1
		elif "Sketch" in item.Category.Name:
			sketch_count += 1
		elif "Groups" in item.Category.Name:
			nest_group_count += 1
		elif item.Category.Name == "Constraints":
			constraint_count += 1
		elif item.Category.Name == "Insulation Batting Lines":
			insulation_count += 1
		else:
			if print_output:
				print("unique item: " + item.Category.Name)
			other_count += 1

	is_critical_A = False
	is_critical_B = False
	is_critical_C = False
	is_critical_F = False
	if lines_count > 20 or textnotes_count > 10 or dimension_count > 5 or detailitem_count > 5 or generic_anno_count > 20 :
		is_critical_A = True
	if constraint_count > 0:
		is_critical_B = True
	if nest_group_count > 0:
		is_critical_C = True
	if len(content) <= 3:
		is_critical_F = True


	if not print_output:
		critical_text = ""
		if is_critical_A:
			critical_text += "[A]"
		if is_critical_B:
			critical_text += "[B]"
		if is_critical_C:
			critical_text += "[C]"
		if is_critical_F:
			critical_text += "[F]"

		#if is_critical_A or is_critical_B or is_critical_C:


		return critical_text


	else:#print values when asked to print, used in final stage
		print("#Detail Group: '{}' has {} elements inside.".format(group_instance.Name,len(content)-sketch_count))

		output_text = "It has"
		if lines_count > 0:
			output_text += " {} lines,".format(lines_count)
		if textnotes_count > 0:
			output_text += " {} textnotes,".format(textnotes_count)
		if dimension_count > 0:
			output_text += " {} dimensions,".format(dimension_count)
		if detailitem_count > 0:
			output_text += " {} detail items,".format(detailitem_count)
		if generic_anno_count > 0:
			output_text += " {} generic annotations,".format(generic_anno_count)
		if nest_group_count > 0:
			output_text += " {} nesting groups,".format(nest_group_count)
		if constraint_count > 0:
			output_text += " {} constriants,".format(constraint_count)
		if insulation_count > 0:
			output_text += " {} insulation batting lines,".format(insulation_count)
		if other_count > 0:
			output_text += " {} others,".format(other_count)

		output_text = output_text[:-1] + "."#replace the last "," with "."

		print(output_text)
		#print "It has {} lines, {} textnotes, {} dimensions, {} detail items, {} generic annotation, {} constriants, {} others.".format(lines_count, textnotes_count, dimension_count, detailitem_count, generic_anno_count, constraint_count, other_count)

		if is_critical_A:
			print ("[A]:Too many elements inside, consider using detail components.")
		if is_critical_B:
			print ("[B]:Try to remove constriants in the group.")
		if is_critical_C:
			print ("[C]:Try to remove nesting group/array in the group.")
		if is_critical_F:
			print ("[F]:There are only 3 or less elements in the group.")


class group_dict:
	def __init__(self, group_name, sample_group, critical_level):
		self.group_name = group_name
		self.count = 1
		self.sample = sample_group
		self.critical_level = critical_level
		self.over_used = False
		self.under_used = True

	def new_data(self):
		self.count += 1
		if "E" not in self.critical_level:
			self.under_used = False
			self.critical_level += "[E]"
		if self.count > 5 and "D" not in self.critical_level:#placed more than 5 times
			self.critical_level += "[D]"
			self.over_used = True


def get_group_type_list(groups_raw):

	detail_group_types = []
	unique_detail_group_name_list = []
	limit = len(groups_raw)
	#limit = 50#save test time when debug
	counter = 0
	pb_step =  limit/10
	with forms.ProgressBar(title = "Making Type List, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
		for group in groups_raw:
			counter +=1
			if group.Name not in unique_detail_group_name_list:
				critical_text = get_detail_group_content_info(group, False)

				detail_group_types.append(group_dict(group.Name, group, critical_text))
				unique_detail_group_name_list.append(group.Name)
			else:
				for item in detail_group_types:
					if item.group_name == group.Name:
						item.new_data()

			if counter > limit:
				break

			if pb.cancelled:
				script.exit()
			pb.update_progress(counter, limit)

	#try to sort the collection of sample groups:
	#print detail_group_types
	detail_group_types.sort(key = lambda x: len(x.critical_level), reverse = True)
	return detail_group_types


def final_print(group_type):
	if group_type.critical_level:
		print("{Critical}-->" + group_type.critical_level)
	get_detail_group_content_info(group_type.sample, True)
	print("This group is placed {} time(s).".format(group_type.count))
	if group_type.over_used:
		print("[D]:This groups is used too many times and it is slowing down the performance. Try to break down to smaller detail components.")
	if group_type.under_used:
		print("[E]:This groups is only used once. Please evaluate if we need to keep this.")
	print("{}".format(output.linkify(group_type.sample.Id, title = "Go To Sample Group")))
	print("\n-----")






#-------------main code below-------------
if __name__== "__main__":

	all_detail_groups = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()

	forms.alert( "Found {} detail group instance.\nReady to shortlist, this will take a few seconds.".format(len(all_detail_groups)))
	select_list = []

	type_list = get_group_type_list(all_detail_groups)
	for item in type_list:
		## DEBUG: print item.critical_level
		if item.critical_level != "":
			select_list.append("{Critical}-" + item.critical_level + ": " + item.group_name)
		else:
			select_list.append(item.group_name)

	selected_groups_raw = forms.SelectFromList.show(select_list, title = "Select the groups you want to expand.", button_name='Select Groups',multiselect  = True)

	if not selected_groups_raw:
		script.exit()

	selected_type_name = []
	for item in selected_groups_raw:
		try:
			selected_type_name.append(item.split(": ")[-1])
		except:
			selected_type_name.append(item)

	output = script.get_output()
	output.freeze()
	for type in type_list:
		if type.group_name in selected_type_name:
			final_print(type)
	output.unfreeze()
