#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
import EA_UTILITY
import EnneadTab
output = script.get_output()
output.close_others()

__title__ = "Track Warnings"
__doc__ = 'Get Clickable Warnings.'



def process_warning(warning):
    print ("#{0} {1}:".format(counter, warning.GetSeverity()))
    #print warning.ToString()
    print warning.GetDescriptionText()




    error_els = warning.GetFailingElements()

    for error_el in error_els:
        #if hasattr(error_el, "Category"):
        try:
            category = error_el.Category.Name
        except:
            category = "None"
        #category = error_el.Category.Name if hasattr(error_el. "Category") else "None"
        #print ("Element Id = {0}-->{1}. Category = {2}".format(error_el,output.linkify(error_el, title = "Go To Element"), category))
        print ("Element Id = {} {}-->{}.".format(error_el , EA_UTILITY.get_element_full_info(revit.doc.GetElement(error_el), output), output.linkify(error_el, title = "Go To Element")))
    #print warning.GetType()

    try:
        print ("Try {}.".format(warning.GetDefaultResolutionCaption()))
    except:
        pass
        #print "There are No default Resolution."


    #script.insert_divider(level = "")
    print "-------------------------------------"

class w_dict:
    def __init__(self, description):
        self.description = description
        self.count = 1

    def new_data(self):
        self.count += 1



#-------------main code below-------------

if __name__== "__main__":
    #output.freeze()
    counter = 0
    all_warnings = revit.doc.GetWarnings()
    unique_warning_description = set() #used to
    warning_dicts = []
    for warning in all_warnings:
        counter += 1
        #process_warning(warning)
        #print warning.GetDescriptionText()
        current_description = warning.GetDescriptionText()
        if current_description not in unique_warning_description:
            warning_dicts.append(w_dict(current_description))
            unique_warning_description.add(current_description)
        else:
            for w in warning_dicts: # update count number only for those existing warning
                if current_description == w.description:
                    w.new_data()


    #print unique_warning_description
    #print len(unique_warning_description)
    #print warning_dicts

    select_list = []
    for item in warning_dicts:
        #print item.description
        #print item.count
        select_list.append("{" + str(item.count) + "}: " + str(item.description))
    #output.unfreeze()


    selected_warnings_raw = forms.SelectFromList.show(select_list, title = "Select the warnings you want to expand.", button_name='Select Warnings',multiselect  = True)

    #print selected_warnings_raw


    if selected_warnings_raw == None:
        script.exit()

    if len(selected_warnings_raw) == 0:
        script.exit()

    selected_warnings = []
    for item in selected_warnings_raw:
        selected_warnings.append(item.split("}: ")[1])
    #print selected_warnings

    output.freeze()
    counter = 1
    try:
        def get_view_name(x):
            z = x.GetFailingElements()[0]
            return doc.GetElement(z.OwnerViewId ).Name
        all_warnings.sort(key = lambda x: get_view(x))
    except:
        pass
    for warning in all_warnings:
        if warning.GetDescriptionText() in selected_warnings:
            process_warning(warning)
            counter += 1
    output.unfreeze()


    print ("There are totally {} warnings in the projects.\nCurrently reviewing {} warnings".format(len(all_warnings), counter))






    #output.open_url("https://knowledge.autodesk.com/support/revit-products/troubleshooting/caas/CloudHelp/cloudhelp/2019/ENU/Revit-Troubleshooting/files/GUID-F0945713-4389-4F8E-B5DB-DCE03A8C1ADF-htm.html")
