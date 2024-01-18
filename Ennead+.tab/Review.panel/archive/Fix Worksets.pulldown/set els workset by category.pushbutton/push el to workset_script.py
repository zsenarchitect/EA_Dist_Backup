__doc__ = "pick category, get all elemetns fro that category, pick workset, make it that"
__title__ = "Set Workset\nBy Category"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28475"
from pyrevit import revit,DB, forms, script
from pyrevit import HOST_APP


"""
keyords to ignore, seperated by ","

try set workset for each element, if failed append a list that shows

element in design options, groups, except warning for elemanet that failed
"""

def get_id_card(element):
    try:
        id_card = "[{}]:[{}]".format(element.Symbol.FamilyName, element.Symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString())
    except:
        id_card = "'{}''".format(element.Id)
    return id_card

def get_element_workset(element):
    return revit.doc.GetWorksetTable().GetWorkset(element.WorksetId)

def set_element_workset(element,workset):
    #print element.GetParameters("Workset")[0]
    try:
        para = element.GetParameters("Workset")[0]
        #print para
        para.Set(workset.Id.IntegerValue)
        """
        para = element.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM]
        para.Set(workset)
        """
        return "OK"
    except:
        print "\n---------------------------------"
        id_card = get_id_card(element)
        ########print element.Symbol.GetPreviewImage(Drawing.Size(200,200))
        #if hasattr(obj, 'attr_name')
        #if isinstance(5, int)
        '''
        if '.dwg' in element.Category.Name and element.ViewSpecific:
            view_id = element.OwnerViewId
            try:#revit 2020 and 2019 use diffrent propety for names
                view_name = revit.doc.GetElement(view_id).ViewName
            except AttributeError:
                view_name = revit.doc.GetElement(view_id).Name

            print "dwg name: {}".format(view_name)
            print ("It is view specific 2D dwg in view '{}' --->{}".format(view_name, script.get_output().linkify(view_id, title = "Go To View")))

            if element.IsHidden(revit.doc.GetElement(view_id)):
                print "It is currently hidden in the view."
            return
        '''
        if element.ViewSpecific:
            print "View Specific item has no user workset.{}".format(script.get_output().linkify(element.Id, title = "Go To Element"))
            return "View Specific"


        if element.GroupId != -1: #-1 means not in group
            try:
                group_name = revit.doc.GetElement(element.GroupId).Name
                print "\nFail to set workset for {0} becasue it is in group '{3}'---> {1}--->{2}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element"),script.get_output().linkify(element.GroupId, title = "Go To Group"), group_name)
                print "This group is currently in workset '{}'".format(get_element_workset(revit.doc.GetElement(element.GroupId)).Name)
            except:
                group_name = "None"



            try:
                #if revit.doc.GetElement(element.GroupId).DesignOption:
                print "The group '{}' is in design option '{}'. You may use 'Go To Group' while that design option is in edit mode.\n\n ".format(group_name, revit.doc.GetElement(element.GroupId).DesignOption.Name)
                return "Group In DesignOption"
            except:#no attribute designoption, just say it is in a group
                return "In Group"
            finally:
                #print ("test" + str(revit.doc.GetElement(element.GroupId).DesignOption))
                pass

        elif element.DesignOption != -1:#-1 means not in design option
            print "The element is in design option '{}'. You may use 'Go To Element' while that design option is in edit mode.\n\n ".format(element.DesignOption.Name)
            return "Element In DesignOption"



        else:
            print "Fail to set workset on {0} ---> {1}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element"))
            return "Unknown"


        print "Contact SenZhang"

def get_all_userworkset():
    all_worksets = []
    all_worksets_raw = DB.FilteredWorksetCollector(revit.doc).ToWorksets()
    for workset in all_worksets_raw:
        if workset.Kind.ToString() == "UserWorkset":
            all_worksets.append(workset)
    return all_worksets

def get_workset_by_name(name):
    for workset in get_all_userworkset():
        if workset.Name == name:
            return workset
def get_all_userworkset_name():
    all_workset_names = []
    all_worksets_raw = DB.FilteredWorksetCollector(revit.doc).ToWorksets()
    for workset in all_worksets_raw:
        if workset.Kind.ToString() == "UserWorkset":
            all_workset_names.append(workset.Name)
    return all_workset_names

def user_select_workset():
    select_list = get_all_userworkset_name()
    selected = forms.SelectFromList.show(select_list, title = "Select a workset they will go to", button_name='Go!',multiselect  = False)
    if not selected:
		script.exit()
    return get_workset_by_name(selected)

def collect_room():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

def collect_furniture():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()

def collect_grids():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

def collect_levels():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

def collect_columns():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()

def collect_structural_columns():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()

def collect_areas():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()

def collect_rm_seperation_lines():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_RoomSeparationLines).WhereElementIsNotElementType().ToElements()

def collect_area_seperation_lines():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_AreaSchemeLines).WhereElementIsNotElementType().ToElements()

def collect_rvt():
    return DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()

