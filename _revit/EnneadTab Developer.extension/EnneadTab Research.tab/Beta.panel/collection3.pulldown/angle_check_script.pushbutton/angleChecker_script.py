
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
import math



__title__ = "Ortho Checker"
__doc__ = 'XXXXXXXXXXXXXX'


def find_angle(vec1,vec2):
	angle = math.degrees(vec1.AngleTo(vec2))
	telorance = 0.0000000001
	if angle < telorance:
		return 0.0
	elif -telorance < angle - 90 < telorance:
		return 90.0
	elif -telorance < angle - 180 < telorance:
		return 180.0
	else:
		return angle

def find_all_angles_scopbox(scopebox):
	edges = scopebox.Geometry[DB.Options()]
	angle_list = []
	for edge in edges:

		angle_list.append(find_angle(edge.Direction,ref_line.Direction))
	return angle_list


def is_scopebox_ok(angle_list):
	temp = 1
	for angle in angle_list:
		temp *= angle
	if temp == 0:

		return True
	else:
		return False

def find_scopebox_center_z_axis(scopebox):
	box = scopebox.Geometry[DB.Options()].GetBoundingBox()

	center = (box.Max + box.Min) / 2
	#print "center is {}".format(center)
	return DB.Line.CreateBound(center,center.Add(DB.XYZ(0,0,1)))


def try_fix(scopeboxs, mode):
	for scopebox in scopeboxs:
		#print "new scopebox"
		angle_list = find_all_angles_scopbox(scopebox)
		if is_scopebox_ok(angle_list) and mode in  ["default mode A","default mode B"]:
			#print "******Scopebox ok"
			pass
		else:
			#print "####scopebox need rotation"
			#print angle_list

			rotation = min(angle_list)
			#print "rotation is {}".format(rotation)
			axis = find_scopebox_center_z_axis(scopebox)
			if mode == "default mode A":
				DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, -math.radians(rotation))
			if mode == "default mode B":
				DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, math.radians(rotation))
			elif mode == "90 degree mode":
				DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, math.radians(90))
			else:
				print("conditions no exist")

def update_display_text(scopboxs):
	scopeboxs_condition_ready = True
	for scopebox in scopeboxs:
		if is_scopebox_ok(find_all_angles_scopbox(scopebox)) == False:
			scopeboxs_condition_ready = False

	if scopeboxs_condition_ready:
		return  "All scopboxs is aligned in at least one direction.\nDo you want to adjusting orientation by 90 degree?"

	else:
		return  "Not all scopeboxs are ready.\nPlease try oritent option continously."

#################################


selection = list(revit.get_selection())
if not selection:
	forms.alert("Please selection some elements first.")
	script.exit()


for x in selection:
	print(x.GetType(),x,x.Category.Name)
print("****************************")


walls = [x for x in selection if x.Category.Name == "Walls"]
scopeboxs = [x for x in selection if x.Category.Name == "Scope Boxes"]
ref_lines = [x for x in selection if x.Category.Name == "Lines"]

def find_bad_walls(walls):
	for wall in walls:
		wall_direction = wall.Location.Curve.Direction
		angle_to_view = find_angle(wall_direction,ref_vec)
		print(angle_to_view)

		if angle_to_view in [0.0, 90.0, 180.0]:
			print("good wall at angle {}".format(angle_to_view))
		else:
			print("bad wall id = {} at angle {}".format(wall.Id, angle_to_view))


#ref_line = ref_lines[0].GeometryCurve

ref_vec = revit.active_view.RightDirection
print(ref_vec)


if walls:
	find_bad_walls(walls)
