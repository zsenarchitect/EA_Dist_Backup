__doc__ = "Select views from project browser, remove tags that are too close to other tags( if they are taging the same element).\n\nIt then tags Objects with user selected type"
__title__ = "27_TAG MANY VIEWS---"

from pyrevit import forms, revit, script #
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import Creation

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

doc = __revit__.ActiveUIDocument.Document # pyright: ignore
# uidoc = __revit__.ActiveUIDocument

# from Autodesk.Revit import UI # pyright: ignore
# uiapp = UI.UIApplicationapp
# uidoc = UI.UIDocument
# optional
# host_app = pyrevit._HostApplication
# app = host_app.app
# uiapp = host_app.uiapp
# uidoc = host_app.uidoc


def get_all_area_tags(view):
    if view.IsTemplate:
        return []
    return DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaTags).WhereElementIsNotElementType().ToElements()

def cleanup_tag_in_view(view):
    if len(get_all_area_tags(view)) == 0:
        return

    def delete_tag_closer_than_distance(tag):
        delete_happened = False

        try:
            location = tag.TagHeadPosition
        except Exception as e:
            print("*"*20)
            print (e)
            print(tag)
            print(tag.Id)
            print(view.Name)
            return delete_happened

        for other_tag in get_all_area_tags(view):

            if tag.Id == other_tag.Id or tag.Area.Id == other_tag.Area.Id:
                continue
            other_location = other_tag.TagHeadPosition
            other_location_projected = DB.XYZ(other_location.X,
                                                other_location.Y,
                                                location.Z)
            dist = location.DistanceTo(other_location_projected)
            #print dist
            if dist < tolerance:

                doc.Delete(other_tag.Id)
                delete_happened = True
                break


        return delete_happened  #delete happedn so loop need to restart




    safety = 0
    status_reset = True
    tolerance = 100 #in mm unit
    tolerance *= view.Scale
    tolerance = ARCHI_UTILITY.mm_to_internal(tolerance)

    while status_reset:
        status_reset = False
        if safety > 100:
            break
        safety += 1

        tags = get_all_area_tags(view)
        for tag in tags:
            if not tag:
                continue
            status_reset = status_reset or delete_tag_closer_than_distance(tag)
            if status_reset:
                break


    pass



def tag_in_view(view):
    #get all areas in view
    areas = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()


    for area in areas:
        #get pts of area
        area_location = area.Location.Point
        # print area_location.X
        # print area_location.Y

        tag_location = DB.UV(area_location.X, area_location.Y)

        #create area tags
        new_tag = doc.Create.NewAreaTag(view, area, tag_location)
        new_tag.TagHeadPosition = area_location
        new_tag.HasLeader = False

    #change all tag to defined tag type
    area_tags = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaTags).WhereElementIsNotElementType().ToElements()

    for area_tag in area_tags:
        area_tag.AreaTagType = tag_type
    # map(lambda x: x.AreaTagType = tag_type, area_tags)
    # cleanup_tag_in_view(view)


################## main code below #####################
output = script.get_output()
output.close_others()

selection = revit.get_selection()
#GET SELECTED VIEWS
views = selection

#define tag
tag_types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
type_name = forms.alert("pick tag family", options = ["Discount Ratio Tag",
                                                        "TAG_Area - FC",
                                                        "TAG_Area_Internal Check"])
tag_type = filter(lambda x: x.FamilyName == type_name, tag_types)[0]
#print tag_type
res = forms.alert("sync and close docs after finish?", options = ["Yes","No"])
close_others_afterward = True if res == "Yes" else False


#PROCESS EACH VIEW
t = DB.Transaction(doc, "tag many views")
t.Start()
map(tag_in_view, views)
t.Commit()

if close_others_afterward:
    EnneadTab.REVIT.REVIT_SYNC.sync_and_close(close_others = close_others_afterward)


