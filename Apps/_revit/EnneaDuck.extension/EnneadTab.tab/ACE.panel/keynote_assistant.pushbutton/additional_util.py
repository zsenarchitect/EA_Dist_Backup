import os
import datetime

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
# import sys
# for i, path in enumerate(sys.path):
#     print("{}: {}".format(i+1, path))

from EnneadTab import    EXCEL , NOTIFICATION, AI, TEXT, OUTPUT
# from EnneadTab import LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PROJ_DATA
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()

import keynotesdb as kdb
from natsort import natsorted # pyright: ignore 


from pyrevit import forms, script




def show_help():

    output = OUTPUT.get_output()
    output.write("What to do if:", OUTPUT.Style.Title)
    output.insert_divider()
    output.write("1. You are about to setup on a new project:", OUTPUT.Style.Subtitle)
    output.write("   - 1. Make sure your current keynote file is pointed at project folder, not from public template folder.")
    output.write("   - 2. (Optional, if you have existing keynote file you want to merge to the current list)Click on \"Import Keynote\" button to merge another file into current file.")
    output.write("   - 3. (Optional, if you have some legacy quote mark around the description.)Click on \"Cleanup quota mark around description\" button to cleanup them.")
    output.write("   - 4. Click on \"Edit Extend DB Excel\" button to pick a loocation for the extended DB excel file. This will be the file storing all your ohter product information. The address will be recorded for future use.")
    output.write("   - 5. Click on \"Export Keynote as Excel\" button to pick a loaction to save your keynote as two separate excel files, one for exterior and one for interior. Those locations will be recorded for future use.")
    output.write("      - You can use those two excel file to sticky link as schedule in Revit.")
    output.insert_divider()

    
    output.write("2. You are about to work with existing keynote setup:", OUTPUT.Style.Subtitle)
    output.write("   - 1. How to add a new keynote:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Add Keynote\" button to add a new keynote to the current list.")
    output.write("      - Click on \"Pick Parent\" button to attach it to a new parent.")
    output.write("   - 2. How to edit an exsiting keynote:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Edit Keynote\" button to edit an exsiting keynote.")
    output.write("      - Click on \"Pick Parent\" button to attach it to a new parent.")
    output.write("   - 3. How to reattach multiple keynotes to a new parent:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Reattach Keynotes\" button to reattach multiple keynotes to a new parent.")
    output.write("      - Select the keynotes you want to reattach.")
    output.write("      - Select the new parent to attach to.")
    output.write("   - 4. How to translate single keynote description:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Edit Keynote\" button to open the keynote description.")
    output.write("      - Click on \"Translate Keynote\" button to translate the keynote description.")
    output.write("   - 5. How to translate all keynote descriptions:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Batch Translate Keynote\" button to translate the keynote description.")
    output.write("   - 6. How to export for Exterior and Interior excel:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Export Keynote as Excel\" button to export the keynote as two separate excel files, one for exterior and one for interior.")
    output.write("   - 7. How to edit extended DB excel:", OUTPUT.Style.SubSubtitle)
    output.write("      - Click on \"Edit Extend DB Excel\" button to open the extended DB excel file.")
    output.write("      - Edit as you prefer, the primary area to change is the Exterior and Interior category.")

    output.insert_divider()
    output.write("Why this way?", OUTPUT.Style.Subtitle)
    output.write("   - Revit keynote file is organized in a tree structure by autodesk, for each keynote item, it will looks like this:")
    output.write("   - KEY | DESCRIPTION | PARENT KEY")
    output.write("   - So when you want to organize under a 'folder', you are really just assigning many keynote items to the same parent.")
    
    output.insert_divider()
    pyrevit_help = "https://pyrevitlabs.notion.site/Manage-Keynotes-6f083d6f66fe43d68dc5d5407c8e19da"
    output.write("Need more information about the original pyRevit keynote function?", OUTPUT.Style.Subtitle)
    output.write(pyrevit_help, OUTPUT.Style.Link)
    
    output.plot()

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
        [MyOption(x) for x in get_leaf_keynotes(keynote_data_conn)],
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



