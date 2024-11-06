#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities for working with Excel files.
Check formulas, read data, save data, etc."""

import os
import shutil
import sys
import trace
import traceback
import time
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
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
import xlrd
import xlsxwriter

from collections import defaultdict

def column_number_to_letter(number, is_upper=True):
    return chr(number + 64 + (0 if is_upper else 32))

def letter_to_index(letter):
    """Get the index of a letter in the alphabet.
    A -> 0, B -> 1, C -> 2, etc.

    Args:
        letter (str): A single letter.

    Returns:
        int: The index of the letter in the alphabet.
    """
    if isinstance(letter, int):
        return letter
    try:
        return ord(letter.upper()) - ord("A")
    except TypeError:
        return None


def get_column_index(letter):
    """Get the index of an Excel column.

    Args:
        letter (str): The column letter.

    Returns:
        int: The column index.
    """
    if isinstance(letter, int):
        return letter
    
    if len(letter) == 1:
        return letter_to_index(letter)
    elif len(letter) == 2:
        char1 = letter[0]
        char2 = letter[1]
        return 26 * (letter_to_index(char1) + 1) + letter_to_index(char2)
    else:
        return None


class ExcelDataItem:
    def __init__(
        self,
        item,
        row,
        column,
        cell_color=None,
        text_color=None,
        border_style=None,
        border_color=None,
    ):
        if isinstance(column, str):
            column = letter_to_index(column)
        self.item = item
        self.row = row
        self.column = column
        self.cell_color = cell_color
        self.text_color = text_color
        self.border_style = border_style
        self.border_color = border_color

    def __str__(self):
        info = "ExcelDataItem: {} @ ({}, {})".format(self.item, self.row, self.column)
        if self.cell_color:
            info += " ({})".format(self.cell_color)
        return info


def get_all_worksheets(filepath):
    """List all the worksheets in an Excel file.

    Args:
        filepath (str): The path to the Excel file.

    Returns:
        list: A list of worksheet names.
    """

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def save_as_xls(filepath):
    """Save an Excel file as .xls format.

    Args:
        filepath (str): The path to the Excel file to convert.

    Returns:
        str: The path to the saved .xls file, or None if conversion failed.
    """
    _, file = os.path.split(filepath)
    safe_copy = FOLDER.get_EA_dump_folder_file("save_copy_" + file)
    shutil.copyfile(filepath, safe_copy)

    

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
    """Read data from an Excel file or URL.

    Args:
        filepath (str): The path to the Excel file or URL.
        worksheet (str, optional): The name of the worksheet. Defaults to None.
        return_dict (bool, optional): Whether to return the data as a dictionary, otherwise by line. Defaults to False.

    Returns:
        list or dict: The data from the Excel
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
    with open(temp_filepath, 'wb') as f:
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
    filepath = FOLDER.get_save_copy(filepath)
    
    if filepath.endswith(".xlsx"):
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


def get_column_values(data, column):
    """Get all unique values in a column and their corresponding row numbers.
    
    Args:
        data (dict): Excel data dictionary with (row,col) tuple keys and value/color dicts
        column (str/int): Column letter (e.g. 'A') or index number (0-based)
        
    Returns:
        dict: Dictionary mapping unique values to lists of row numbers where they appear
    """
    column = get_column_index(column)
    result = defaultdict(list)
    for key, value_dict in data.items():
        if key[1] == column:
            result[value_dict["value"]].append(key[0])
    return dict(result)

def search_row_in_column_by_value(data, column, search_value, is_fuzzy=False):
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
    column = get_column_index(column)
    if is_fuzzy:
        column_values = get_column_values(data, column).keys()
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

def save_data_to_excel(data, filepath, worksheet="EnneadTab", open_after=True):
    """Save data to an Excel file.

    Args:
        data (list): list of Excel Data item that has row, column, item attr.
        the order is handled before the data entry
        filepath (str): The path to the Excel file.
        worksheet (str, optional): The name of the worksheet. Defaults to "EnneadTab".
        open_after (bool, optional): Whether to open the Excel file after saving. Defaults to True.
    """

    # note to self: rework the format method in dataitem so can construct any combonation format
    # see doc here: https://xlsxwriter.readthedocs.io/format.html#format-set-border
    def write_data_item(worksheet, data):
        if any(
            [data.cell_color, data.text_color, data.border_style, data.border_color]
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
            column_max_width_dict[column], 1.2 * len(str(item))
        )

    for column in column_max_width_dict.keys():
        worksheet.set_column(column, column, column_max_width_dict[column])

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
    """Check the formulas in an Excel file.

    Args:
        excel (str): The name of the Excel file.
        worksheet (str): The name of the worksheet.
        highlight_formula (bool, optional): Whether to highlight the formulas in the Excel file. Defaults to True.
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
