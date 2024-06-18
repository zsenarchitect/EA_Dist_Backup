#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__doc__ = "try to place alot of text boxs.\nUse in the starting sync view or 1:1 view"
__title__ = "Deploy all text types"

SAMPLE_TEXT = "THE QUICK BROWN FOX JUMPS OVER A LAZY DOG."
SAMPLE_TEXT += "\nthe quick brown fox jumps over a lazy dog."
SAMPLE_TEXT += "\n0123456789    ,.?!@#$%&;[]()<>"

"""
need to add parts where the view scale can be factored to the textnote spacing
"""




def print_para(element):
    print('------')
    for para in element.Parameters:
        print("{}--->{}".format(para.Definition.Name, para.AsValueString()))
    print("-----------\n\n")

def print_table(list):
    table_data = []
    for item in list:
        #print_para(item)
        type_name = item.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
        text_background = item.LookupParameter("Background").AsValueString()
        text_size = item.LookupParameter("Text Size").AsValueString()

        """
        print(item.LookupParameter("Color"))
        print(item.LookupParameter("Color").AsElementId())
        print(item.LookupParameter("Color").AsDouble())
        print(item.LookupParameter("Color").AsString())
        print(item.LookupParameter("Color").AsValueString())
        """
        """
        print(item.Parameter[DB.BuiltInParameter.TEXT_COLOR].GetType())

        color_r = item.Parameter[DB.BuiltInParameter.TEXT_COLOR].Color.Red
        color_g = item.LookupParameter("Color").Color.Green
        color_b = item.LookupParameter("Color").Color.Blue
        text_color = "({},{},{})".format(color_r,color_g,color_b)
        """
        #print item.Parameter[DB.BuiltInParameter.TEXT_COLOR].AsInteger()
        #print item.LookupParameter("Italic").AsInteger()
        text_line_weight = item.LookupParameter("Line Weight").AsValueString()
        text_width_factor = item.LookupParameter("Width Factor").AsValueString()
        text_font = item.LookupParameter("Text Font").AsString()
        text_tabsize = item.LookupParameter("Tab Size").AsValueString()
        text_underline = "Underline" if item.LookupParameter("Underline").AsInteger() == 1 else "No"
        text_italic = "Italic" if item.LookupParameter("Italic").AsInteger() == 1 else "No"
        text_bold = "Bold" if item.LookupParameter("Bold").AsInteger() == 1 else "No"
        text_border = "Border" if item.LookupParameter("Show Border").AsInteger() == 1 else "No"
        text_leaderarrow = item.LookupParameter("Leader Arrowhead").AsValueString()

        temp_data = [type_name,text_size,text_background,text_width_factor,text_font,text_tabsize,text_leaderarrow,text_line_weight,text_underline,text_italic,text_bold,text_border]
        table_data.append(temp_data)

    output.print_table(table_data=table_data,
                    title="Textnote Styles Rank By Size",
                    columns=[ "Type Name", "Size", "Background", "Width Factor","Font", "Tab Size","Leader Arrow","Line Weight","Under Line","Italic","Bold","Border"],
                    formats=['', '', '', ''])


def create_along_Y(location_start, type_list):
    out = []
    location_last = location_start
    for i in range(len(type_list)):
        '''
        try:
            type_height = type_list[i - 1].LookupParameter("Text Size").AsDouble()
        except:
            type_height = 0
        print(type_height)
        print(DB.UnitUtils.ConvertToInternalUnits( 2, DB.DisplayUnitType.DUT_MILLIMETERS))
        step_dist = DB.UnitUtils.ConvertToInternalUnits( type_height * 4, DB.DisplayUnitType.DUT_MILLIMETERS)##multiple by 3 becasue there are three lines in the sampelk text, then convert to internal value
        print(step_dist)
        print(type_height * 3)
        print("```````")
        step_vector = step_dist * -1 * revit.active_view.UpDirection
        #step_vector = 5 * type_height * -1 * revit.active_view.UpDirection
        '''


        if i >= 1:
            type_height_last = type_list[i - 1].LookupParameter("Text Size").AsDouble()#those height are in internal value
        else:
            type_height_last = 0
        #print type_height
        gap = DB.UnitUtils.ConvertToInternalUnits( 10, DB.DisplayUnitType.DUT_MILLIMETERS)#how much 4mm is to revit internal value

        #step_dist = DB.UnitUtils.ConvertFromInternalUnits( type_height_last * 8, DB.DisplayUnitType.DUT_MILLIMETERS)##multiple by 3 becasue there are three lines in the sampelk text, then convert to internal value
        #print step_dist
        #print type_height * 3
        #print "```````"
        #step_vector = step_dist * -1 * revit.active_view.UpDirection
        step_vector = (gap + 10 * type_height_last) * -1 * revit.active_view.UpDirection

        #print_para( type_list[i] )
        #print '%%%'
        type_name = type_list[i].Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
        text_size = type_list[i].LookupParameter("Text Size").AsValueString()
        #display_text = "<Text Style Name: {}>\n{}\n".format(type_name, "_" * (len(type_name) + 20)) + SAMPLE_TEXT
        display_title = "<Text Style Name: {}><Text Size: {}>".format(type_name, text_size)
        display_text = "{}\n{}\n{}".format(display_title, "_" * len(display_title), SAMPLE_TEXT)

        location_now = location_last + step_vector
        textnote_temp = DB.TextNote.Create(revit.doc, revit.active_view.Id, location_now, display_text, type_list[i].Id)
        out.append(textnote_temp)

        location_last = location_now
    #for item in type_list, create one instance based on last location and step vector and type
    return out
############## main code below ################
output = script.get_output()
output.self_destruct(220)

if __name__ == "__main__":
        
    forms.alert("For best result, it is suggested to deply at 1:1 scale drafting view, for example, at 'Sync and Close' starting view")
    # get the starting box
    selection = revit.get_selection()

    if len(selection) != 1 or isinstance(selection[0], DB.TextNote) == False:
        forms.alert("Please select only one textnotes as the begining location for the deploy.")
        script.exit()

    location_ref = selection[0].Coord
    '''
    print(location_ref.X)
    print(location_ref.Y)
    print(location_ref.Z)
    '''

    type_list_raw = DB.FilteredElementCollector(revit.doc).OfClass(DB.TextNoteType).WhereElementIsElementType().ToElements()

    '''
    for x in type_list:
        print(x)
        print(x.GetType())
        print(x.LookupParameter("Text Size").AsDouble())

    print("~~~~~~~~~")
    print(type_list)
    print(list(type_list))
    '''
    type_list = list(type_list_raw)
    type_list.sort(key = lambda x: x.LookupParameter("Text Size").AsDouble(), reverse = False)
    '''
    for x in type_list:
        print_para(x)

    print("~~~~~~~~~")
    '''


    with revit.Transaction("Deploy Textnote Samples"):
        deploy_collection = create_along_Y(location_ref,type_list)


        #get information from deploy_collection
        #print (x for x in deploy_collection)

    print_table(type_list)
