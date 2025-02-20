#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Excel file manipulation utilities for EnneadTab.

This module provides comprehensive tools for Excel file operations including:
- Reading and writing data from/to Excel files
- Formula validation and visualization
- Column/row manipulation and searching
- Color and formatting management
- Support for both local and online Excel files

The module handles both .xls and .xlsx formats, with special handling for
SharePoint-hosted files.
"""

import os

import sys
import traceback
import time
import io
try:
    
    sys.setdefaultencoding("utf-8")
except:
    pass


import ENVIRONMENT
import EXE
import NOTIFICATION
import COLOR
import FOLDER
import UNIT_TEST
import TEXT
import DATA_FILE
import COPY
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
import xlrd
import xlsxwriter

from collections import defaultdict

def column_number_to_letter(number, is_upper=True):
    """Convert numeric column index to Excel letter notation.

    Args:
        number (int): Column number (1-based index)
        is_upper (bool): If True, returns uppercase letter

    Returns:
        str: Column letter (e.g., 1 -> 'A', 2 -> 'B')
    """
    return chr(number + 64 + (0 if is_upper else 32))

def letter_to_index(letter, start_from_zero=False):
    """Convert Excel column letter to numeric index.

    Args:
        letter (str): Column letter ('A' to 'Z')
        start_from_zero (bool): If True, 'A' maps to 0; if False, 'A' maps to 1

    Returns:
        int: Column index, or None if invalid input
    """
    if isinstance(letter, int):
        return letter
    try:
        return ord(letter.upper()) - ord("A") + (0 if start_from_zero else 1)
    except TypeError:
        return None


def get_column_index(letter, start_from_zero=False):
    """Convert Excel column reference to numeric index.

    Handles both single ('A') and double ('AA') letter columns.

    Args:
        letter (str|int): Column reference or direct index
        start_from_zero (bool): If True, 'A' maps to 0; if False, 'A' maps to 1

    Returns:
        int: Column index, or None if invalid input
    """
    if isinstance(letter, int):
        return letter
    
    if len(letter) == 1:
        return letter_to_index(letter, start_from_zero)
    elif len(letter) == 2:
        char1 = letter[0]
        char2 = letter[1]
        return 26 * (letter_to_index(char1, start_from_zero) + 1) + letter_to_index(char2, start_from_zero)
    else:
        return None


class ExcelDataItem:
    """Container for Excel cell data and formatting.
    
    Reference for border styles: https://xlsxwriter.readthedocs.io/format.html#set_border

    Attributes:
        item: Cell content
        row (int): Row index
        column (int|str): Column index or letter
        cell_color (tuple): RGB color for cell background
        text_color (tuple): RGB color for text
        border_style (str): Border style specification
        border_color (tuple): RGB color for border
        top_border_style (str): Top border style
        side_border_style (str): Left/right border style
    """
    def __init__(
        self,
        item,
        row,
        column,
        cell_color=None,
        text_color=None,
        border_style=None,
        border_color=None,
        top_border_style=None,
        side_border_style=None,
    ):
        if isinstance(column, str):
            column = letter_to_index(column, start_from_zero=True)
        self.item = item
        self.row = row
        self.column = column
        self.cell_color = cell_color
        self.text_color = text_color
        self.border_style = border_style
        self.border_color = border_color
        self.top_border_style = top_border_style
        self.side_border_style = side_border_style
    def __str__(self):
        info = "ExcelDataItem: {} @ ({}, {})".format(self.item, self.row, self.column)
        if self.cell_color:
            info += " ({})".format(self.cell_color)
        return info


def get_all_worksheets(filepath):
    """List all worksheets in an Excel file.

    Args:
        filepath (str): Path to Excel file

    Returns:
        list: Names of all worksheets in the file
    """

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def save_as_xls(filepath):
    """Convert Excel file to .xls format.

    Creates a safe copy before conversion and handles cleanup.

    Args:
        filepath (str): Source Excel file path

    Returns:
        str: Path to converted .xls file, or None if conversion fails
    """
    _, file = os.path.split(filepath)
    safe_copy = FOLDER.get_EA_dump_folder_file("save_copy_" + file)
    COPY.copyfile(filepath, safe_copy)

    

    try:
        import clr  # pyright: ignore
        clr.AddReference("Microsoft.Office.Interop.Excel")
        from Microsoft.Office.Interop import Excel  # pyright: ignore

        excel_app = Excel.ApplicationClass()
        excel_app.Visible = False
        excel_app.DisplayAlerts = False  # Suppress warnings and prompts

        
        # Force open the workbook as ReadOnly and ignore warnings
        workbook = excel_app.Workbooks.Open(
            safe_copy,
            ReadOnly=True,  # Open in read-only mode to avoid write permission issues
            IgnoreReadOnlyRecommended=True,  # Suppress the read-only prompt
            CorruptLoad=Excel.XlCorruptLoad.xlRepairFile  # Try opening with repair options
        )
        save_as_path = FOLDER.get_EA_dump_folder_file("local_save_as_{}.xls".format(time.time()))
        workbook.SaveAs(save_as_path, FileFormat=Excel.XlFileFormat.xlExcel8)
        return save_as_path
    except:
        print ("Cannot save as xls, see error below:")
        print (traceback.format_exc())
    finally:
        try:    
            workbook.Close(False)
            excel_app.Quit()
        except:
            pass


def read_data_from_excel(filepath, worksheet=None, return_dict=False, headless=True):
    """Read data from local or online Excel file.

    Supports both local files and HTTP URLs. For .xlsx files, uses ExcelHandler
    for improved performance.

    Args:
        filepath (str): Local path or URL to Excel file
        worksheet (str): Target worksheet name
        return_dict (bool): If True, returns dict with (row,col) keys
        headless (bool): If True, runs Excel operations without UI

    Returns:
        list|dict: Excel data in requested format
    """
    # Check if the filepath is a URL
    if filepath.startswith("http://"):
        return _read_data_from_excel_online(filepath, worksheet, return_dict, headless)
    else:
        return _read_data_from_excel_locally(filepath, worksheet, return_dict, headless)

def _read_data_from_excel_online(url, worksheet, return_dict, headless):
    import clr  # pyright: ignore
    clr.AddReference("System")
    from System.Net import WebClient  # pyright: ignore
    from System.IO import MemoryStream  # pyright: ignore

    web_client = WebClient()
    data = web_client.DownloadData(url)
    stream = MemoryStream(data)

    # Create a temporary file to save the downloaded data
    temp_filepath = FOLDER.get_EA_dump_folder_file("_temp_excel_{}.xls".format(time.time()))
    with io.open(temp_filepath, 'wb', encoding="utf-8") as f:
        f.write(data)

    # Clean up temp file
    print ("temp file is at: {}".format(temp_filepath))
    os.startfile(temp_filepath)
    # Read the data using the local file reader
    result = _read_data_from_excel_locally(temp_filepath, worksheet, return_dict, headless)

    # try:
    #     os.remove(temp_filepath)
    # except:
    #     pass

    return result


def _read_data_from_excel_locally(filepath, worksheet, return_dict, headless):
    filepath = FOLDER.get_safe_copy(filepath)
    
    if filepath.endswith(".xlsx"):
        if not worksheet:
            NOTIFICATION.messenger(main_text="Worksheet input is required for xlsx files")
            return {}   
        job_data = {
            "mode": "read",
            "filepath": filepath,
            "worksheet": worksheet
        }
        DATA_FILE.set_data(job_data, "excel_handler_input.sexyDuck")
        EXE.try_open_app("ExcelHandler")
        max_wait = 100
        wait = 0
        while wait<max_wait:
            job_data = DATA_FILE.get_data("excel_handler_input.sexyDuck")
            if job_data.get("status") == "done":
                break
            time.sleep(0.1)
            wait += 1
        raw_data = DATA_FILE.get_data("excel_handler_output.sexyDuck")
        
        # Convert string keys back to tuple keys
        converted_data = {}
        for key, value in raw_data.items():
            row, column = map(int, key.split(','))
            converted_data[(row, column)] = value

        if not return_dict:
            # convert the converted_data to a list of lists, sorted by row, adding missing rows with empty strings. the coumn count need to match the max column count in the data
            max_column = max(column for row, column in converted_data.keys())
            max_row = max(row for row, column in converted_data.keys())
            OUT = []
            for row in range(max_row):
                row += 1 # because the row index is 1-based, so need to shift it
                row_data = []
                for column in range( max_column):
                    column += 1 # because the column index is 1-based, so need to shift it
                    if (row, column) in converted_data:
                        row_data.append(converted_data[(row, column)])
                    else:
                        row_data.append({})
                OUT.append(row_data)
            return OUT
        
        return converted_data
        NOTIFICATION.messenger(main_text="Excel file is xlsx, converting to xls, this will take a few moments.\nFor better performance, save as .xls instead of .xlsx.")   
        filepath = save_as_xls(filepath)

    if not return_dict:
        wb = xlrd.open_workbook(
            filepath, formatting_info=return_dict
        )
        try:
            if not worksheet:
                worksheet = wb.sheet_names()[0]
            sheet = wb.sheet_by_name(worksheet)
        except:
            NOTIFICATION.messenger(main_text="Cannot open worksheet: {}".format(worksheet))
            return None
        
        OUT = []

        for i in range(0, sheet.nrows):
            OUT.append(sheet.row_values(i))
        return OUT

    import clr  # pyright: ignore

    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel  # pyright: ignore

    excel_app = Excel.ApplicationClass()
    excel_app.Visible = not headless
    excel_app.DisplayAlerts = False  # Suppress warnings and prompts

    OUT = {}
    try:
        # Force open the workbook as ReadOnly and ignore warnings
        workbook = excel_app.Workbooks.Open(
            filepath,
            ReadOnly=True,  # Open in read-only mode to avoid write permission issues
            IgnoreReadOnlyRecommended=True,  # Suppress the read-only prompt
            CorruptLoad=Excel.XlCorruptLoad.xlRepairFile  # Try opening with repair options
        )
        sheet = workbook.Sheets[worksheet]

        import COLOR

        for i in range(1, sheet.UsedRange.Rows.Count + 1):
            for j in range(1, sheet.UsedRange.Columns.Count + 1):
                cell = sheet.Cells[i, j]
                decimal_color = cell.Interior.Color
                rgb_color = COLOR.decimal_to_rgb(decimal_color)
                cell_value = cell.Value2 if cell.Value2 is not None else ""

                # note to self, use i-1 and j-1 because the index starting method is different for clr called method
                OUT[(i - 1, j - 1)] = {"value": cell_value, "color": rgb_color}

    except:
        print (traceback.format_exc())
    finally:
        try:
            workbook.Close(False)
            excel_app.Quit()
        except:
            pass
        
    return OUT


def get_column_values(data, column, start_from_zero=False):
    """Extract unique values and their row positions from a column.

    Args:
        data (dict): Excel data dictionary
        column (str|int): Column identifier
        start_from_zero (bool): If True, uses 0-based indexing

    Returns:
        dict: Mapping of unique values to their row numbers
    """
    column = get_column_index(column, start_from_zero)
    result = defaultdict(list)
    for key, value_dict in data.items():
        if key[1] == column:
            result[value_dict["value"]].append(key[0])
    return dict(result)

def search_row_in_column_by_value(data, column, search_value, is_fuzzy=False, start_from_zero=False):
    """Search for a value in a specific column and return the matching row number.
    
    Args:
        data (dict): Excel data dictionary with (row,col) tuple keys and value/color dicts.
            Example format:
            {
                (93, 9): {'color': (255, 255, 255), 'value': 'apple'},
                (68, 2): {'color': (255, 255, 255), 'value': 'E10 - Lobby Cafe'}
            }
        column (str/int): Column letter (e.g. 'A') or index number (0-based)
        search_value (str): Value to search for in the column
        is_fuzzy (bool, optional): Whether to use fuzzy matching. Defaults to False.
        
    Returns:
        int: Row number where value was found, or None if not found
    """
    column = get_column_index(column, start_from_zero)
    if is_fuzzy:
        column_values = get_column_values(data, column, start_from_zero).keys()
        new_search_value = TEXT.fuzzy_search(search_value, column_values) # change the search value to the best match
        print ("search value changed from [{}] --> [{}]".format(search_value, new_search_value))
        search_value = new_search_value
        

    for key in data.keys():
        data_row, data_column = key
        if data_column != column:
            continue
        else:
            if data[key]["value"] == search_value:
                return data_row
    return None

def save_data_to_excel(data, filepath, worksheet="EnneadTab", open_after=True, freeze_row = None):
    """Write data to Excel file with formatting.

    Args:
        data (list): List of ExcelDataItem objects
        filepath (str): Target Excel file path
        worksheet (str): Worksheet name
        open_after (bool): If True, opens file after saving
        freeze_row (int): Row number for freeze panes
    """

    # note to self: rework the format method in dataitem so can construct any combonation format
    # see doc here: https://xlsxwriter.readthedocs.io/format.html#format-set-border
    def write_data_item(worksheet, data):
        if any(
            [data.cell_color, data.text_color, data.border_style, data.border_color, data.top_border_style]
        ):
            format_dict = {}
            if data.cell_color:
                format_dict["bg_color"] = COLOR.rgb_to_hex(data.cell_color)
            if data.text_color:
                format_dict["color"] = COLOR.rgb_to_hex(data.text_color)
            if data.border_style:
                format_dict["border"] = data.border_style
            if data.border_color:
                format_dict["border_color"] = COLOR.rgb_to_hex(data.border_color)
            if data.top_border_style:
                format_dict["top"] = data.top_border_style
            if data.side_border_style:
                format_dict["left"] = data.side_border_style
                format_dict["right"] = data.side_border_style
            format = workbook.add_format(format_dict)
            worksheet.write(data.row, data.column, data.item, format)
        else:
            worksheet.write(data.row, data.column, data.item)

        # if data.cell_color:
        #     hex_color = COLOR.rgb_to_hex(data.cell_color)
        #     format = workbook.add_format({'bg_color' : hex_color})
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item,
        #                     format)
        # elif data.text_color:
        #     hex_color = COLOR.rgb_to_hex(data.text_color)
        #     format = workbook.add_format({'color' : hex_color})
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item,
        #                     format)

        # else:
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item)

    workbook = xlsxwriter.Workbook(filepath)

    worksheet = workbook.add_worksheet(worksheet)
    for data_entry in data:
        write_data_item(worksheet, data_entry)

    column_max_width_dict = dict()
    for entry in data:
        column, item = entry.column, entry.item
        if column not in column_max_width_dict.keys():
            column_max_width_dict[column] = 0
        column_max_width_dict[column] = max(
            column_max_width_dict[column], 1.1 * len(str(item))
        )

    for column in column_max_width_dict.keys():
        worksheet.set_column(column, column, column_max_width_dict[column])

    if freeze_row:
        worksheet.freeze_panes(freeze_row, 0)

    try:
        workbook.close()
        if not open_after:
            NOTIFICATION.messenger(main_text="Excel saved at '{}'".format(filepath))
    except:
        NOTIFICATION.messenger(
            main_text="the excel file you picked is still open, cannot override. Writing cancelled."
        )
        return

    if open_after:
        os.startfile(filepath)


def check_formula(excel, worksheet, highlight_formula=True):
    """Analyze and optionally highlight Excel formulas.

    Args:
        excel (str): Excel file name
        worksheet (str): Worksheet name
        highlight_formula (bool): If True, visually marks cells containing formulas
    """
    # find all the cells with formula and print the formula like this:
    # B2 = A2 *1.4 + D4:D12
    # Open the workbook and select the first sheet
    import clr  # pyright: ignore

    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel  # pyright: ignore

    excel_app = Excel.ApplicationClass()
    excel_app.Visible = False

    excel = FOLDER.copy_file_to_local_dump_folder(excel, "LocalCopy_" + excel)
    workbook = excel_app.Workbooks.Open(excel)
    sheet = workbook.Sheets[worksheet]

    for col in range(1, sheet.UsedRange.Columns.Count + 1):
        for row in range(1, sheet.UsedRange.Rows.Count + 1):
            cell = sheet.Cells(row, col)
            # Check if there's a formula in the cell
            if cell.HasFormula:
                # Print the location and the formula
                cell_value = cell.Value2 if cell.Value2 is not None else ""
                print(
                    "cell[{}{}] = {} = {}".format(
                        chr(64 + col), row, cell.Formula.replace("=", ""), cell_value
                    )
                )
                if highlight_formula:
                    borders = cell.Borders
                    borders.Weight = 3  # xlThick
                    borders.LineStyle = -4115  # xlDash
                    # borders.LineStyle = 1  # xlContinuous
                    borders.Color = 0xFF0000  # Red color

    if highlight_formula:
        workbook.Save()
    else:
        workbook.Close(False)
    excel_app.Quit()

    if highlight_formula:
        EXE.try_open_app(excel)



def flip_dict(dict):
    output = {}
    for key in dict.keys():
        output[dict[key]] = key
    return output

def num_and_letter(num, letter):
    return num + letter_to_index(letter)




#################  UNIT TEST  #################

test_dict = {
    "get_column_index": {
        "'A'": 0,
        "'B'": 1,
        "'Z'": 25,
        "'AA'": 26,
        "'AB'": 27,
        "'AZ'": 51,
        "'BA'": 52,
        "'BBB'": None,
    },
    "letter_to_index": {
        "'A'": 0,
        "'B'": 1,
        "'Z'": 25,
        "'AA'": None,
        "'BBB'": None,
    },
    "flip_dict": {
        "{'a': 1, 'b': 2}": {1: 'a', 2: 'b'},
        "{'x': 3, 'y': 4}": {3: 'x', 4: 'y'},
    },
    "num_and_letter": {
        "1, 'A'": 1,
        "2, 'B'": 3,
        "3, 'C'": 5,
    },
}


# Old unit test function
# def unit_test():
#     return
#     import xlrd
#     import WEB

#     # Replace this with your SharePoint URL
#     sharepoint_url = "https://enneadarch-my.sharepoint.com/:x:/g/personal/scott_mackenzie_ennead_com/Eey-gTYaVIdGuU9Jg65gig8BIUBmc32Aie-0nNsjVSgUfQ?rtime=4PY2woUX3Eg"

#     # Open the Excel file from the URL
#     str = WEB.get_request(sharepoint_url)
#     print(str)
#     workbook = xlrd.open_workbook(file_contents=str)

#     # Select the first sheet (you can change the sheet index as needed)
#     sheet = workbook.sheet_by_index(0)

#     # Iterate through rows and print each row
#     for row_num in range(sheet.nrows):
#         row = sheet.row_values(row_num)
#         print(row)


#################  MAIN  #################

if __name__ == "__main__":
    filename = __file__
    UNIT_TEST.pretty_test(test_dict, filename)
