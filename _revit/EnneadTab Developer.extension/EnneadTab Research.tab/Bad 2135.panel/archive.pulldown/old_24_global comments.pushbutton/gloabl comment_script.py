__doc__ = "DO NOT USE, use newer show hide office markup tool"
__title__ = "[depreciated]24_Show/Hide Markups and Office layout"

from pyrevit import forms, script #
from Autodesk.Revit import DB # pyright: ignore 
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
import System
"""
from Autodesk.Revit import UI # pyright: ignore
uiapp = UI.UIApplicationapp
uidoc = UI.UIDocument
#optional
host_app = pyrevit._HostApplication
app = host_app.app
uiapp = host_app.uiapp
uidoc = host_app.uidoc




uidoc = __revit__.ActiveUIDocument
"""



"""
from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc
"""


def get_all_markup_contents(category_name, view_id = None):
    def is_markup_content(x):
        type = x.GetType()

        if "TextNote" in str(type):
            type_name = x.TextNoteType.LookupParameter("Type Name").AsString()
        elif "Dimension" in str(type):
            type_name = x.DimensionType.LookupParameter("Type Name").AsString()
            #print x.DimensionType.StyleType
        elif str(type) in ["Autodesk.Revit.DB.DetailArc",
                            "Autodesk.Revit.DB.DetailLine",
                            "Autodesk.Revit.DB.ModelLine",
                            "Autodesk.Revit.DB.ModelArc",
                            "Autodesk.Revit.DB.DetailNurbSpline",
                            "Autodesk.Revit.DB.CurveElement" ,
                            "Autodesk.Revit.DB.DetailEllipse" ,
                            "Autodesk.Revit.DB.DetailEllipse",
                            "Autodesk.Revit.DB.ModelHermiteSpline",
                            "Autodesk.Revit.DB.DetailEllipse"]:
            type_name = x.LineStyle.Name
        elif "RevisionCloud" in str(type):
            return True
        else:
            print(type)
            type_name = "bad"

        #print type_name
        #script.exit()
        if "markup" in type_name.lower():
            #print "))))))))))))))))))))))"
            #print type_name
            return True
        return False




    bic = DB.BuiltInCategory.Parse(DB.BuiltInCategory,category_name)
    if view_id == None:
        all_elements = DB.FilteredElementCollector(doc).OfCategory(bic).WhereElementIsNotElementType().ToElements()
    else:
        all_elements = DB.FilteredElementCollector(doc, view_id).OfCategory(bic).WhereElementIsNotElementType().ToElements()

    return filter(is_markup_content, all_elements)


def OLD_get_unique_viewids(elements):
    return {x.OwnerViewId for x in elements}
    #for element in elements:


def process_view_for_markup_content(view_id):
    view = doc.GetElement(view_id)
    if "Save to Central" in view.Name:
        return
    #print "view name = {}".format(view.Name)
    ##get all dim, text, line inside each view
    ##filter out the markup content in view
    """
    all_markup_texts = get_all_markup_contents("OST_TextNotes", view_id)
    all_markup_dims = get_all_markup_contents("OST_Dimensions", view_id)
    all_markup_lines = get_all_markup_contents("OST_Lines", view_id)
    collection = all_markup_texts + all_markup_dims + all_markup_lines
    """
    view_collection = get_markup_content_by_view(view_id)
    #print try_hidding_all
    #print collection
    #for x in collection:
        #print x.IsHidden(view)


    action_list = [item.Id for item in view_collection if item.IsHidden(view) != try_hidding_all]
    action_list = System.Collections.Generic.List[DB.ElementId](action_list)
    if len(action_list) == 0:
        return

    if try_hidding_all:
        view.HideElements(action_list)
    else:
        view.UnhideElements(action_list)

def get_markup_content_by_view(view_id):
    return [element for element in markup_collection if element.OwnerViewId == view_id]








def get_all_office_layout_textnotes():
    all_textnotes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: "Office Layout" in x.TextNoteType.LookupParameter("Type Name").AsString(), all_textnotes)


