__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "match style\nfrom others"


"""

dim or text or arrowhead or.....
give detail inform from other doc and set current doc

"""



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
