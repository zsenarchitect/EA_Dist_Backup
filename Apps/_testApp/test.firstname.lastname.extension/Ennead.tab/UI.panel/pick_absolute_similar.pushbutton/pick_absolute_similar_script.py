#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "PIck one element, and this tool will pick all the elements that are absolutely similar to the first one."
__title__ = "Pick\nAbsolute Similar"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB, UI # pyright: ignore 
import traceback
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import forms

def is_instance_absolute_similar_with_sample(instance, sample, picked_parameter_names):


    for para in instance.Parameters:
        para_name = para.Definition.Name
        if para_name not in picked_parameter_names:
            continue
        try:
            # Get the corresponding parameter from sample
            sample_param = sample.LookupParameter(para_name)
            if not sample_param:
                return False
                
            # Get storage type to avoid trying unnecessary conversions
            storage_type = para.StorageType
            
            if storage_type == DB.StorageType.Integer:
                if para.AsInteger() != sample_param.AsInteger():
                    return False
            elif storage_type == DB.StorageType.Double:
                if para.AsDouble() != sample_param.AsDouble():
                    return False
            elif storage_type == DB.StorageType.String:
                if para.AsString() != sample_param.AsString():
                    return False
            elif storage_type == DB.StorageType.ElementId:
                if para.AsElementId() != sample_param.AsElementId():
                    return False
        except:
            print (traceback.format_exc())
            return False
        return True


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def pick_absolute_similar(doc):
    

    selected_instances = REVIT_SELECTION.get_selection(UIDOC)
    if len(selected_instances) != 1:
        NOTIFICATION.messenger("Need to have exactly one selection")
        return
        
   
    selected_instance = selected_instances[0]
    all_parameters_names = [para.Definition.Name for para in selected_instance.Parameters]
    all_parameters_names.sort()
    picked_parameter_names = forms.SelectFromList.show(all_parameters_names, 
                                                       multiselect=True,
                                                       title="Pick which parameter to guide against.")

    if not picked_parameter_names:
        NOTIFICATION.messenger("No parameter selected")
        return 

    whole_selection = []
   
    # get all instance in the project that is the same family and type as instance
    type_filter = DB.FamilyInstanceFilter (doc, selected_instance.GetTypeId())
    filtered_collector = DB.FilteredElementCollector(doc)

    all_raw_similar_instances = list(filtered_collector.OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())

    for element in all_raw_similar_instances:
        if is_instance_absolute_similar_with_sample(element, selected_instance, picked_parameter_names):
            whole_selection.append(element)

                
    REVIT_SELECTION.set_selection(whole_selection)
    NOTIFICATION.messenger("{} elements of absolute similar selected in the project.".format(len(whole_selection)))
                    

  


################## main code below #####################
if __name__ == "__main__":
    pick_absolute_similar(DOC)







