from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import *

__title__ = "Review\nTextnotes"
__doc__ = 'Nice! \nThis tool allow you to review the textnotes in sheets while comparing the text family types. '


def GetParamByName(el,name):
    for para in el.Parameters:
        #print para.Definition.Name #enable this to see what parameter is available
        if para.Definition.Name == name:
            #print "OK, found para ID" + str(para.Id)
            #return el.LookupParameter(name).Id # can be used to return para ID
            return para.AsString()



def get_textnotes_in_sheets(sheets):
    all_text_notes = []
    for sheet in sheets:
        viewports = sheet.GetAllViewports()
        for viewport in viewports:
            view_id = revit.doc.GetElement(viewport).ViewId
            text_notes_current_view = DB.FilteredElementCollector(revit.doc,view_id)\
              .OfCategory(DB.BuiltInCategory.OST_TextNotes)\
              .WhereElementIsNotElementType()\
              .ToElements()
            all_text_notes.extend(text_notes_current_view)
    return all_text_notes

#####################################_MAIN_CODE_#############################################
sel_sheets = forms.select_sheets(title='Select Sheets That You Want To Find Textnotes.')

output = script.get_output()

seperation = "---------------"

if sel_sheets:
    if len(sel_sheets) > 0:
        text_notes = get_textnotes_in_sheets(sel_sheets)
    else:
        forms.alert("No Sheet Slected. \nCancelled.")
        script.exit()
else:
    forms.alert("Cancelled")
    script.exit()


if len(text_notes)>0:
    type_names = []
    for idx, textnote in enumerate(text_notes):
        #id = textnote.Id

        #text_content = textnote.Parameter[DB.BuiltInParameter.TEXT_TEXT].AsString()
        text_content = textnote.Text
        parent_view = textnote.OwnerViewId

        print ("{}: Textnote Id = {}-->{}".format(idx+1,textnote.Id,output.linkify(textnote.Id, title = "Go To Textnote")))
        print("Text = " + text_content)
        #print "1: " + str(textnote.GetType())
        #print "2: " + str(textnote.TextNoteType)
        #print "3: " + str(textnote.TextNoteType.GetType())
        #print "4: " + str(textnote.TextNoteType.FamilyName)

        #temp = textnote.TextNoteType.GetParameters("Type Name")
        #print "5: " + str(len(temp)) + "_____" + str(temp[0])
        #temp_id = textnote.TextNoteType.LookupParameter("Type Name").Id
        #print "5.01 " + str(temp_id)
        #print "5.1: " + str(textnote.TextNoteType.GetParameters(temp_id))
        current_type_name = GetParamByName(textnote.TextNoteType,"Type Name")
        print ("Textnotes Type Name = {}").format(current_type_name)
        if current_type_name not in type_names:
            type_names.append(current_type_name)
        print("Found in this view: {} -->{}".format(revit.doc.GetElement(parent_view).ViewName,output.linkify(parent_view, title = "Go To View")))
        print(seperation)


print('{0} Textnote(s) Found In Selected Sheets.'.format(len(text_notes)))
print ("There are {} kind(s) of TextNote Used, Listed Below:".format(len(type_names)))
for item in type_names:

    output.print_md("**{}**".format( item))
#print "Select {} Above.".format(output.linkify(user_keynotes_tags.element_ids, title = "All Tags"))
