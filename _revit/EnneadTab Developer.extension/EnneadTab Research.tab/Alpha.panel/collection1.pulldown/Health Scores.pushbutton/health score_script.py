#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
import random
import os



__title__ = "Run Health Score`"
__doc__ = 'Feedback a score chart for model health. All score proportiontal to file size. First time running per session will pop up warning, ignore that and re-run, it will work.'

output = script.get_output()
output.self_destruct(2)
def convert_score(input_x,sample_value_for_200MB, threshold):
	ideal_value =  (float(doc_size) * sample_value_for_200MB / 200)

	print("value {} is 100 points, value {} is 0 points". format(ideal_value, ideal_value + threshold))
	delta = float(input_x) - float(ideal_value)
	if delta < 0:
		return 100# perfect sore
	elif delta > threshold: # there are x more error than in ideal situation, no points given
		return 0
	else:
		a = -100 / (threshold * threshold)
		score =  100 + (a * delta *delta)
		return int(score)

def get_score_reference_plane():
	rp_list = DB.FilteredElementCollector(revit.doc).OfClass(DB.ReferencePlane).WhereElementIsNotElementType().ToElements()
	counter = 0
	for rp in rp_list:
		if rp.Name == False:
			counter += 1
	print("there are {} unnamed Reference Plane.".format(counter))

	sample_value_for_200MB = 1
	threshold = 5.0#if you have 50+ error more than ideal error
	return convert_score(counter , sample_value_for_200MB, threshold)


def get_detail_group_content_info(group_instance):
	content = group_instance.GetMemberIds()


	lines_count = 0
	textnotes_count = 0
	dimension_count = 0
	other_count = 0
	detailitem_count = 0
	generic_anno_count = 0
	sketch_count = 0
	constraint_count = 0
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
		elif item.Category.Name == "Constraints":
			constraint_count += 1
		else:
			print(item.Category.Name)
			other_count += 1


	print("#Detail Group: '{}' has {} elements inside.".format(group_instance.Name,len(content)-sketch_count))
	print("It has {} lines, {} textnotes, {} dimensions, {} detail items, {} generic annotation, {} constriants, {} others.".format(lines_count, textnotes_count, dimension_count, detailitem_count, generic_anno_count, constraint_count, other_count))
	if lines_count < 20 and textnotes_count < 10 and dimension_count < 5 and detailitem_count < 5 and generic_anno_count < 5:
		pass
	else:
		print ("Too many elements inside, consider using detail components.")
	if constraint_count > 0:
		print ("Try to remove constriants in the group.")

class group_dict:
	def __init__(self, group_name, sample_group):
		self.group_name = group_name
		self.count = 1
		self.sample = sample_group

	def new_data(self):
		self.count += 1


def get_score_groups():
	'''
	for each group(detail,model), get group name, total elements count in group, total line count if detail group, ref pan if any, dimension counts if any, textnotes count if any.
	'''

	all_detail_groups = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()
	all_model_groups = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_IOSModelGroups).WhereElementIsNotElementType().ToElements()

	detail_group_types = []
	unique_detail_group_name_list = []
	limit = 500#save test time when debug
	counter = 0
	for group in all_detail_groups:
		counter +=1
		if group.Name not in unique_detail_group_name_list:
			detail_group_types.append(group_dict(group.Name, group))
			unique_detail_group_name_list.append(group.Name)
		else:
			for item in detail_group_types:
				if item.group_name == group.Name:
					item.new_data()

		if counter > limit:
			break

	for group in detail_group_types:
		get_detail_group_content_info(group.sample)
		print("This group is placed {} time(s).".format(group.count))
		print("\n-----")
	print("$$$$$$$$$$$$$")

	'''
	print(all_detail_groups_types)
	counter = 0
	for group_type in all_detail_groups_types:
		counter += 1
		group_instances = group_type.Groups
		get_detail_group_content_info(group_instances[0])

		if counter > limit:
			break
	'''

	return 50