#ideas:
"""
IDEAS
    - wall to room seperation line or area boubnary line
    - copy material defination, object style definiation, object style material assignment, template defination across open docs or from link
    - net bound for complex curtain panel inside
    -rename family/type in multiple open doc
    -report dim that is not whole number

    - deep purge sub family




    - what is my view direvtion vector, what is this line vector
    - override graphic for all user keynote as blue color,

    - ceiling family alway use ceiling line but switch head up and down becasue usally you dim to the ceiling dash

    - annotater family add lines for eng and CN as interger to control the left align location

    - RENAME GROUP BY CURRENT VIEW---- group usage report

    - flusing , bolt, fire stoper, plate, hanger, angle, tubes

    - MATCH SLAB BOUDARY PINK LINES

    - INUSLATED BACK PAN , OPTION TO USE CL AND SIDE Line
    - TUBE OPTION TO US CL AND EDGE



    - add section, elevation, to temp vision tool

    - extract CAD lines by layer and assign to object style

    - ANNOTATION MODE -- ONLY ABLE TO SELECT 2D ELEMENTS

    - GUI recent used family type, drag and drop

    - IF FAMILY NAME = TYPE NAME, THAT IS NOT GOOD, RENAME THE TYPE NAME TO "DD"

    - PERMITION TO DELEETE ELEMENT

    - mark element as non-editable, soyou dont accidentally go inside a family_doc


    - detauil item object style:
        insulation, water proof, profil extieor, interior, cut but not important, center, slab cut, see but not important....

    - proejct line style
        $$ predefined profile, ceiling, waterproffing, slab_cut, column cut, CL line, ceiling

    - label unused legend and schedule

    - CHANGE  $LINE STYLE TO INVISIBLE(USFUL FOR FILLED REGION)
    AND CHANGE ALL INVISUABELT O T$$ea LINE SO YOU CAN CHECK THE BOUDNARY

    - SHORT LIST LOCAL OVERRIDE


t = DB.Transaction(doc , "action")
t.Start()
#do work
t.Commit()

__all__ = ('pick_element', 'pick_element_by_category',
           'pick_elements', 'pick_elements_by_category',
           'get_picked_elements', 'get_picked_elements_by_category',
           'pick_edge', 'pick_edges',
           'pick_face', 'pick_faces',
           'pick_linked', 'pick_linkeds',
           'pick_elementpoint', 'pick_elementpoints',
           'pick_point', 'pick_rectangle', 'get_selection_category_set',
           'get_selection')

doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = revit.doc
uidoc = revit.uidoc




global

########note to self to research
#GUI window?
#how did select from para window show extra icon  instance/type by list?
#try to search from directory the name used for revit tab manager?


fake delete Transaction
    with revit.DryTransaction("Search for linked elements"):
        linked_elements_list = revit.doc.Delete(selection.first.Id)

from playsound import playsound
playsound('/path/to/a/sound/file/you/want/to/play.mp3')

FREQUENTLY_SELECTED_CATEGORIES = [
    DB.BuiltInCategory.OST_Areas,
    DB.BuiltInCategory.OST_AreaTags,
    DB.BuiltInCategory.OST_AreaSchemeLines,
    DB.BuiltInCategory.OST_Columns,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_Dimensions,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_StructuralFraming,
    DB.BuiltInCategory.OST_Furniture,
    DB.BuiltInCategory.OST_Grids,
    DB.BuiltInCategory.OST_Rooms,
    DB.BuiltInCategory.OST_RoomTags,
    DB.BuiltInCategory.OST_CurtainWallPanels,
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Windows,
    DB.BuiltInCategory.OST_Ceilings,
    DB.BuiltInCategory.OST_SectionBox,
    DB.BuiltInCategory.OST_ElevationMarks,
    DB.BuiltInCategory.OST_Parking,
    DB.BuiltInCategory.OST_GenericModel
    OST_Sheets
    OST_TextNotes
    OST_GenericLines
    OST_Lines
]


remove duplicate from list:
list({x for x in list_raw})

filter(function, sequence)
Parameters:
function: function that tests if each element of a
sequence true or not.
sequence: sequence which needs to be filtered, it can
be sets, lists, tuples, or containers of any iterators.
Returns:
returns an iterator that is already filtered.



from datetime import date
print(date.today())


keynotes = DB.FilteredElementCollector(revit.doc,revit.active_view.Id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()

WhereElementIsElementType()
#to get element type name
type.LookupParameter("Type Name").AsString()


# ICollections format: System.Collections.Generic.List[DB.date type]([list data])
    shapes = [shapes list]
    shape_collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in shapes])
    revit.active_view.IsolateElementsTemporary(shape_collection)


##Rhino - Rhino3dmIO

Rhino3dmIO is a subset of RhinoCommon and it gives you access to openNurbs, allowing you to, amongst other things, read and write 3dm files.
>>> from rpw.extras.rhino import Rhino as rc
>>> pt1 = rc.Geometry.Point3d(0,0,0)
>>> pt2 = rc.Geometry.Point3d(10,10,0)
>>> line1 = rc.Geometry.Line(pt1, pt2)
>>> line1.Length
14.142135623730951
>>>
>>> pt1 = rc.Geometry.Point3d(10,0,0)
>>> pt2 = rc.Geometry.Point3d(0,10,0)
>>> line2 = rc.Geometry.Line(pt1, pt2)
>>>
>>> rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
(True, 0.5, 0.5)
>>>
>>> file3dm = f = rc.FileIO.File3dm()
>>> file3md_options = rc.FileIO.File3dmWriteOptions()
>>> file3dm.Objects.AddLine(line1)
>>> filepath = 'c:/folder/test.3dm'
>>> file3dm.Write(filepath, file3md_options)


forms.WPFWindow(xaml_source, literal_string=False, handle_esc=True, set_owner=True)
>>> from pyrevit import forms
>>> layout = '<Window ' \
>>>          'xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" ' \
>>>          'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" ' \
>>>          'ShowInTaskbar="False" ResizeMode="NoResize" ' \
>>>          'WindowStartupLocation="CenterScreen" ' \
>>>          'HorizontalContentAlignment="Center">' \
>>>          '</Window>'
>>> w = forms.WPFWindow(layout, literal_string=True)
>>> w.show()


>>> with ErrorSwallower() as swallower:
>>>     for fam in families:
>>>         revit.doc.EditFamily(fam)
>>>         if swallower.get_swallowed():
>>>             logger.warn("Warnings swallowed")

forms.alert(msg, title=None, sub_msg=None, expanded=None, footer='', ok=True, cancel=False, yes=False, no=False, retry=False, warn_icon=True, options=None, exitscript=False)
forms.ask_for_color(default=None)
forms.ask_for_one_item(items, default=None, prompt=None, title=None, **kwargs)
forms.ask_for_string(default=None, prompt=None, title=None, **kwargs)
forms.select_family_parameters(family_doc, title='Select Parameters', button_name='Select', multiple=True, filterfunc=None, include_instance=True, include_type=True, include_builtin=True, include_labeled=True)
forms.select_image(images, title='Select Image', button_name='Select')
forms.select_parameters(src_element, title='Select Parameters', button_name='Select', multiple=True, filterfunc=None, include_instance=True, include_type=True, exclude_readonly=True)
forms.select_swatch(title='Select Color Swatch', button_name='Select')


output = pyrevit.output.get_output()
output.print_image(r'C:\image.gif')
print(script.get_script_path())
print(script.get_bundle_files())
print(script.get_bundle_file('triangle.png'))
output.set_width(1500)
output.set_height(900)
output.center()
output.close_others()
#output.open_url("http://dict.cn/")
output.show()
output.print_md(str)----->    https://www.markdownguide.org/basic-syntax/
        bold ====   **text**
        italic ====   *text*
        bold and italic ======   ***text***
        heading =======   ## text   (# biggest, ##### smallest)





no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)




with forms.WarningBar(title='Pick title corner point'):
    ref_pt = revit.pick_point()




sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')



res = forms.alert(options = ["mark title corners at sheets", "remove existing marks from sheets."], msg = "I want to [.....]")

if "remove" in res:
    option = False
elif "mark" in res:
    option = True
else:
    script.exit()



forms.alert(msg = '{0} FILES RENAMED.'.format(sheetcount), sub_msg = fail_text)





from pyrevit import forms
items = ['item1', 'item2', 'item3']
res = forms.SelectFromList.show(context = items, button_name='Select Item')
if res == 'item1':
    do_stuff()
~~~~~
ops = [viewsheet1, viewsheet2, viewsheet3]
res = forms.SelectFromList.show(ops,
                                multiselect=False,
                                name_attr='Name',
                                button_name='Select Sheet')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
forms.SelectFromList.show(
        {'All': '1 2 3 4 5 6 7 8 9 0'.split(),
         'Odd': '1 3 5 7 9'.split(),
         'Even': '2 4 6 8 0'.split()},
        title='MultiGroup List',
        group_selector_title='Select Integer Range:',
        multiselect=True
    )
~~~
ops = {'Sheet Set A': [viewsheet1, viewsheet2, viewsheet3],
       'Sheet Set B': [viewsheet4, viewsheet5, viewsheet6]}
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                name_attr='Name',
                                group_selector_title='Sheet Sets',
                                button_name='Select Sheets')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
from pyrevit import forms

class MyOption(forms.TemplateListItem):
    @property
    def name(self):
        return "Option: {}".format(self.item)

ops = [MyOption('op1'), MyOption('op2', checked=True), MyOption('op3')]
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                button_name='Select Item')
~~~

selected_views = forms.SelectFromList.show(no_sheet_views,
                                multiselect=True,
                                name_attr='Name',
                                title = "Those views are not on sheet",
                                button_name= "Mark them with 'NoSheet-' prefix",
                                filterfunc=lambda x: x.ViewType not in [DB.ViewType.Legend, DB.ViewType.Schedule])




DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()

.OfCategory(DB.BuiltInCategory.OST_Massing)





with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:
        new_name = "NoSheet-" + view.Name
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(new_name)





def final_print_table():
    table_data = []
    for item in view_item_collection:
        if item.view_name in view_item_collection_selected:
            #temp_list = [item.critical_level_text, item.view_name, item.line_count]
            temp_list = [ item.critical_level_text, item.view_name, item.line_count, output.linkify(item.id, title = "Go To View")]
            table_data.append(temp_list)
    output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])



output.freeze()
output.unfreeze()
output.self_destruct()
output.set_title()
output.update_progress(cur_value, max_value)
output.add_style('body { color: blue; }')





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


>>> for count, value in enumerate(values):
...     print(count, value)


selection = revit.get_selection()

if len(selection) > 1:
    forms.alert("Please select 1 tags only.")
    script.exit()

if "Tags" not in selection[0].Category.Name:
    forms.alert("This is not a tag.")
    script.exit()


ref_tag = revit.doc.GetElement(get_ref_tag_id())

"""
