#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Extract program information from Excel and transfer target value based on program name."
__title__ = "Transfer In Excel Target"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXCEL, TEXT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
import re
from pyrevit import script

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

def formated_name(program_name):
    """Format program name by removing prefix pattern if it exists.
    
    Removes prefix pattern 'A1 - xxxxx' (capital letter, number, space, dash, space) 
    if present, otherwise returns original name.
    
    Args:
        program_name (str): The original program name
        
    Returns:
        str: Formatted program name with prefix removed if pattern exists
    """
    if not program_name:
        return program_name
    
    # Pattern: capital letter + number + space + dash + space + rest
    pattern = r'^[A-Z]\d+ - (.+)$'
    match = re.match(pattern, program_name)
    
    if match:
        # Return only the part after the pattern
        return match.group(1)
    
    # Return original if pattern not found
    return program_name


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def transfer_in_excel_target(doc):

    program_target_dict = get_program_target_dict()
    output = script.get_output()

    output.print_md("## Program Target Dict")
    table_data = []
    for item in sorted(program_target_dict.keys()):
        table_data.append([item, program_target_dict[item]])
    output.print_table(table_data, columns = ["Program", "Target"])
 
    print ("If your parater use value other than those above, it cannot find the target value.")


    t = DB.Transaction(doc, __title__)
    t.Start()
    
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    for area in all_areas:

        program_assigned = area.LookupParameter("Area_$Department_Program Type").AsString()
        if not program_assigned or program_assigned == "":
            program_assigned = "No program assigned"
   
        desired_program_area = program_target_dict.get(program_assigned)
        if not desired_program_area:
            comment = "Cannot find target value for program: [{}]".format(program_assigned)
            fuzzy_searach = TEXT.fuzzy_search(program_assigned, program_target_dict.keys())
            if fuzzy_searach:
                comment += " Did you mean: [{}]?".format(fuzzy_searach)
        else:   
            comment = "Target: " + desired_program_area

        if REVIT_SELECTION.is_changable(area):
            area.LookupParameter("Comments").Set(comment)
        else:
            print ("Cannot change area {} due to ownership by {}".format(output.linkify(area.Id, title = program_assigned), REVIT_SELECTION.get_owner(area)))

    t.Commit()

    print ("Done! All areas comments have been updated.\nAt the moment, there is not couting for how many itme of this same program used. Need a solution to for scheme indepedent.")
    

def get_program_target_dict():
    excel_path = "J:\\2151\\2_Master File\\B-70_Programming\\04_Area\\2025-03-06 Program Comparison 549 BED.xlsx"
    
    data = EXCEL.read_data_from_excel(excel_path, 
                                      worksheet="Hospital Program 549 bed",
                                      return_dict=True)


    B_index = EXCEL.letter_to_index("B") # try this col first, but it's not always the case, then try next col
    C_index = EXCEL.letter_to_index("C")
    out = {}
    for pointer in sorted(data.keys()):
        row, col = pointer
        col = EXCEL.column_number_to_letter(col)
        if col != "T":
            continue

        target_cell = data[pointer]
        target_cell_value = target_cell["value"]
        if not target_cell_value or target_cell_value == "" or target_cell_value == "None":
            continue

        program_name = data[row, B_index]["value"]
        if not program_name or program_name == "" or program_name == "None":
            program_name = data[row, C_index]["value"]

        program_name = formated_name(program_name)

        try:
            out[program_name] = str(int(target_cell_value)) + " SF"
        except:
            pass
            # print (program_name, target_cell_value)
            # ignore some non-number cell such as target/Factor

    
    return out






################## main code below #####################
if __name__ == "__main__":
    transfer_in_excel_target(DOC)







