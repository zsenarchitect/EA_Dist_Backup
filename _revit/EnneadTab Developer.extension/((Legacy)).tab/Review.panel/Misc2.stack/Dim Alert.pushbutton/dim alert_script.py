from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__title__ = "Dim Alert"
__doc__ = 'Use the Predefined Dims value list in the project to chack if there are dimensions not included in the ignore list.'



def GetParamByName(el,name):

    for para in el.Parameters:
        #print para.Definition.Name #enable this to see what parameter is available
        if para.Definition.Name == name:
            #print "OK, found para ID" + str(para.Id)

            #return el.LookupParameter(name).Id # can be used to return para ID
            return para

def get_dims_in_sheets(sheets):
    dims = []
    for sheet in sheets:
        viewports = sheet.GetAllViewports()
        for viewport in viewports:
            view_id = revit.doc.GetElement(viewport).ViewId
            dims_on_this_view = DB.FilteredElementCollector(revit.doc,view_id)\
              .OfCategory(DB.BuiltInCategory.OST_Dimensions)\
              .WhereElementIsNotElementType()\
              .ToElements()

            dims.extend(dims_on_this_view)
    return dims

def print_segement_value(dim):
    segs = dim.Segments
    for idx, seg in enumerate(segs, 1):
        print ("Segment {}: Dim Value Readable = {}".format(idx, seg.ValueString))
    print("---------")
    for idx, seg in enumerate(segs, 1):
        print ("Segment {}: Dim Value Internal = {}".format(idx, seg.Value))

def print_values(dim):

    if dim.NumberOfSegments == 0:
        print("Single Segment Dimension")
        print ("Dim Value Readable = {}".format(dim.ValueString))
        print ("Dim Value Internal = {}".format(dim.Value))
    else:
        print ("{} Segments Found.".format(dim.NumberOfSegments))
        values = print_segement_value(dim)

def print_output_list(dims):
    if len(dims)>0:
        type_names = []
        for idx, dim in enumerate(dims):


            parent_view = dim.OwnerViewId

            print ("#{}: Bad Dim Id = {}-->{}".format(idx+1,dim.Id,output.linkify(dim.Id, title = "Go To Dim")))

            #print ("Dim Value = {}".format(dim.Value))
            print_values(dim)



            print("Found in this view: {} :-->{}".format(revit.doc.GetElement(parent_view).Name,output.linkify(parent_view, title = "Go To View")))
            print(seperation)


    print('{0} Bad Dim(s) FOUND IN SELECTED SHEETS.'.format(len(dims)))

    print ("They have value not in the ignore list defined in view: {} ------> {}".format(ignore_list_view_name,output.linkify(ignore_list_view.Id, title = "Go To View")))




def get_draftingView_by_name(name):
    all_draftviews = DB.FilteredElementCollector(revit.doc)\
      .OfClass(DB.ViewDrafting)\
      .WhereElementIsNotElementType()\
      .ToElements()

    for view in all_draftviews:
        if view.Name == name:
            return view



def get_textnote_on_view(view):
    try:
        return DB.FilteredElementCollector(revit.doc,view.Id)\
          .OfCategory(DB.BuiltInCategory.OST_TextNotes)\
          .WhereElementIsNotElementType()\
          .ToElements()[0]
    except:
        forms.alert("No drafting view with this name found. Action will be Cancelled\nAre you sure that view has been setup in the project? \nAre you sure that is a drafting view?", title = "Hmmm...")
        script.exit()


def get_value_from_textnote(el):
    value_list = []
    lines = el.Text.split("\r")
    for line in lines:
        if (line.startswith("#") or line == "" ) == False:
            value_list.append(line.replace(";", ""))
    return  value_list

def all_value_in_list(dim, list):#when every segment dim can be ignored from alert, the whole dim is in ignore list.
    for seg in dim.Segments:
        if seg.ValueString not in list:
            return False
    return True


#------------------main code below------------
sel_sheets = forms.select_sheets(title='Select Sheets That You Want To Check Dim Value.')

output = script.get_output()

seperation = "-----------------------------------------------------"

if sel_sheets:
    if len(sel_sheets) > 0:
        all_dims = get_dims_in_sheets(sel_sheets)
    else:
        forms.alert("No Sheet Selected. \nCancelled.")
        script.exit()
else:
    forms.alert("Cancelled")
    script.exit()


ignore_list_view_name = "#EA_Dim_Alert_Ignore_List"
#get the textnote element in drafting view called "#EA_Dim Alert Ignore List"
ignore_list_view_name = forms.ask_for_string( default = "#EA_Dim_Ignore_List", prompt = "Which view do you want to reference as ignore list?\nType in the drafting view name that has the ignore list \nor accept default name suggestion.\nYou can look up on the BIM Wiki for the suggested format.", title = "What is it called?")


ignore_list_view = get_draftingView_by_name(ignore_list_view_name)



#print ("debug:{}".format(temp_view.ViewName))
textnote_el = get_textnote_on_view(ignore_list_view)

#read content of that textbox as ignore list
ignore_list = get_value_from_textnote(textnote_el)
#print ("debug:{}".format(ignore_list))

#prepare empty container bad dims
bad_dims = []

#compare dim in dims to ignore listed
for dim in all_dims:

    #if single segement no in ignore list, then it is bad
    if dim.NumberOfSegments == 0:
        if dim.ValueString not in ignore_list:
            #print "single sement dim not in ignore list"
            bad_dims.append(dim)

    #or many segements
    else:
        if all_value_in_list(dim, ignore_list) == False:
            #print "multi segement dim has parts not in ignore list"
            bad_dims.append(dim)

#display all bad dims.
print_output_list(bad_dims)
