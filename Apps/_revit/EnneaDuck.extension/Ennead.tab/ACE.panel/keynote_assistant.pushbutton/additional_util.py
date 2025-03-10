import os
import datetime

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
# import sys
# for i, path in enumerate(sys.path):
#     print("{}: {}".format(i+1, path))

from EnneadTab import ERROR_HANDLE, EXCEL
# from EnneadTab import LOG
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()

import keynotesdb as kdb
from natsort import natsorted
from collections import defaultdict

@ERROR_HANDLE.try_catch_error()
def batch_attach_keynotes():
    pass

@ERROR_HANDLE.try_catch_error()
def rename_parent_key():
    pass

@ERROR_HANDLE.try_catch_error()
def translate_keynote():
    pass

@ERROR_HANDLE.try_catch_error()
def export_keynote(keynote_data_conn):
    """
    Export keynotes from 'Exterior' and 'Interior' categories to separate Excel files.
    
    Creates a hierarchically organized Excel file with keynotes grouped by category
    and branch. Includes proper formatting for improved readability.
    
    Args:
        keynote_data_conn: Database connection to the keynotes database
        
    Returns:
        Path to generated Excel file
    """
    # print ("\n== ALL KEYNOTES ==")
    # for x in all_keynotes:
    #     print(x.key, x.text, x.parent_key)



    # Get the full keynote tree
    categorys = [x for x in kdb.get_categories(keynote_data_conn) if x.key.upper() in ["EXTERIOR", "INTERIOR"]]

    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    for cate in categorys:
        data_collection = []
        pointer_row = 0
        data_collection.append(EXCEL.ExcelDataItem("Keynote ID", pointer_row, "B", cell_color=(200, 200, 200), 
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("Keynote Description", pointer_row, "C", cell_color=(200, 200, 200), 
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        print("\n== CATEGORY: {} ==".format(cate.key))
        top_branch = [x for x in all_keynotes if x.parent_key == cate.key]
        print ("\tTop branchs in {}".format(cate.key))
        for i, branch in enumerate(top_branch):
            pointer_row += 2 # skip 2 for adding empty line
            bran_name = branch.text
            if len(bran_name) == 0:
                bran_name = "UnOrganized"
            data_collection.append(EXCEL.ExcelDataItem(bran_name, pointer_row, "B", is_bold=True))
            print("\t\t{}: [{}] {}".format(i+1,branch.key, branch.text))
            leafs = [x for x in all_keynotes if x.parent_key == branch.key]
            for j, leaf in enumerate(leafs):
                pointer_row += 1
                data_collection.append(EXCEL.ExcelDataItem(leaf.key, pointer_row, "B",
                                                           top_border_style=1, side_border_style=1, bottom_border_style=1))
                data_collection.append(EXCEL.ExcelDataItem(leaf.text, pointer_row, "C",
                                                           top_border_style=1, side_border_style=1, bottom_border_style=1))
                print("\t\t\t{}-{}: [{}] {}".format(i+1, j+1, leaf.key, leaf.text))
                

        # Create output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "EnneadTab_KeynoteExport")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        excel_file = os.path.join(output_dir, "Keynotes_{}_{}.xlsx".format(cate.key, timestamp))
        EXCEL.save_data_to_excel(data_collection, excel_file, worksheet=cate.key, freeze_row=1)




def _collect_keynotes(root_keynote):
    """
    Recursively collect all keynotes under a root keynote.
    
    Args:
        root_keynote: The root keynote to collect from
        
    Returns:
        List of keynotes under this root
    """
    keynotes = [root_keynote]
    for child in root_keynote.children:
        keynotes.extend(_collect_keynotes(child))
    return keynotes

def _prepare_excel_data(keynotes):
    """
    Format keynote data as ExcelDataItem objects for Excel export.
    
    Args:
        keynotes: List of keynote objects to format
        
    Returns:
        List of ExcelDataItem objects ready for Excel export
    """
    
    # Create header row with formatting
    header_color = (200, 200, 200)  # Light gray
    data_items = [
        EXCEL.ExcelDataItem("Key", 0, 0, cell_color=header_color, border_style=1),
        EXCEL.ExcelDataItem("Description", 0, 1, cell_color=header_color, border_style=1),
        EXCEL.ExcelDataItem("Parent", 0, 2, cell_color=header_color, border_style=1),
        EXCEL.ExcelDataItem("Used", 0, 3, cell_color=header_color, border_style=1)
    ]
    
    # Add data rows
    for i, keynote in enumerate(keynotes, 1):
        # Alternate row colors for readability
        bg_color = (240, 240, 240) if i % 2 == 0 else None
        
        # Add basic keynote data
        data_items.append(EXCEL.ExcelDataItem(keynote.key, i, 0, cell_color=bg_color))
        data_items.append(EXCEL.ExcelDataItem(keynote.text, i, 1, cell_color=bg_color))
        data_items.append(EXCEL.ExcelDataItem(keynote.parent_key, i, 2, cell_color=bg_color))
        
        # Add usage information with color coding
        if keynote.used:
            usage_text = "Yes ({0})".format(keynote.used_count)
            usage_color = (200, 255, 200)  # Light green
        else:
            usage_text = "No"
            usage_color = None
        
        data_items.append(EXCEL.ExcelDataItem(usage_text, i, 3, cell_color=usage_color))
    
    return data_items


if __name__ == "__main__":
    pass
