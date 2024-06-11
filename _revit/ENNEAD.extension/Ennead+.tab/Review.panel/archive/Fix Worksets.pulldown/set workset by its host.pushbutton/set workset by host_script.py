__doc__ = "Define the workset by its host"
__title__ = "Set Workset\nBy Parent Host"

"""
for door, window, light fixture, face based family, use the host workset to drive hosted.
door on curtain wall as well
"""

from pyrevit import DB,forms,revit,script
from pyrevit import HOST_APP
from System import Drawing

def get_id_card(element):
    try:
        id_card = "[{}]:[{}]".format(element.Symbol.FamilyName, element.Symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString())
    except:
        id_card = "'{}''".format(element.Id)
    return id_card

def set_element_workset(element):

    try:
        host_workset = get_element_workset(element.Host)
        para = element.GetParameters("Workset")[0]
        #print para
        para.Set(host_workset.Id.IntegerValue)
        """
        para = element.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM]
        para.Set(workset)
        """
        return "OK"
    except:
        print("\n---------------------------------")


        id_card = get_id_card(element)

        ########print element.Symbol.GetPreviewImage(Drawing.Size(200,200))
        #### bmp1.Save("c:\\button.gif", System.Drawing.Imaging.ImageFormat.Gif)

        #if hasattr(obj, 'attr_name')
        #if isinstance(5, int)


        if element.GroupId != -1: #-1 means not in group
            try:
                group_name = revit.doc.GetElement(element.GroupId).Name
                print("\nFail to set workset for {0} becasue it is in group '{3}'---> {1}--->{2}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element"),script.get_output().linkify(element.GroupId, title = "Go To Group"), group_name))
                print("This group is currently in workset '{}'".format(get_element_workset(revit.doc.GetElement(element.GroupId)).Name))
            except:
                group_name = "None"



            try:
                #if revit.doc.GetElement(element.GroupId).DesignOption:
                print("The group '{}' is in design option '{}'. You may use 'Go To Group' while that design option is in edit mode.\n\n ".format(group_name, revit.doc.GetElement(element.GroupId).DesignOption.Name))
                return "Group In DesignOption"
            except:#no attribute designoption, just say it is in a group
                return "In Group"
            finally:
                #print ("test" + str(revit.doc.GetElement(element.GroupId).DesignOption))
                pass

        elif element.DesignOption != -1:#-1 means not in design option
            print("The element is in design option '{}'. You may use 'Go To Element' while that design option is in edit mode.\n\n ".format(element.DesignOption.Name))
            return "Element In DesignOption"

        else:
            print("Fail to set workset on {0} ---> {1}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element")))
            return "Unknown"

        print("Contact SenZhang")

def get_element_workset(element):

    try:
        return revit.doc.GetWorksetTable().GetWorkset(element.WorksetId)
    except:
        print(element)
        print(element.Id)
        pass

def collect_door():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

def collect_window():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
############## main ###########
options = {'Windows': collect_window,
           'Doors': collect_door
           }

selected_option = forms.CommandSwitchWindow.show(options.keys(),message='Select category to change workset')

if selected_option:
    elements = options[selected_option]()
    #DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.selected_option).WhereElementIsNotElementType().ToElements()

if len(elements) == 0:
    forms.alert("No element of this category are found in this project.")
    script.exit()

temp = []
safety_counter = 0
original_count = len(elements)
fail_inPlace = 0
for element in elements:

    """
    if safety_counter > 200:
        break
    """
    #if element.Host == None:
    if element.Symbol.Family.IsInPlace:
        print("Cannot edit '{0}' due to it is in-place family---> {1}".format(get_id_card(element),script.get_output().linkify(element.Id, title = "Go To Element")))
        print("It is currently in workset '{}'\n~~~~~~~~".format(get_element_workset(element).Name))
        fail_inPlace += 1
        continue


    if get_element_workset(element).Name != get_element_workset(element.Host).Name:
        #print "its workset need to be corrected"
        #print get_element_workset(element).Name , selected_workset.Name
        temp.append(element)
        safety_counter += 1
        #print safety_counter

elements = temp
#print len(elements)
if len(elements) == 0 and fail_inPlace == 0:
    forms.alert("All {} elements are already in its parent's workset.".format(original_count))
    script.exit()



script.get_output().freeze()
safety_counter = 0
fail_owner = 0
fail_convert = 0
fail_group = 0
fail_groupindesignoption = 0
fail_elementindesignoption = 0
success_count = 0

with revit.Transaction("Set Workset by Host"):
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
            print("Cannot edit {0} due to ownership by {2}---> {1}".format(get_id_card(element),script.get_output().linkify(element.Id, title = "Go To Element"),ownership))
            fail_owner += 1

            continue
        else:
            #print "ok to edit"
            result = set_element_workset(element)
            if result == "OK":
                success_count += 1
            elif result == "In Group":
                fail_group += 1
            elif result == "Group In DesignOption":
                fail_groupindesignoption += 1
            elif result == "Element In DesignOption":
                fail_elementindesignoption += 1
            else:
                fail_convert += 1
"""
if len(elements) == success_count:
    print("All elements changed workset successfully.")
    script.get_output().self_destruct(1)
"""
script.get_output().unfreeze()

display_text = "Totally found {} elements in project, in which {} elements are in wrong workset.".format(original_count, len(elements))
if fail_inPlace > 0:
    display_text += "\n{} elements have no host(AKA. In-place Family).".format(fail_inPlace)

display_text += "\n\n"


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

if len(elements) != success_count or fail_inPlace != 0:
    display_text += "\nYou may use the output window for additional details and links to the elements."

forms.alert( display_text )
