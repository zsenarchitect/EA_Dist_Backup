__doc__ = "xxxxxxxx "
__title__ = "Cross Compare\nTemplate"

from pyrevit import DB, revit, script, forms
"""
user select several view template, possible from link even? and find parts in the template setting that is "checked" to apply all views, that has difference in the template selected, only print those differnt parts in a table format
"""

def find_para_that_checkstatus_is_unique(templates_selected):
    all_template_paras = set(templates_selected[0].GetTemplateParameterIds())
    #View.GetNonControlledTemplateParameterIds()
    #View.GetTemplateParameterIds()
    count = 0
    for template in templates_selected:
        count +=1
        checked_paras = template.GetNonControlledTemplateParameterIds()
        if count == 1:
            unique = set(checked_paras)
            continue
        unique.symmetric_difference(set(checked_paras))


    return list(all_template_paras - unique)

def pick_template_from_link(doc):
    all_views_raw = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    all_templates = []
    for view in all_views_raw:
        if view.IsTemplate == True:
            all_templates.append(view)

    """
    print("~~~~~")
    for view in all_templates:
        print(view.Name)
    print("~~~~~")
    """

    #[x.Name for x in all_templates]]
    select = forms.SelectFromList.show(all_templates, button_name='Select Additional Templates', multiselect = True, name_attr = "Name")
    #print select

    """
    for x in select:
        print(x.Name)
    """

    return select




def count_template(views,templates):
    dict = {}
    template_ids = [x.Id for x in templates]
    for view in views:
        if view.ViewTemplateId in template_ids:

            current_template_name = revit.doc.GetElement(view.ViewTemplateId).Name
            if current_template_name in dict:
                dict[current_template_name] += 1
                ####append to the value list
            else:
                dict[current_template_name] = 1
                ####maybe make those value as list so it can be printed later


            #print dict[revit.doc.GetElement(view.ViewTemplateId).Name]

    #print list(dict)
    print("~~~~~~~~~ template usage counts ~~~~~~~~~")
    for key in dict:
        print("{} = {} counts".format(key, dict[key]))
        #print "{} = {}".format(item.keys, item.value)

    ####### maybe should display all the view with it instead of just the count
    pass

#####################  main code below ##############

#use pyrevit to select multiple Template
templates_selected = forms.select_viewtemplates(title = "Select Templates to Compare", button_name = "Go!", width = 400, multiple = True, doc = None, filterfunc = None)
#doc can be used to get template from another doc!!!!!!!!!!!!!!!!
if templates_selected == None:
    forms.alert("No template selected.")
    script.exit()




revit_links = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()


if len(revit_links) != 0:
    result = forms.alert(msg = "Revit Links found", sub_msg = "There are also revit links found, do you want to select template from those as well?", title = "Wait...", footer = "Test Footer", yes = True, no = True, warn_icon = False )
    if result == True:
        link_name_selected = forms.ask_for_one_item([x.GetLinkDocument().Title for x in revit_links], default = revit_links[0].GetLinkDocument().Title,prompt = "Pick the additional revit link.", title = "additional templates..")

        if link_name_selected == None:
            forms.alert("No additional revit links selected, will use cuurent document only.")
        else: #link selected has value, now process the document to select template from this link
            for link in revit_links:
                if link.Name == link_name_selected:
                    break
            link_doc = link.GetLinkDocument()

            """
            print(revit.doc)
            print(link_doc)
            print(link_doc.Title)
            print("~~~~~~~~~~~~~")
            """

            link_templates_selected = pick_template_from_link(link_doc)


            #link_templates_selected = forms.select_viewtemplates(title = "Select Templates to Compare", button_name = "Go!", width = 600, multiple = True, doc = link_doc, filterfunc = None)

            if link_templates_selected == None:#user fail to pick any templater from this link revit
                forms.alert("No additional template in the revit links selected, will use cuurent templates selection only.")
            else:#user successfully picked addtiontal templates from the link
                templates_selected.extend(link_templates_selected)
    else : # result == Fasle, dont want to get additional links files..
        pass

else:# there are no revit links found, no need to select additional templater
    pass

if len(templates_selected) < 2:
    forms.alert("You need to select at least 2 templates in total to compare.\nNow cancelling.")
    script.exit()

for x in templates_selected:
    print(x.Name)







#for each template selected, get how many views each is being used in current doc.
#View.ViewTemplatedId ------->!!
all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
count_template(all_views, templates_selected)


#get all template info that is checked, and then unchecked.
unique_checked_paras = find_para_that_checkstatus_is_unique(templates_selected)

for x in unique_checked_paras:
    print(x)
    print(revit.doc.GetElement(DB.ElementId(x)))
    print(revit.doc.GetElement(x).Name)
print (x.Name for x in unique_checked_paras)

"""
no this is not good, better to see the whole thing which is chefcked or not, not just the checked item.
hoever the set math intersection can be used for category searchs
"""





# do unchecked to display first to the user first in red in table that those are not being checked, while soe other might be.
#the detailed table is a speperated table so it si good to read.



# check for main display difference, then each inner tab display setting


#for item in template content, if all graphical setting are same, including visibility setting and halftone, then ignore this item in template. other wise append the each version tot a data list that will print latter




#out put data in table, there will be many table


#tel people to save the output window as excel.
