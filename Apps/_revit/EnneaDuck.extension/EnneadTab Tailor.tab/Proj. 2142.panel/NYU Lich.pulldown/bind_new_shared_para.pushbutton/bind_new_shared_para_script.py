#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Bind new shared parameters to Room category from Excel file. Requires a worksheet named 'Shared Paras To Add' with parameter names and types. User selects which columns contain parameter names and parameter types during execution. Those parameters will be added to the project document and bind to Room category. Let me know if you want to bind to other categories."
__title__ = "Bind New Shared Para"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXCEL
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PARAMETER, REVIT_UNIT, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def read_excel_to_param_dict():
    """Ask user for Excel file and convert to parameter dictionary
    
    Returns:
        tuple: (parsed_data, param_type_header) where parsed_data is from parse_excel_data
    """
    # Ask user for Excel file path
    from pyrevit import forms
    excel_file = forms.pick_file(file_ext='xlsx')
    if not excel_file:
        REVIT_FORMS.dialogue(main_text="No Excel file selected.", options=["OK"])
        return None, None
        
    # Read Excel data using EnneadTab EXCEL module
    try:
        # Read raw Excel data
        raw_data = EXCEL.read_data_from_excel(excel_file, return_dict=True, worksheet="Shared Paras To Add")
        if not raw_data:
            REVIT_FORMS.dialogue(main_text="Failed to read Excel file or file is empty.", options=["OK"])
            return None, None
            
        # Let user select which worksheet if needed
        # For now, assume first worksheet is used (handled by read_data_from_excel)
        
        # Get headers to help user identify the parameter name column
        header_map = EXCEL.get_header_map(raw_data, header_row=1)
        header_names = list(header_map.values())
        
        if not header_names:
            REVIT_FORMS.dialogue(main_text="No headers found in Excel file.", 
                               sub_text="Make sure row 1 contains column headers.", 
                               options=["OK"])
            return None, None
            
        # Ask user which column contains parameter names
        param_name_header = REVIT_FORMS.dialogue(
            main_text="Select Parameter Name Column",
            sub_text="Which column contains the parameter names?",
            options=header_names
        )
        
        if not param_name_header or param_name_header == "Close":
            REVIT_FORMS.dialogue(main_text="No parameter name column selected.", options=["OK"])
            return None, None
            
        # Use parse_excel_data to convert to structured format
        # This will use the selected column as the key
        parsed_data = EXCEL.parse_excel_data(raw_data, param_name_header, header_row=1)
        
        if not parsed_data:
            REVIT_FORMS.dialogue(main_text="No data found using '{}' as key column.".format(param_name_header), 
                               options=["OK"])
            return None, None
            
        # Ask user which column contains parameter types
        remaining_headers = [h for h in header_names if h != param_name_header]
        if not remaining_headers:
            REVIT_FORMS.dialogue(main_text="Need at least 2 columns.", 
                               sub_text="One for parameter names and one for parameter types.", 
                               options=["OK"])
            return None, None
            
        param_type_header = REVIT_FORMS.dialogue(
            main_text="Select Parameter Type Column",
            sub_text="Which column contains the parameter types?",
            options=remaining_headers
        )
        
        if not param_type_header or param_type_header == "Close":
            # Default to first remaining column if user cancels
            param_type_header = remaining_headers[0]
            REVIT_FORMS.dialogue(main_text="No parameter type column selected.", 
                               sub_text="Using '{}' as default.".format(param_type_header), 
                               options=["OK"])
        
        return parsed_data, param_type_header
        
    except Exception as e:
        REVIT_FORMS.dialogue(main_text="Error reading Excel file.", 
                           sub_text=str(e), 
                           options=["OK"])
        return None, None


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def bind_new_shared_para(doc):
    """Main function to bind new shared parameters from Excel to Room category"""
    
    # Get parsed data and type header from Excel
    parsed_data, param_type_header = read_excel_to_param_dict()
    
    if not parsed_data or not param_type_header:
        return
    
    # Show user what parameters will be created
    param_list = []
    for param_name, row_data in parsed_data.items():
        param_type = row_data.get(param_type_header, 'Text')
        param_list.append("{}: {}".format(param_name, param_type))
    
    message = "The following parameters will be added to Room category:\n\n" + "\n".join(param_list)
    
    # Ask for confirmation
    result = REVIT_FORMS.dialogue(main_text="Confirm Parameter Binding", 
                                 sub_text=message, 
                                 options=["Yes, add parameters", "No, cancel"])
    
    if result != "Yes, add parameters":
        return
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    try:
        # Get room category
        room_category = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Rooms)
        if not room_category:
            REVIT_FORMS.dialogue(main_text="Room category not found in this document.", options=["OK"])
            t.RollBack()
            return
            
        successful_params = []
        failed_params = []
        
        # Process each parameter directly from parsed data
        for param_name, row_data in parsed_data.items():
            try:
                # Get parameter type from the row data
                param_type_str = row_data.get(param_type_header, 'Text')
                
                # Convert string type to SpecTypeId using REVIT_PARAMETER function
                param_type = REVIT_PARAMETER.get_parameter_type_from_string(param_type_str)
                
                # Try to get existing shared parameter definition
                definition = REVIT_PARAMETER.get_shared_para_definition_in_txt_file_by_name(doc, param_name)
                
                # If not found, create new one
                if not definition:
                    definition = REVIT_PARAMETER.create_shared_parameter_in_txt_file(doc, param_name, param_type)
                
                # Add to project document bound to Room category
                success = REVIT_PARAMETER.add_shared_parameter_to_project_doc(
                    doc, 
                    definition, 
                    "Data", 
                    [room_category],
                    is_instance_parameter=True
                )
                
                if success:
                    successful_params.append(param_name)
                else:
                    failed_params.append(param_name)
                    
            except Exception as e:
                failed_params.append("{} (Error: {})".format(param_name, str(e)))
        
        # Show results
        result_message = "Parameter binding complete!\n\n"
        if successful_params:
            result_message += "Successfully added {} parameters:\n".format(len(successful_params))
            for param in successful_params:
                result_message += "- {}\n".format(param)
        
        if failed_params:
            result_message += "\nFailed to add {} parameters:\n".format(len(failed_params))
            for param in failed_params:
                result_message += "- {}\n".format(param)
        
        REVIT_FORMS.dialogue(main_text="Results", sub_text=result_message, options=["OK"])
        
        t.Commit()
        
    except Exception as e:
        t.RollBack()
        REVIT_FORMS.dialogue(main_text="Transaction failed.", sub_text=str(e), options=["OK"])


################## main code below #####################
if __name__ == "__main__":
    bind_new_shared_para(DOC)