def get_score_CAD():
	dwgs_list = DB.FilteredElementCollector(revit.doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType().ToElements()
	dwg_link_num = 0
	dwg_import_num = 0
	for dwg in dwgs_list:
		if dwg.IsLinked:
			dwg_link_num += 1
		else:
			dwg_import_num += 1
	print("there are {} linked dwgs and {} impoted dwgs.".format(dwg_link_num,dwg_import_num))

	sample_value_for_200MB = 1
	threshold = 5.0#if you have 50+ error more than ideal error
	return convert_score(dwg_import_num , sample_value_for_200MB, threshold)

def get_scores_warning():
	warnings = revit.doc.GetWarnings()
	num_of_warning = len(warnings)
	print("there are {} warning in the project.".format(num_of_warning))

	'''
	to-do: make a critical warning list and checke how much percetage warning is critical among all warning. Show as Donut chart maybe?
	'''

	sample_value_for_200MB = 1
	threshold = 70.0#if you have 50+ error more than ideal error
	return convert_score(num_of_warning, sample_value_for_200MB, threshold)


def draw_chart():
    chart = output.make_radar_chart()
    chart.options.title = {"display":True, "text":"Sample Health Check. Future Feature. All score proportional to file size. \nWork In Progress", "fontSize":24}
    chart.data.labels = ["Error Num", "too many CAD imports?", "too many unnamed ref plane?","too many In place models?", "Category 5", "Category 6"]

    set_ref_1 = chart.data.new_dataset(".")
    set_ref_1.data = [100, 100, 100, 100, 100, 100]
    set_ref_1.backgroundColor = ["#fcd8f0"]
    set_ref_1.fill = False

    set_ref_2 = chart.data.new_dataset(".")
    set_ref_2.data = [0, 0, 0, 0, 0, 0]
    set_ref_2.backgroundColor = ["#fcd8f0"]
    set_ref_2.fill = False

    set_proj = chart.data.new_dataset(".")
    set_proj.data = [score_warnings,score_cad,score_ref_plane,score_groups,58,70]
	#fill_list(set_proj.data,len(chart.data.labels))
    set_proj.backgroundColor = ["rgba(180,244,230,0.3)"]
    set_proj.borderColor = ["rbga(130,175,165,1)"]
    set_proj.lineTension = 0 #0 = straight line, 1 = panckae,3 = curve
    set_proj.opacity = 50

    chart.draw()
    """
    for item in range(len(set_good)):
        set_good.backgroundColor.append(coreutils.random_hex_color())
    """

seperation_big = "#######################################################"
#-------------main code below-------------

doc_size = forms.ask_for_string(default = "500", prompt = "Typein the file size in MB", title = "How big is your file in MB")


print("EA note: first time running on every session will popup dialog window saying something is not working, that message is normal and wont show again on following run in the session.")


'''
doc_path = DB.BasicFileInfo.CentralPath.AsString()
print(doc_path)
doc_size = os.path.getsize(doc_path)
print(doc_size)
'''

output = script.get_output()
output.self_destruct(240)#close this window in 240 secounds

output.print_md( "**doc_size** = {} MB".format(doc_size))

'''
to-do:insert time date when this script is run
question: make it autorun at startup, triggerd by what document opening event.
'''



print(seperation_big)
score_warnings = get_scores_warning()
output.print_md( "# #1 Category: warnings numbers = {} points".format(score_warnings))

print(seperation_big)
score_cad = get_score_CAD()
output.print_md( "# #2 Catergory: Import CAD numerb = {} points".format(score_cad))

print(seperation_big)
score_ref_plane = get_score_reference_plane()
output.print_md( "# #3 Category: unnamed ref planes = {} points".format(score_ref_plane))

'''
sz working: check the usgae count for groups, detail and model, in-use or not-in-use. Return a score for how well the file is performing in the radar chart. Also print top 5 group with outstanding element counts with click-link.
Also suggest user to use group tracker toll(not yet made) to get full review summery.
'''
print(seperation_big)
output.freeze()
score_groups = get_score_groups()
output.print_md( "# #4 Category: Detail/Model Groups = {} points".format(score_groups))
output.unfreeze()

'''
to-do: use donut cahrt to show the percentage of, for views that are  on sheets, views that has no template
'''

'''
to-do: count how many elements are using local graphic overiride. Suggest to use filter, template, material etc
'''


'''
to-do:check detail line usage count by views. need to check in group or not. Return a score for how well the file is doing in the radar chart. Also print  top 5 views with click-link with most count.
Also suggest user to use detail item tools(not yet made) to get full review of the summery.
'''



'''
to-do: find the 5 biggest family, is the any size is bigger than x, then rise as count to the score.
'''


'''
to-do: check the numer of elements in each workset. If there is one workset  with less than x items, maybe it should be merged into others.
'''


'''
another tool for catching result: list elements count by category for a selected workset, for instance, if i see 23 wall elements in shared level grid workset, that means action needed. It can also combine that temopory isolate elements by workset in current view.
'''


draw_chart()

'''
IDEA: make a ENNEAD QAQC annotation family that take text as para and place it at the starting screen. This tool will find this element and update the display test in there. As well as color block if stateent
'''



#output.open_url("https://knowledge.autodesk.com/support/revit-products/troubleshooting/caas/CloudHelp/cloudhelp/2019/ENU/Revit-Troubleshooting/files/GUID-F0945713-4389-4F8E-B5DB-DCE03A8C1ADF-htm.html")