def collect_CAD():
    return DB.FilteredElementCollector(revit.doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType().ToElements()

def collect_scopebox():
    temp = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
    return [x for x in temp if x.Category.Name == "Scope Boxes"]
    """
    scopeboxs = []
    for item in temp:
        print item.Category.Name
        try:
            if item.Category.Name == "Scope Boxes":
                scopeboxs.append(item)
        except:
            continue
    return scopeboxs
    """

def finish_tool():
    global FINISH_TOOL
    FINISH_TOOL = True


def collect_mass():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Mass).WhereElementIsNotElementType().ToElements()

def main_func():
    selected_option = forms.CommandSwitchWindow.show(options.keys(), message='Select category to change workset')

    if selected_option:
        elements = options[selected_option]()
        #DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.selected_option).WhereElementIsNotElementType().ToElements()

    global FINISH_TOOL
    if FINISH_TOOL:
        return

    if len(elements) == 0:
        forms.alert("No element of this category are found in this project.")
        return


    """
    safety_counter = 0
    for x in elements:
        print x
        print get_element_workset(x).Name, get_element_workset(x).Kind
        safety_counter += 1
        if safety_counter > 50:
            break
    """
    #selected_workset = revit.doc.GetWorksetTable().GetWorkset(all_rooms[0].WorksetId)

    #print user_select_workset()
    """
    print "************"
    for x in get_all_userworkset():
        print x.Name
    """

    selected_workset = user_select_workset()


    #get rid of the elements that already in this workset, a work around for the nested shared family.
    #print len(elements)
    temp = []
    safety_counter = 0
    original_count = len(elements)

    for element in elements:

        """
        if safety_counter > 200:
            break
        """

        if get_element_workset(element).Name != selected_workset.Name:
            #print "its workset need to be corrected"
            #print get_element_workset(element).Name , selected_workset.Name
            temp.append(element)
            safety_counter += 1
            #print safety_counter

    elements = temp
    #print len(elements)
    if len(elements) == 0:
        forms.alert("All {} elements are already in this workset.".format(original_count))
        return


    script.get_output().freeze()
    safety_counter = 0
    fail_owner = 0
    fail_convert = 0
    fail_group = 0
    fail_groupindesignoption = 0
    fail_elementindesignoption = 0
    fail_2D = 0
    success_count = 0

    with revit.Transaction("Set Workset by Category"):
        for element in elements:
            safety_counter += 1
            """
            if safety_counter > 100:
                break
            """
            #print "******new element*****"
            #print safety_counter
            #print get_element_workset(element).Name
            ownership = DB.WorksharingUtils.GetWorksharingTooltipInfo(revit.doc,element.Id).Owner
            if ownership and (ownership != HOST_APP.username):
                print "Cannot edit {0} due to ownership by {2}---> {1}".format(element.Id,script.get_output().linkify(element.Id, title = "Go To Element"),ownership)
                fail_owner += 1

                continue
            else:
                #print "ok to edit"
                result = set_element_workset(element,selected_workset)
                if result == "OK":
                    success_count += 1
                elif result == "In Group":
                    fail_group += 1
                elif result == "Group In DesignOption":
                    fail_groupindesignoption += 1
                elif result == "Element In DesignOption":
                    fail_elementindesignoption += 1
                elif result == "View Specific":
                    fail_2D += 1
                else:
                    fail_convert += 1

    """
    if len(elements) == success_count:
        print "All elements changed workset successfully."
        script.get_output().self_destruct(1)
    """

    script.get_output().unfreeze()

    display_text = "Totally found {} elements in project, in which {} elements are in wrong workset.\n\n".format(original_count, len(elements))
    if success_count > 0:
        display_text += "{} successfully converted.\n".format(success_count)
    if fail_owner > 0:
        display_text += "{} failed due to ownership limit.\n".format(fail_owner)
    if fail_group > 0:
        display_text += "{} failed due to in a group.\n".format(fail_group)
    if fail_groupindesignoption > 0:
        display_text += "{} failed due to in a group inside design option.\n".format(fail_groupindesignoption)
    if fail_elementindesignoption > 0:
        display_text += "{} failed due to element inside a design option.\n".format(fail_elementindesignoption)
    if fail_convert > 0:
        display_text += "{} failed due to other reason.\n".format(fail_convert)
    if fail_2D > 0:
        display_text += "{} failed due to being view specific element\n".format(fail_2D)

    if len(elements) != success_count:
        display_text += "\nYou may use the output window for additional details and links to the elements."

    forms.alert( display_text )
############## main ###########
script.get_output().close_others()
FINISH_TOOL = False
options = {'Rooms': collect_room,
           'Furnitures': collect_furniture,
           'Grids':collect_grids,
           'Levels':collect_levels,
           'Architectural Columns':collect_columns,
           'Structural Columns':collect_structural_columns,
           'Areas':collect_areas,
           'Room Seperation Lines':collect_rm_seperation_lines,
           'Area Boundary Lines':collect_area_seperation_lines,
           'Mass':collect_mass,
           'ScopeBox':collect_scopebox,
           'Revit Link':collect_rvt,
           'CAD':collect_CAD,
           '--->click me to finish tool<---':finish_tool
           }
"""
add dwg and revit link as category

"""
"""
options = {'Rooms': OST_Rooms,
           'Furnitures': collect_furniture}
"""
while True:
    main_func()

    if FINISH_TOOL == True:
        break
