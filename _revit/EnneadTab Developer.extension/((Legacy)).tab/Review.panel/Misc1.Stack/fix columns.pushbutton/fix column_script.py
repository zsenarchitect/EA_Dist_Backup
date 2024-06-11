__doc__ = "It finds the intersection point of all grids and see if there is a architectural column near miss this intersection."
__title__ = "Column\nLocations"

import clr
from pyrevit import revit, DB, script, forms



"""
this will look for grid intersection point in the project and move to the nearest point

perform on with while loop, can fix single or multiple columns.
if cannot eidt columns in group, raise the element


"""

def find_pair(list):
    temp = [(a, b) for idx, a in enumerate(list) for b in list[idx + 1:]]
    return temp

def get_grid_pts_from_grid_pairs(grid_pairs):
    grid_pts = []
    i = 0
    for pair in grid_pairs:
        """
        if i > 20000:####remove later if decide to do all point
            break
        """
        grid1 = list(pair)[0]
        grid2 = list(pair)[1]
        crv1 = grid1.Curve
        crv2 = grid2.Curve

        """if curve MakeUnbound(), if line CreateUnBound()
        print(grid1.Curve)
        print(grid1.Curve.MakeUnbound())
        try:
            res = crv1.Intersect(crv2)
        except:
            output = script.get_output()
            print("{}:'{}'".format(grid1.Name, output.linkify(grid1.Id, title = "Go to grid")))
            print("{}:'{}'".format(grid2.Name, output.linkify(grid2.Id, title = "Go to grid")))
        """

        res = crv1.Intersect(crv2)
        #print res
        if res == DB.SetComparisonResult.Overlap:
            '''
            print("~~~~~~~~~~")
            print(grid1.Name)
            print(grid2.Name)
            print(res)
            '''
            i += 1
            #iResult = DB.IntersectionResultArray()
            iResult = clr.StrongBox[DB.IntersectionResultArray](DB.IntersectionResultArray())
            #iResult = StrongBox[resultArray](DB.IntersectionResultArray())
            crv1.Intersect(crv2,iResult)
            if iResult.Size > 1:
                print("%%%%many intersection")


            raw_pt = iResult.Item[0].XYZPoint
            projected_pt = DB.XYZ(raw_pt.X,raw_pt.Y,0)
            grid_pts.append([grid1.Name, grid2.Name,projected_pt])

    #print grid_pts
    #print len(grid_pts)
    return grid_pts


def CP_dist(column, pts):
    location_raw = column.Location.Point
    location = DB.XYZ(location_raw.X,location_raw.Y, 0)
    #print location
    #CP_dist = min([location.DistanceTo(x[2]) for x in pts])


    #########i need to project flat the pts before make distance.
    pts.sort(key = lambda x: location.DistanceTo(x[2]), reverse = False)
    CP = pts[0]
    CP_dist = location.DistanceTo(CP[2])



    """
    CP = pts[0]
    for pt in pts:
        if location.DistanceTo(pt) < location.DistanceTo(CP):
            CP = pt
    print("****")
    print(location.DistanceTo(CP))
    print(CP_dist)
    print("^^^^")
    """

    if CP_dist < 0.00001:
        return [0, [   CP[0], CP[1]]   ]
    else:
        return [CP_dist, [   CP[0], CP[1]]   ]

class bad_column:
    def __init__(self, ref, dist, grids):
        self.dist = dist
        self.Id = ref.Id
        self.grids = grids
        if dist >= 100/304.8:
            self.condition = "<Design Intent?>"
        elif dist > 1/304.8:
            self.condition = "{Critical, Must Fix}"
        elif dist > 0.01/304.8:
            self.condition = "[Bad, Should Fix]"
        else:
            self.condition = "(Meh...)"

############# main code below #######

all_grids = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()
grids = forms.SelectFromList.show(all_grids, name_attr = "Name", multiselect = True, button_name= "Pick Grids", title = "pick grids to get intersection pt")
if grids == None:
    script.exit()
"""
for x in grids:
    print(x.Name)
"""
#print list(grids)
#find_pair([1,2,3,4,5])
grid_pairs = find_pair(list(grids))
grid_pts = get_grid_pts_from_grid_pairs(grid_pairs)

columns = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
#columns = forms.SelectFromList.show(all_columns, name_attr = "MC_$BuildingID", multiselect = True, button_name= "Pick Columns", title = "pick columns to meassure pt distance")
"""if columns == None:
    script.exit()"""

#print "@"*10
output = script.get_output()
collection = []
for column in columns:
    res = CP_dist(column, grid_pts)
    dist = res[0]
    if dist == 0:
        pass
    else:
        collection.append(bad_column(column, dist, res[1]))

collection.sort(key = lambda x: x.dist, reverse = True)
for item in collection:
    print("!"*20)
    print("{}: Column '{}' is '{}ft' or '{}mm' away from nearst grid intersection by {}. --->{}".format(item.condition, item.Id, item.dist, item.dist *304.8, item.grids, output.linkify(item.Id, title = "Go to Column")))


with revit.TransactionGroup("Highlight bad column"):
    view = revit.doc.ActiveView

    with revit.Transaction("reset color"):
        all_columns = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()

        for item in all_columns:
            setting = DB.OverrideGraphicSettings()
            view.SetElementOverrides(item.Id, setting)

    with revit.Transaction("Highlight color column"):
        view.EnableTemporaryViewPropertiesMode(view.Id)
        for item in collection:

            if "Design Intent" in item.condition:
                color = DB.Color(91,186,214)
            elif "Critical" in item.condition:
                color = DB.Color(210,102,91)
            elif "Bad" in item.condition:
                color = DB.Color(219,163,82)
            elif "Meh" in item.condition:
                color = DB.Color(172,198,95)
            else:
                print("not possible")


            setting = DB.OverrideGraphicSettings()
            setting.SetCutForegroundPatternColor(color)
            #setting.SetCutForegroundPatternId(fill_pattern.Id)
            setting.SetSurfaceForegroundPatternColor(color)
            #setting.SetSurfaceForegroundPatternId(fill_pattern.Id)
            view.SetElementOverrides(item.Id, setting)


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
