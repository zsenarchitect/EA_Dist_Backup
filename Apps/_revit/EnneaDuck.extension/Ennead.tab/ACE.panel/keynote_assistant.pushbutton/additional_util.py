import os
import datetime

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
# import sys
# for i, path in enumerate(sys.path):
#     print("{}: {}".format(i+1, path))

from EnneadTab import ERROR_HANDLE, EXCEL, TEXT
# from EnneadTab import LOG
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()

import keynotesdb as kdb
from natsort import natsorted # pyright: ignore 
from collections import defaultdict

from pyrevit import forms

@ERROR_HANDLE.try_catch_error()
def batch_reattach_keynotes(keynote_data_conn):
    """
    Batch attach keynotes to selected elements in Revit.
    
    This function allows you to attach keynotes to selected elements in Revit.
    
    Args:
        keynote_data_conn: Database connection to the keynote data
        
    Returns:
        None
    """
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]<{}>: {}".format(self.parent_key, self.key, self.text)
    
    selected_keynotes = forms.SelectFromList.show(
        [MyOption(x) for x in kdb.get_keynotes(keynote_data_conn)],
        title='Select Keynote',
        multiselect=True,
        button_name="Pick keynotes to attach..."
        )
    
    if not selected_keynotes:
        return
    
    categories = kdb.get_categories(keynote_data_conn)
    keynotes = kdb.get_keynotes(keynote_data_conn)
    available_parents = [x.key for x in categories]
    available_parents.extend([x.key for x in keynotes])
   
    # prompt to select a record
    new_parent = forms.SelectFromList.show(
        natsorted(available_parents),
        title='Select New Parent',
        multiselect=False,
        button_name="Pick new parent to attach to..."
        )
    
    if not new_parent:
        return
    
    with kdb.BulkAction(keynote_data_conn):
        for keynote in selected_keynotes:
            try:
                if keynote.parent_key == new_parent:
                    print ("Forbidden to reattach [{}]:{} to same parent".format(keynote.key, keynote.text))
                    continue
                if keynote.key == new_parent:
                    print ("Forbidden to reattach [{}]:{} to itself".format(keynote.key, keynote.text))
                    continue
                original_parent = keynote.parent_key
                kdb.move_keynote(keynote_data_conn, keynote.key, new_parent)
                print ("Reattach [{}]:{} parent from [{}] to [{}]".format(keynote.key, keynote.text, original_parent, new_parent))
            except Exception as e:
                print ("Error reattaching [{}]:{} from [{}] to [{}]".format(keynote.key, keynote.text, original_parent, new_parent))
                print(e)


@ERROR_HANDLE.try_catch_error()
def translate_keynote():
    pass

@ERROR_HANDLE.try_catch_error()
def cleanup_quote_text(keynote_data_conn):
    """
    Clean up quote text in the keynote database.
    
    This function cleans up quote text in the keynote database by removing
    leading and trailing quotes in keynote text, if any quotes exist.
    
    Args:
        keynote_data_conn: Database connection to the keynote data
        
    Returns:
        None
    """
    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    bad_text_count = 0
    for keynote in all_keynotes:
        new_text = None
        if keynote.text.startswith('"') and keynote.text.endswith('"'):
            new_text = keynote.text[1:-1]
            bad_text_count += 1
        elif keynote.text.startswith("'") and keynote.text.endswith("'"):
            new_text = keynote.text[1:-1]
            bad_text_count += 1

        if new_text:
            print("{}: {} -> {}".format(keynote.key, keynote.text, new_text))
            kdb.update_keynote_text(keynote_data_conn, keynote.key, new_text)

    if bad_text_count > 0:
        print("{} Bad text found and cleaned up.".format(bad_text_count))
    else:
        print("No bad text found.")




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



def open_extended_db_excel():
    pass

class KeynoteExtendedData:
    def __init__(self, 
                 key,
                 keynote_text,
                 format = None,
                 division_number = None,
                 division_name = None,
                 section_number = None,
                 section_name = None,
                 product_number = None,
                 source = None,
                 product = None,
                 color = None,
                 finish = None,
                 size = None,
                 contact = None,
                 remarks = None,
                 ):
        self.key = key
        self.keynote_text = keynote_text
        self.format = format
        self.division_number = division_number
        self.division_name = division_name
        self.section_number = section_number
        self.section_name = section_name
        self.product_number = product_number
        self.source = source
        self.product = product
        self.color = color
        self.finish = finish
        self.size = size
        self.contact = contact
        self.remarks = remarks

    @staticmethod   
    def get_cloest_match(key, text, all_keys):
        """
        Get the closest match between a key and text.
        
        Args:
            key: The key to match against
            text: The text to match against
            
        Returns:
            The closest match between the key and text
        """
        # to-do: this need more consideration, like which direct to search from....
        return TEXT.fuzzy_search("{}:{}".format(key, text), all_keys)
    

if __name__ == "__main__":
    pass
