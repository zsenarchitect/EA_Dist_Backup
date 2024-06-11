from pyrevit import forms
from pyrevit.framework import List
from pyrevit import revit, DB, UI
from pyrevit import script
import pickle

__title__ = "Align Tags_H"
__doc__ = 'Align multiple tags horizontally after picking the ref tag for head position and elbow position. The selection is pre-filtered to tags so you can over-select beforehand.'
direction = "H"

#########lines below should be the same for both code##########

def print_list(list):#for debug
    for item in list:
        print(item)

def get_all_available_tags():
    all_independent_tags = \
        DB.FilteredElementCollector(revit.doc, revit.active_view.Id)\
          .OfClass(DB.IndependentTag)\
          .WhereElementIsNotElementType()\
          .ToElements()#use view.ViewId not view.id for filterelementcollector argument

    all_spatial_el_tags = \
        DB.FilteredElementCollector(revit.doc, revit.active_view.Id)\
          .OfClass(DB.SpatialElementTag)\
          .WhereElementIsNotElementType()\
          .ToElements()

    available_tags = []
    available_tags.extend(all_independent_tags)
    available_tags.extend(all_spatial_el_tags)
    return available_tags

def test_elbow_straight(tag):
    #get archor position and elbow location, if thwo are same then it is straight line.
    if tag.HasLeader == False:
        return False
    if tag.HasElbow:
        return False
    else:
        return True


def find_middle_value_index(list):#def find middle value from list
	list.sort()#sort list
	mid_i = int(len(list)/2)#return middle value
	return mid_i

def move_to_target_in_view(location,target_pt):
    if direction == "V":
        screen_vector = revit.active_view.UpDirection #!!!!this is great! use this!!!!!
    elif direction == "H":
        screen_vector = revit.active_view.RightDirection
    #print "this is unit x direction: {}".format(unit_x)
    pt_line = DB.Line.CreateUnbound(location, screen_vector)
    ped_pt = pt_line.Project(target_pt)#pependicular point with the project unbound line
    return ped_pt.XYZPoint


def get_ref_tag_id():
    datafile = script.get_document_data_file("SelList", "pym")
    f = open(datafile, 'r')
    id_as_string  = pickle.load(f)

    f.close()
    id_as_id = DB.ElementId(int(id_as_string))
    return id_as_id

def align(elements):
    '''
    for idx, el in enumerate(elements):
        ref_tag_index = 0#protection so this value exist even when all tags has no leaders
        if el.HasLeader and el.HasElbow:
            ref_tag_index = idx
    '''





    for el in elements:
        temp_location = move_to_target_in_view(el.TagHeadPosition, ref_tag.TagHeadPosition)
        try:
            el.TagHeadPosition = temp_location
        except:
            print("Tag with no leaders cannot have tag head outside the host. Will try to add leader for you.")
            el.HasLeader = True
            el.TagHeadPosition = temp_location


        try:
            temp_location = move_to_target_in_view(el.LeaderElbow,ref_tag.LeaderElbow)
            el.LeaderElbow = temp_location
        except:
            if test_elbow_straight(el):
                #print "Elbow is straight, no elbow point for {}. The blbow move will be ignored".format(el.Id)
                pass
            elif el.HasLeader == False:
                #print "No leader for this element:{}. Leader moves will be ignored.".format(el.Id)
                pass
            else:
                #print "Elbow move fails for this element:{}".format(el.Id)
                pass


#----------------actual code below-------------

active_view_type = revit.active_view.GetType()
if str(active_view_type) == "Autodesk.Revit.DB.ViewSheet":
	forms.alert("CURRENT ACTIVE VIEW IS A SHEET.")
	script.exit()

selection = revit.get_selection()#collect selected elements.
if not selection:#make sure selection is not empty
    selection = revit.pick_elements()


#all_tags = get_all_available_tags()

#print_list(all_tags)
main_tags = []

for el in selection:
    #print el #,el.GetType()
    #print el.Category.Name


    if "Tags" in el.Category.Name:
        main_tags.append(el)
    '''
    #print str(el.Parameter[DB.BuiltInParameter.]
    for tag in all_tags:
        if el.Id == tag.Id:

            main_tags.append(el)
    '''


try:
    ref_tag = revit.doc.GetElement(get_ref_tag_id())

except:
    forms.alert("Please pick ref tag first.\nThis action is cancelled.")
    script.exit()

with revit.Transaction("Align Tags"):

    align(main_tags)

'''
output = script.get_output()
output.print_md("# This window will close itself in 15 seconds.\nYou can continue working on the project.")
output.self_destruct(15)
'''