def get_office_layout_textnote_by_view(view_id):
    return [element for element in get_all_office_layout_textnotes() if element.OwnerViewId == view_id]


def process_view_for_textnote(view_id):
    view = doc.GetElement(view_id)
    if "Save to Central" in view.Name:
        return

    view_collection = get_office_layout_textnote_by_view(view_id)

    action_list = [item.Id for item in view_collection if item.IsHidden(view) != try_hidding_all]
    action_list = System.Collections.Generic.List[DB.ElementId](action_list)
    if len(action_list) == 0:
        return

    if try_hidding_all:
        view.HideElements(action_list)
    else:
        view.UnhideElements(action_list)











def process_office_layout_template(template):


    #set visibility
    try:
        template.SetFilterVisibility(filter_id, not(try_hidding_all))
    except:
        print("skip {}".format(template.Name))
        pass

    #forms.alert("all template now {} office layout filter".format( res))
    pass

def get_office_layout_filter_id():
    #get the id of the office layout filter
    view_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Name == "Office Layout Content", view_filters)[0].Id



def get_all_templates():
    views = DB.FilteredElementCollector(doc).OfClass(DB.View)
    """
    for v in views:
        if v.IsTemplate:
            print(v.Name)
    """
    return [v for v in views if v.IsTemplate and v.Name in template_checklist]

def get_template_checklist():

    with open(template_checklist_filepath) as f:
        lines = f.readlines()
    #lines.insert(0, "<keep as current, make no change>")
    return map(lambda x: x.replace("\n",""), lines)

################## main code below #####################
output = script.get_output()
output.close_others()
template_checklist_filepath = r"I:\2135\0_BIM\10_BIM Management\Office Layout Template Checklist.txt"



#ask if want to show, hide
hidding_options = ["hide", "show", "know where is the template checklist saved"]
res = forms.alert("for all markup or office layout content, i want to [...]", options = hidding_options)
if res == hidding_options[0]:
    try_hidding_all = True
elif res == hidding_options[1]:
    try_hidding_all = False
else:
    forms.alert("Go to this text file to modify the view template name checklist that you want to participate the office layout filter on/off.\n\n{}".format(template_checklist_filepath))
    script.exit()

temp_1 = []
temp_2 = []
all_templates = []
cate_options = ["Markup Dim, Markup Textnote, Markup Line", "Revision Cloud", "Office Layout Filter"]
cate_selection = forms.SelectFromList.show(cate_options,
                                            multiselect = True,
                                            button_name = "Go!",
                                            title = "what is considered as markup?")

#get markup content
output.freeze()
all_markup_texts = get_all_markup_contents("OST_TextNotes")
all_markup_dims = get_all_markup_contents("OST_Dimensions")
all_markup_lines = get_all_markup_contents("OST_Lines")
all_clouds = get_all_markup_contents("OST_RevisionClouds")
#print all_clouds
output.unfreeze()


if cate_options[0] in cate_selection:
    temp_1 = all_markup_texts + all_markup_dims + all_markup_lines
if cate_options[1] in cate_selection:
    temp_2 = all_clouds
if cate_options[2] in cate_selection:
    template_checklist = get_template_checklist()
    all_templates = get_all_templates()
    filter_id = get_office_layout_filter_id()
#print all_templates


##get collection of the view that markup live in
markup_collection = temp_1 + temp_2
view_ids = {x.OwnerViewId for x in markup_collection}
#print view_ids

#print collection


##process contetn in this list for the view
t = DB.Transaction(doc, "{} markup content".format(res))
t.Start()
map(process_view_for_markup_content, view_ids)
#forms.alert("all {} markup elements {}\n(except sample graphic in the start view)".format(len(collection), res))

map(process_office_layout_template, all_templates)
view_ids = {x.OwnerViewId for x in get_all_office_layout_textnotes()}
map(process_view_for_textnote, view_ids)

t.Commit()

forms.alert("{} action finished.\n{} markup element involved (except sample graphic in the start view)\n{} view template changed.".format(res, len(markup_collection), len(all_templates)))

#for text not, if not have"{note author} in text contet, add that at front"

#report stauts