def batch_translate_keynote(keynote_data_conn):
    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    input_texts = [TEXT.strip_chinese(x.text) for x in all_keynotes if x.text]
    print ("Going to translate those descriptions:")
    for x in input_texts:
        print (x)
    result_dict = AI.translate_multiple(input_texts)
    if not result_dict:
        print ("No result from translation, usally due to missing api key, please check your api key")
        return
    print ("\n\n\n\n\nResult:")
    for x in result_dict:
        print ("\t{} --> {}".format(TEXT.strip_chinese(x), result_dict[x]))
    with kdb.BulkAction(keynote_data_conn):
        for keynote in all_keynotes:
            if result_dict.get(keynote.text):
                final_text = TEXT.strip_chinese(keynote.text) + " " + result_dict.get(keynote.text)
                kdb.update_keynote_text(keynote_data_conn, keynote.key, final_text)
    

def translate_keynote(input):
    return input + " " + AI.translate(input)





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




def get_leaf_keynotes(keynote_data_conn):
    OUT = []
    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    all_categories = kdb.get_categories(keynote_data_conn)
    for category in all_categories:
        top_branch = [x for x in all_keynotes if x.parent_key == category.key]
        for branch in top_branch:
            leafs = [x for x in all_keynotes if x.parent_key == branch.key]
            for leaf in leafs:
                OUT.append(leaf)
    return OUT

