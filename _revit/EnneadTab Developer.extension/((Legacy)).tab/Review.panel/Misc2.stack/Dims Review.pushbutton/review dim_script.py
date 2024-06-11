from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__title__ = "Review Dim"
__doc__ = 'Review the content and type of dimensions.'



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
            dim_this_view = DB.FilteredElementCollector(revit.doc,view_id)\
              .OfCategory(DB.BuiltInCategory.OST_Dimensions)\
              .WhereElementIsNotElementType()\
              .ToElements()

            dims.extend(dim_this_view)
    return dims

def print_segement_value(dim):
    segs = dim.Segments
    for idx, seg in enumerate(segs, 1):
        print ("Segment {}: Dim Value Readable = {}".format(idx, seg.ValueString))
    print("---------")
    for idx, seg in enumerate(segs, 1):
        print ("Segment {}: Dim Value Internal = {} ft".format(idx, seg.Value))

def print_values(dim):

    if dim.NumberOfSegments == 0:
        print("Single Segment Dimension")
        print ("Dim Value Readable = {}".format(dim.ValueString))
        print ("Dim Value Internal = {} ft".format(dim.Value))
    else:
        print ("{} Segments Found.".format(dim.NumberOfSegments))
        values = print_segement_value(dim)


#------------------main code below------------
sel_sheets = forms.select_sheets(title='Select Sheets That You Want To Check Dim Value.')

output = script.get_output()

seperation = "-----------------------------------------------------"

if sel_sheets:
    if len(sel_sheets) > 0:
        dims = get_dims_in_sheets(sel_sheets)
    else:
        forms.alert("No Sheet Selected. \nCancelled.")
        script.exit()
else:
    forms.alert("Cancelled")
    script.exit()

type_names = []
if len(dims)>0:

    for idx, dim in enumerate(dims):


        parent_view = dim.OwnerViewId

        print ("#{}: Dim Id = {}-->{}".format(idx+1,dim.Id,output.linkify(dim.Id, title = "Go To Dim")))

        #print ("Dim Value = {}".format(dim.Value))
        print_values(dim)

        #print dim.Parameters[DB.BuiltInParameter.SYMBOL_NAME_PARAM]
        current_dim_type = dim.DimensionType
        current_type_name = GetParamByName(current_dim_type,"Type Name").AsString()
        print("Type Name = " + str(current_type_name))
        if current_type_name not in type_names:
            type_names.append(current_type_name)

        try:
            print("Found in this view: {} :-->{}".format(revit.doc.GetElement(parent_view).ViewName,output.linkify(parent_view, title = "Go To View")))
        except:
            print("Found in this view: {} :-->{}".format(revit.doc.GetElement(parent_view).Name,output.linkify(parent_view, title = "Go To View")))
        print(seperation)


print('{0} Dim(s) FOUND IN SELECTED SHEETS.'.format(len(dims)))
print("{} kind(s) of dim types founds, listed below:".format(len(type_names)))
for item in type_names:
    print(item)

print("\n\nEA Note: \nI dont know if people want to see internal value or not. If you prefer to see no internal value, please submit your idea by 'reporting bugs' as feedback.\nIf you want to see other kind of information in the output window please also report as an idea.")
