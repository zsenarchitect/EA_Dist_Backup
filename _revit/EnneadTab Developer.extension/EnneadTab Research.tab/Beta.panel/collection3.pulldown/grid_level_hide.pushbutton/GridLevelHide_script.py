__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Hide\nGrid/Level"


from pyrevit import forms, DB, script, revit
from System.Collections.Generic import List



def get_filter_by_name(names):
    print("$$cuurent filter names = {}".format(names))
    #all_filters = DB.FilteredElementCollector(revit.doc).OfClass(DB.ElementParameterFilter).WhereElementIsElementType().ToElements()
    all_filters = DB.FilteredElementCollector(revit.doc).OfClass(DB.ParameterFilterElement)
    #all_filters = DB.FilteredElementCollector(revit.doc).OfClass(DB.ElementFilter).ToElements()
    OUT = []
    for filter in all_filters:
        if filter.Name in names:
            print("$$find a filter = {}".format(filter.Name))
            OUT.append( filter )
    return OUT

def get_grids_by_filter(filters):
    collection = []
    for filter in filters:
        collection.extend(  DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Grids).WherePasses(filter.GetElementFilter())  )

    return List[DB.ElementId]([x.Id for x in collection])

def get_levels_by_filter(filters):
    collection = []
    for filter in filters:
        collection.extend(  DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WherePasses(filter.GetElementFilter())  )

    return List[DB.ElementId]([x.Id for x in collection])

def get_keyword_forGRID_in_view_name(view_name):
    if "SUNKEN COURTYARD" in view_name or "B1" in view_name:
        keyword = ["Basement"]
    elif "SITE" in view_name:
        keyword = ["Site","T1","T2","T3","T4"]
    elif "T1" in view_name:
        keyword = ["T1"]
    elif "T2" in view_name:
        keyword = ["T2"]
    elif "T3" in view_name:
        keyword = ["T3"]
    elif "T4" in view_name:
        keyword = ["T4"]
    else:
        keyword = "#Not Found"
        print("no keyword found in view name : {}".format(view_name))
    return keyword


def get_keyword_forLEVEL_in_view_name(view_name):
    if "SUNKEN COURTYARD" in view_name or "B1" in view_name:
        keyword = ["Basement", "Site"]
    elif "SITE" in view_name:
        keyword = ["Site","T1","T2","T3","T4"]
    elif "T1" in view_name:
        keyword = ["Site","T1"]
    elif "T2" in view_name:
        keyword = ["Site","T2"]
    elif "T3" in view_name:
        keyword = ["T3"]
    elif "T4" in view_name:
        keyword = ["Site","T4"]
    else:
        keyword = "#Not Found"
        print("no keyword found in view name : {}".format(view_name))
    return keyword



def get_filter_name_by_keyword(keywords):
    #relate to gloabl filter options
    print("current keywords = {}".format(keywords))
    filter_names = []
    for keyword in keywords:
        for filter_name in filter_options:
            if keyword in filter_name:
                filter_names.append(filter_name)
    return filter_names

def get_keyword_in_filter_name(filter_name):
    keyword = filter_name.split("- ")[-1]
    return keyword

def hide_all_level_grid(view):

    levels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    grids = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
    collection = []
    #print levels, grids
    collection.extend(levels)
    collection.extend(grids)
    if len(collection) == 0:
        print("Nothing to hide")
    view.HideElements(    List[DB.ElementId]([x.Id for x in collection])    )

######## main code below ########


filter_options = [
            "Grids & Levels - Basement",
            "Grids & Levels - Site",
            "Grids & Levels - T1",
            "Grids & Levels - T2",
            "Grids & Levels - T3",
            "Grids & Levels - T4"
            ]

"""
keyword_options = [get_keyword_in_filter_name(x) for x in filter_options]
print(keyword_options)
"""

sel_sheets = forms.select_sheets(title='Select Sheets that will hide/unhide levels grids')

if sel_sheets == None:
    script.exit()

with revit.Transaction("apply level grid hide/unhide"):
    #for each view on selected sheets, get keyword
    for sheet in sel_sheets:
        for view_id in sheet.GetAllPlacedViews():
            view = revit.doc.GetElement(view_id)
            hide_all_level_grid(view)
            try:
                hide_all_level_grid(view)#set everything to no shown and then turn on the one we need
            except:
                print(view.Name)
                continue###lengend or schedule or draft view that donest have levels grid to hide

            print("\t\tProcessing View: {}".format(view.Name))
            view_name_keyword = get_keyword_forGRID_in_view_name(view.Name)
            if view_name_keyword == "#Not Found":
                continue
            print("view_name_keyword: " + str(view_name_keyword))
            filter_name = get_filter_name_by_keyword(view_name_keyword)
            print("filter_name: " + str(filter_name))
            filter = get_filter_by_name(filter_name)
            print("filter: " + str(filter))
            grids = get_grids_by_filter(filter)
            view.UnhideElements(grids)


            view_name_keyword = get_keyword_forLEVEL_in_view_name(view.Name)
            if view_name_keyword == "#Not Found":
                continue
            print("view_name_keyword: " + str(view_name_keyword))
            filter_name = get_filter_name_by_keyword(view_name_keyword)
            print("filter_name: " + str(filter_name))
            filter = get_filter_by_name(filter_name)
            print("filter: " + str(filter))
            levels = get_levels_by_filter(filter)
            view.UnhideElements(levels)










########note to self to research
#GUI window?
#how did select from para window show extra icon  instance/type by list?
#try to search from directory the name used for revit tab manager?

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

"""
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
"""




"""
no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)
"""


"""
with forms.WarningBar(title='Pick title corner point'):
    ref_pt = revit.pick_point()
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