def export_keynote_as_exterior_and_interior(keynote_data_conn):
    """
    Export keynotes from 'Exterior' and 'Interior' categories to separate Excel files.
    
    Creates a hierarchically organized Excel file with keynotes grouped by category
    and branch. Includes proper formatting for improved readability.
    
    Args:
        keynote_data_conn: Database connection to the keynotes database
        
    Returns:
        Path to generated Excel file
    """
    doc = REVIT_APPLICATION.get_doc()
    t = DB.Transaction(doc, "edit extended db excel")
    t.Start()
    REVIT_PROJ_DATA.setup_project_data(doc)
    t.Commit()
    project_data = REVIT_PROJ_DATA.get_revit_project_data(doc)
    extend_db_path = project_data.get("keynote_assistant", {}).get("setting", {}).get("extended_db_excel_path")
    if extend_db_path and os.path.exists(extend_db_path):
        db_data = EXCEL.read_data_from_excel(extend_db_path, 
                                             worksheet="Keynote Extended DB", 
                                             return_dict=True)

        db_data = EXCEL.parse_excel_data(db_data, "KEYNOTE ID", ignore_keywords=["[Branch]", "[Category]"])
       
    else:
        db_data = {}



    # Get the full keynote tree
    categorys = [x for x in kdb.get_categories(keynote_data_conn) if x.key.upper() in ["EXTERIOR", "INTERIOR"]]

    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    for cate in categorys:
        data_collection = []
        pointer_row = 0
        data_collection.append(EXCEL.ExcelDataItem("Keynote ID", pointer_row, "B", cell_color=(200, 200, 200), col_width=10, merge_with=[(pointer_row+1, "B")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("Keynote Description", pointer_row, "C", cell_color=(200, 200, 200), col_width=50, merge_with=[(pointer_row+1, "C")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))

        data_collection.append(EXCEL.ExcelDataItem("SOURCE", pointer_row+1, "D", cell_color=(200, 200, 200), text_alignment=EXCEL.TextAlignment.Center, col_width=10,
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("PRODUCT", pointer_row+1, "E", cell_color=(200, 200, 200), col_width=10,
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("BASE OF DESIGN", pointer_row, "D", cell_color=(200, 200, 200), merge_with=[(pointer_row, "E")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))

        
        data_collection.append(EXCEL.ExcelDataItem("CAT.NO", pointer_row, "F", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "F")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("COLOR", pointer_row, "G", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "G")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("FINISH", pointer_row, "H", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "H")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("SIZE", pointer_row, "I", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "I")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("CONTACT", pointer_row, "J", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "J")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("SPEC SECTION", pointer_row, "K", cell_color=(200, 200, 200), col_width=15, merge_with=[(pointer_row+1, "K")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))
        data_collection.append(EXCEL.ExcelDataItem("REMARKS", pointer_row, "L", cell_color=(200, 200, 200), col_width=50, merge_with=[(pointer_row+1, "L")],
                                                   top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True))

        
        pointer_row += 2
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

                extend_db_item = db_data.get(leaf.key)
                if extend_db_item:
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.SOURCE, pointer_row, "D",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.PRODUCT, pointer_row, "E",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("CAT.NO"), pointer_row, "F",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("COLOR"), pointer_row, "G",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("FINISH"), pointer_row, "H",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("SIZE"), pointer_row, "I",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("CONTACT"), pointer_row, "J",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("SPEC SECTION"), pointer_row, "K",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(extend_db_item.get("REMARKS"), pointer_row, "L",
                                                            top_border_style=1, side_border_style=1, bottom_border_style=1))
                else:
                    # if cannot find a matching DB item by keynote key, it problly means DB item is lost or user have give a new keynote key.
                    # override the color to light red to make it notice
                    data_collection.append(EXCEL.ExcelDataItem(leaf.key, pointer_row, "B", cell_color=(255, 200, 200),
                                                           top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem(leaf.text, pointer_row, "C", cell_color=(255, 200, 200),
                                                           top_border_style=1, side_border_style=1, bottom_border_style=1))
                    data_collection.append(EXCEL.ExcelDataItem("Cannot find this item in extended DB", pointer_row, "D", cell_color=(211, 211, 211), merge_with=[(pointer_row, "E"), (pointer_row, "F"), (pointer_row, "G"), (pointer_row, "H"), (pointer_row, "I"), (pointer_row, "J"), (pointer_row, "K"), (pointer_row, "L")],
                                                           top_border_style=1, side_border_style=1, bottom_border_style=1))
                    
                print("\t\t\t{}-{}: [{}] {}".format(i+1, j+1, leaf.key, leaf.text))
                

        def _pick_excel_out_path():
            excel_out_path = forms.pick_excel_file(title="Pick Extended Keynote Database Excel File for [{}]".format(cate.key),
                                                    save = True,
                                                    )
            if "keynote_assistant" not in project_data:
                project_data["keynote_assistant"] = {}
            if "setting" not in project_data["keynote_assistant"]:
                project_data["keynote_assistant"]["setting"] = {}
        
            project_data["keynote_assistant"]["setting"]["excel_path_{}".format(cate.key)] = excel_out_path
            REVIT_PROJ_DATA.set_revit_project_data(doc, project_data)
            return excel_out_path

        
        excel_out_path = project_data.get("keynote_assistant", {}).get("setting", {}).get("excel_path_{}".format(cate.key))
        if not excel_out_path:
            note =  "Excel output path for [{}] is not defined, please pick one".format(cate.key)
            NOTIFICATION.messenger(note)
            print (note)
            excel_out_path = _pick_excel_out_path()
        elif not os.path.exists(excel_out_path):
            print ("Excel output path for [{}] is not found, please pick one again.\nOriginal path: {}  is no longer valid".format(cate.key, excel_out_path))
            excel_out_path = _pick_excel_out_path()




        EXCEL.save_data_to_excel(data_collection, excel_out_path, worksheet=cate.key, freeze_row=2)

    if db_data:
        output = script.get_output()
        output.print_md("## =====Please check the following=====")
        # Get keynotes once to avoid multiple database calls
        leaf_keynotes = get_leaf_keynotes(keynote_data_conn)
        diff = set(db_data.keys()) - set([x.key for x in leaf_keynotes])
        if diff:
            output.print_md("Warning: some keys in extended DB are not in keynote file:")
            for i, x in enumerate(diff):
                output.print_md("-{}: [{}]{}".format(i+1, x, db_data[x].KEYNOTE_DESCRIPTION))

        keynote_keys = {keynote.key: keynote for keynote in leaf_keynotes}
        
        reverse_diff = set(keynote_keys.keys()) - set(db_data.keys())
        if reverse_diff:
            output.print_md("Warning: some keys in keynote file are not in extended DB:")
            for i, key in enumerate(reverse_diff):
                output.print_md("-{}: [{}]{}".format(i+1, key, keynote_keys[key].text))

        if diff or reverse_diff:
            print ("\n\n")
            output.print_md("This is usually due to one of the following reasons:")
            output.print_md("1. You have renamed the key in keynote file but did not update the same item in the DB excel file: Please update the same item in the DB excel file")
            output.print_md("2. You have added a new keynote in keynote file, but not in extended DB: Please add the same item in the DB excel file")
            output.print_md("3. You have added a new keynote in extended DB, but not in keynote file: Please add the same item in the keynote file")

def edit_extended_db_excel(keynote_data_conn):
    doc = REVIT_APPLICATION.get_doc()
    t = DB.Transaction(doc, "edit extended db excel")
    t.Start()
    REVIT_PROJ_DATA.setup_project_data(doc)
    t.Commit()
    project_data = REVIT_PROJ_DATA.get_revit_project_data(doc)
    keynote_excel_extend_db = project_data.get("keynote_assistant", {}).get("setting", {}).get("extended_db_excel_path")
    if not keynote_excel_extend_db:
        
        keynote_excel_extend_db = forms.pick_excel_file(title="Pick Extended Keynote Database Excel File",
                                                  save = True,
                                                  )
        if "keynote_assistant" not in project_data:
            project_data["keynote_assistant"] = {}
        if "setting" not in project_data["keynote_assistant"]:
            project_data["keynote_assistant"]["setting"] = {}
      
        project_data["keynote_assistant"]["setting"]["extended_db_excel_path"] = keynote_excel_extend_db
        REVIT_PROJ_DATA.set_revit_project_data(doc, project_data)

    if os.path.exists(keynote_excel_extend_db):
        os.startfile(keynote_excel_extend_db)
        return

    # export a default one to this address, i am just here to setup EMPTY excel
    color_yellow = (252, 213, 180)
    color_green = (196, 215, 155)
    color_light_grey = (224, 224, 224)
    color_dark_grey = (200, 200, 200)
    data_collection = []
    pointer_row = 0
    data_collection.append(EXCEL.ExcelDataItem("KEYNOTE ID", pointer_row, "B", cell_color=color_dark_grey, col_width=15,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("KEYNOTE DESCRIPTION", pointer_row, "C", cell_color=color_dark_grey, 
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("SOURCE", pointer_row, "D", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("PRODUCT", pointer_row, "E", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("CAT.NO", pointer_row, "F", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("COLOR", pointer_row, "G", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("FINISH", pointer_row, "H", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("SIZE", pointer_row, "I", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("CONTACT", pointer_row, "J", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    data_collection.append(EXCEL.ExcelDataItem("SPEC SECTION", pointer_row, "K", cell_color=color_dark_grey, col_width=10,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))   
    data_collection.append(EXCEL.ExcelDataItem("REMARKS", pointer_row, "L", cell_color=color_dark_grey, col_width=30,
                                                top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
    
    # Get the full keynote tree
    categorys = [x for x in kdb.get_categories(keynote_data_conn)]
    all_keynotes = kdb.get_keynotes(keynote_data_conn)
    for cate in categorys:
        pointer_row += 3
        print("\n== CATEGORY: {} ==".format(cate.key))
        data_collection.append(EXCEL.ExcelDataItem("[Category]: " + str(cate.key), pointer_row, "B", cell_color = color_yellow, is_bold=True, is_read_only=True))
        for column in range(10):  # From C to L, char 67 is C
            data_collection.append(EXCEL.ExcelDataItem("", pointer_row, chr(67 + column), cell_color=color_yellow, is_bold=True, is_read_only=True))

        top_branch = [x for x in all_keynotes if x.parent_key == cate.key]
        print ("\tTop branchs in {}".format(cate.key))
        for i, branch in enumerate(top_branch):
            pointer_row += 1
            bran_name = branch.text
            if len(bran_name) == 0:
                bran_name = "UnOrganized"
            data_collection.append(EXCEL.ExcelDataItem("[Branch]: " + str(bran_name), pointer_row, "B", cell_color=color_green, is_bold=True, is_read_only=True))
            for column in range(10):  # From C to L, char 67 is C
                data_collection.append(EXCEL.ExcelDataItem("", pointer_row, chr(67 + column), cell_color=color_green, is_bold=True, is_read_only=True))
            print("\t\t{}: [{}] {}".format(i+1,branch.key, branch.text))
            leafs = [x for x in all_keynotes if x.parent_key == branch.key]
            for j, leaf in enumerate(leafs):
                pointer_row += 1

                print("\t\t\t{}-{}: [{}] {}".format(i+1, j+1, leaf.key, leaf.text))

                data_collection.append(EXCEL.ExcelDataItem(str(leaf.key), pointer_row, "B", cell_color=color_light_grey, 
                                                        top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
                data_collection.append(EXCEL.ExcelDataItem(str(leaf.text), pointer_row, "C", cell_color=color_light_grey, 
                                                        top_border_style=1, side_border_style=1, bottom_border_style=1, is_bold=True, is_read_only=True))
            
            
    

    EXCEL.save_data_to_excel(data_collection, keynote_excel_extend_db, worksheet="Keynote Extended DB", freeze_row=1, freeze_column="C")

    os.startfile(keynote_excel_extend_db)



if __name__ == "__main__":
    pass
