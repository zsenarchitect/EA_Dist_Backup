__doc__ = "rename a family on spot without going thru the project browser"
__title__ = "Rename\nFamily"

from pyrevit import forms, DB, revit, script, output

################## main code below #####################

def rename_family():
    element_raw = revit.get_selection()
    if len(element_raw) != 1:
        forms.alert("Please select 1 element only.")
        script.exit()

    element = element_raw[0]
    current_family_name = element.Symbol.Family.Name

    with revit.Transaction("change family name"):
        attempt = 0
        max_try = 5
        while attempt < max_try:
            try:
                new_family_name = forms.ask_for_string(default= current_family_name, \
                                                        prompt="What is the new name?", \
                                                        title="Family Name change", \
                                                        width = 1200)
                #print new_family_name
                #print current_family_name
                if new_family_name == current_family_name:
                    #print "name not changing"
                    return

                if new_family_name == "":
                    forms.alert("Cannot use empty name, try again.")
                    continue
                if current_family_name != new_family_name:
                    element.Symbol.Family.Name = new_family_name
                    return

            except Exception as e:
                print (e)
                forms.alert("This name taken, try again.")
            finally:
                attempt += 1
    if attempt == max_try:
        forms.alert("Max attempt count reached. Exiting script without changing name")



if __name__ == "__main__":
    rename_family()

########note to self to research
#GUI window?
#how did select from para window show extra icon  instance/type by list?
#try to search from directory the name used for revit tab manager?

"""
>>> from playsound import playsound
>>> playsound('/path/to/a/sound/file/you/want/to/play.mp3')
"""
"""
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
    DB.BuiltInCategory.OST_Parking
]
"""


"""
from datetime import date
print(date.today())
"""
"""
keynotes = DB.FilteredElementCollector(revit.doc,revit.active_view.Id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()
"""

"""# ICollections format: System.Collections.Generic.List[DB.date type]([list data])
    shapes = [shapes list]
    shape_collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in shapes])
    revit.active_view.IsolateElementsTemporary(shape_collection)
"""

"""##Rhino - Rhino3dmIO

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
"""

"""
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
"""




"""
no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)
"""


"""
with forms.WarningBar(title='Pick title corner point'):
    ref_pt = revit.pick_point()
"""


"""
sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')
"""

"""
res = forms.alert(options = ["mark title corners at sheets", "remove existing marks from sheets."], msg = "I want to [.....]")

if "remove" in res:
    option = False
elif "mark" in res:
    option = True
else:
    script.exit()
"""

"""
forms.alert(msg = '{0} FILES RENAMED.'.format(sheetcount), sub_msg = fail_text)
"""



"""
from pyrevit import forms
items = ['item1', 'item2', 'item3']
res = forms.SelectFromList.show(items, button_name='Select Item')
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
"""


"""
DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()

.OfCategory(DB.BuiltInCategory.OST_Massing)
"""



"""
with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:
        new_name = "NoSheet-" + view.Name
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(new_name)
"""



"""
def final_print_table():
	table_data = []
	for item in view_item_collection:
		if item.view_name in view_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.view_name, item.line_count, output.linkify(item.id, title = "Go To View")]
			table_data.append(temp_list)

	output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])
"""

"""
output.freeze()
output.unfreeze()
output.self_destruct()
output.set_title()
output.update_progress(cur_value, max_value)
output.add_style('body { color: blue; }')
"""
"""



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
"""
"""
selection = revit.get_selection()

if len(selection) > 1:
    forms.alert("Please select 1 tags only.")
    script.exit()

if "Tags" not in selection[0].Category.Name:
    forms.alert("This is not a tag.")
    script.exit()
"""
"""
ref_tag = revit.doc.GetElement(get_ref_tag_id())
"""
