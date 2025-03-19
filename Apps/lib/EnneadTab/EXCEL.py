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

Key Features:
- Excel file format conversion and validation
- Cell formatting and styling
- Data extraction and manipulation
- Formula checking and highlighting
- Support for both local and remote Excel files
"""

import os


import re
import time
import io
# if hasattr(sys, "setdefaultencoding"):
#     sys.setdefaultencoding("utf-8")



import EXE
import NOTIFICATION
import COLOR
import FOLDER
import UNIT_TEST
import TEXT
import DATA_FILE
import ERROR_HANDLE
import COPY
import USER
try:
    import xlrd # pyright: ignore
    import xlsxwriter # pyright: ignore
except:
    # r: xlrd
    # r: xlsxwriter
    pass

from collections import defaultdict

def column_number_to_letter(number, is_upper=True):
    """Convert numeric column index to Excel letter notation.

    Handles both single-letter (A-Z) and multi-letter (AA-ZZ) column references.
    Uses 1-based indexing to match Excel's column numbering system.

    Args:
        number (int): Column number (1-based index)
        is_upper (bool, optional): If True, returns uppercase letters. Defaults to True.

    Returns:
        str: Column letter notation (e.g., 1 -> 'A', 27 -> 'AA')
    """
    result = ""
    while number > 0:
        number -= 1
        remainder = number % 26
        result = chr(remainder + 65) + result
        number //= 26
    
    if not is_upper:
        result = result.lower()
    return result

def letter_to_index(letter, start_from_zero=False):
    """Convert Excel column letter to numeric index.

    Args:
        letter (str): Column letter ('A' to 'Z')
        start_from_zero (bool, optional): If True, 'A' maps to 0; if False, 'A' maps to 1.
            Defaults to False.

    Returns:
        int or None: Column index if valid input, None otherwise
    """
    if isinstance(letter, int):
        return letter
    try:
        return ord(letter.upper()) - ord("A") + (0 if start_from_zero else 1)
    except TypeError:
        return None


def letter_next(letter, offset = 1):
    """Get the next column letter in the sequence.

    Args:
        letter (str): Current column letter
        offset (int, optional): Number of positions to move forward. Defaults to 1.
    """
    return column_number_to_letter(letter_to_index(letter) + offset)


def get_column_index(letter, start_from_zero=False):
    """Convert Excel column reference to numeric index.

    Handles both single ('A') and double ('AA') letter column references.
    Accepts both string and integer inputs.

    Args:
        letter (str|int): Column reference or direct index
        start_from_zero (bool, optional): If True, 'A' maps to 0; if False, 'A' maps to 1.
            Defaults to False.

    Returns:
        int or None: Column index if valid input, None otherwise
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

class TextAlignment:
    Left = "left"
    Right = "right"
    Center = "center"
    Justify = "justify"

class BorderStyle:
    Thin = "thin"
    Medium = "medium"
    Thick = "thick"

class ExcelDataCollection:
    """
    there are stored in a list and a dict at same time
    use list for final save excel, so later definitation can override previous one
    use dict for pointer, so can track the position of the pointer if using a ovverride condition.
    """
    def __init__(self):
        self.data = []
        self.row = 0
        self.column = 0
        self.used_coord = {}
        self.has_warning = False

    def set_pointer_lower_right(self):
        largest_row = max(item.row for item in self.data)
        largest_col = max(item.column for item in self.data)
        self.row = largest_row
        self.column = largest_col

    def add(self, item):
        """Add an item to the collection.
        NOTE that it will not move pointer after added.
        
        Args:
            item (ExcelDataItem | str ): The item to add.

        """
        
        if isinstance(item, ExcelDataItem):
            if (item.row, item.column) in self.used_coord:
                print ("!!! Item already exists at ({}, {}): {}".format(item.row, item.column, self.used_coord[(item.row, item.column)].item))
                self.has_warning = True
            self.data.append(item)
            self.used_coord[(item.row, item.column)] = item
        else:
            if (self.row, self.column) in self.used_coord:
                print ("!!! Item already exists at ({}, {}): {}".format(self.row, self.column, self.used_coord[(self.row, self.column)].item))
                self.has_warning = True
            item = ExcelDataItem(item, self.row, self.column)
            self.data.append(item)
            self.used_coord[(self.row, self.column)] = item

        print (self.pointer)

    def add_row(self, row):
        self.row += 1
        self.column = 0
        for item in row:
            self.add(ExcelDataItem(item, self.row, self.column))
            self.next_col()

    @property
    def pointer(self):
        return "Pointer is at cell({}{})".format(column_number_to_letter(self.column+1),self.row+1)  

    def next_row(self):
        self.row += 1

    def next_col(self):
        self.column += 1

    def prev_col(self):
        self.column -= 1

    def prev_row(self):
        self.row -= 1

    def set_col_by_header(self, header):
        """Set the current column to the column with the given header text.
        
        Args:
            header (str): Header text to search for
        """
        # Find the header item in the first row
        for item in self.data:
            if item.row == self.header_row and item.item == header:
                self.column = item.column
                return
        print("Warning: Header '{}' not found".format(header))

    def set_headers(self, headers, width_list = None, starting_col = "A", header_row = 0):

        self.starting_col = starting_col
        self.header_row = header_row
        for i, header in enumerate(headers):
            item = ExcelDataItem(header, self.header_row, letter_next(self.starting_col, i),
                                 cell_color=(200, 200, 200),
                                 is_bold=True,
                                 col_width=width_list[i] if width_list and i < len(width_list) else None,
                                 text_alignment=TextAlignment.Center,
                                 top_border_style=BorderStyle.Thick,
                                 bottom_border_style=BorderStyle.Thick,
                                 side_border_style=BorderStyle.Thick)
            self.add(item)

    def save(self, filepath, worksheet="EnneadTab", open_after=True, freeze_column=None):
        if self.has_warning:
            NOTIFICATION.messenger(main_text="There are warnings related to cell override, see console for details")
        save_data_to_excel(self.data, filepath, worksheet=worksheet, open_after=open_after, freeze_row=self.header_row+1, freeze_column=freeze_column)


        
class ExcelDataItem:
    """Container for Excel cell data and formatting.
    
    Stores cell content, position, and formatting properties including colors and borders.
    Reference for border styles: https://xlsxwriter.readthedocs.io/format.html#set_border

    """
    def __init__(
        self,
        item,
        row,
        column,
        is_bold = False,
        is_read_only = False,
        cell_color=None,
        text_color=None,
        text_alignment = TextAlignment.Left,
        font_size=None,
        font_name=None,
        col_width=None,
        border_style=None,
        border_color=None,
        top_border_style=None,
        bottom_border_style=None,
        side_border_style=None,
        merge_with=None,
    ):
        """_summary_

        Args:
            item (_type_): _description_
            row (_type_): _description_
            column (_type_): _description_
            is_bold (bool, optional): If True, the text will be bold. Defaults to False.
            is_read_only (bool, optional): If True, the cell will be read only. Defaults to False.
            cell_color (_type_, optional): _description_. Defaults to None.
            text_color (_type_, optional): _description_. Defaults to None.
            text_alignment (TextAlignment, optional): _description_. Defaults to TextAlignment.Left.
            font_size (_type_, optional): _description_. Defaults to None.
            font_name (_type_, optional): _description_. Defaults to None.
            col_width (_type_, optional): _description_. Defaults to None.
            border_style (_type_, optional): _description_. Defaults to None.
            border_color (_type_, optional): _description_. Defaults to None.
            top_border_style (_type_, optional): _description_. Defaults to None.
            bottom_border_style (_type_, optional): _description_. Defaults to None.
            side_border_style (_type_, optional): _description_. Defaults to None.
            merge_with (_type_, optional): _description_. Defaults to None.
        """
        if isinstance(column, str):
            column = letter_to_index(column, start_from_zero=True)

        # Ensure all text data is properly encoded. This is a protection to Revit 2025 new CORE.
        if isinstance(item, str):
            # Replace or handle any problematic characters
            item = item.replace('\x00', '') # remove any null character
            
        self.item = item
        self.row = row
        self.column = column
        self.is_bold = is_bold
        self.is_read_only = is_read_only
        self.cell_color = cell_color
        self.text_color = text_color
        self.text_alignment = text_alignment
        self.font_size = font_size
        self.font_name = font_name
        self.col_width = col_width
        self.border_style = border_style
        self.border_color = border_color
        self.top_border_style = top_border_style
        self.bottom_border_style = bottom_border_style
        self.side_border_style = side_border_style
        self.merge_with = merge_with
    def __str__(self):
        info = "ExcelDataItem: {} @ ({}, {})".format(self.item, self.row, self.column)
        if self.cell_color:
            info += " ({})".format(self.cell_color)
        return info

    def as_dict(self):
        """Convert ExcelDataItem to dictionary, excluding internal attributes.
        
        Returns:
            dict: Dictionary containing all non-internal attributes
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


    @classmethod
    def from_dict(cls, data):
        """Create an ExcelDataItem instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing ExcelDataItem attributes
            
        Returns:
            ExcelDataItem: New instance with attributes from dictionary
        """
        # Define all possible attributes with their defaults
        attrs = {
            'item': None,
            'row': None,
            'column': None,
            'is_bold': False,
            'is_read_only': False,
            'cell_color': None,
            'text_color': None,
            'text_alignment': TextAlignment.Left,
            'font_size': None,
            'font_name': None,
            'col_width': None,
            'border_style': None,
            'border_color': None,
            'top_border_style': None,
            'bottom_border_style': None,
            'side_border_style': None,
            'merge_with': None
        }
        
        # Update with provided values
        attrs.update({k: data.get(k) for k in attrs if k in data})
        
        return cls(**attrs)


    @staticmethod
    def convert_datas_to_dict(datas):
        return {i: data.as_dict() for i, data in enumerate(datas)}

    @staticmethod
    def convert_dict_to_datas(data_dict):
        return [ExcelDataItem.from_dict(data) for data in data_dict.values()]


def get_all_worksheets(filepath):
    """List all worksheets in an Excel file.

    Args:
        filepath (str): Path to the Excel file

    Returns:
        list: Names of all worksheets in the workbook
    """

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def save_as_xls(filepath):
    """Convert Excel file to .xls format.

    Creates a safe copy before conversion and handles cleanup.
    Uses Microsoft.Office.Interop.Excel for conversion.

    Args:
        filepath (str): Path to source Excel file

    Returns:
        str or None: Path to converted .xls file if successful, None if conversion fails
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
        print (ERROR_HANDLE.get_alternative_traceback())
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
        worksheet (str, optional): Target worksheet name. Defaults to first sheet.
        return_dict (bool, optional): If True, returns dict with (row,col) keys.
            Defaults to False.
        headless (bool, optional): If True, runs Excel operations without UI.
            Defaults to True.

    Returns:
        list or dict: Excel data in requested format
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


    # Read the data using the local file reader
    result = _read_data_from_excel_locally(temp_filepath, worksheet, return_dict, headless)

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

    ##################################################
    # due to the rhino 8 and revit 2025 core change, there will be no more running for xls files
    if USER.IS_DEVELOPER:
        print ("##################Excel: due to the rhino 8 and revit 2025 core change, there will be no more running for xls files")
        NOTIFICATION.messenger(main_text="due to the rhino 8 and revit 2025 core change, there will be no more running for xls files")
    ##################################################

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
        print (ERROR_HANDLE.get_alternative_traceback())
    finally:
        try:
            workbook.Close(False)
            excel_app.Quit()
        except:
            pass
        
    return OUT


def get_column_values(data, column, start_from_zero=False):
    """Extract all values from a specific column in Excel data.

    Args:
        data (list): Excel data as list of rows
        column (str|int): Column reference (letter or index)
        start_from_zero (bool, optional): If True, column indexing starts at 0.
            Defaults to False.

    Returns:
        list: All values found in the specified column
    """
    column = get_column_index(column, start_from_zero)
    result = defaultdict(list)
    for key, value_dict in data.items():
        if key[1] == column:
            result[value_dict["value"]].append(key[0])
    return dict(result)

def search_row_in_column_by_value(data, column, search_value, is_fuzzy=False, start_from_zero=False):
    """Search for a value in a specific column and return matching row indices.

    Args:
        data (list): Excel data as list of rows
        column (str|int): Column reference (letter or index)
        search_value (str): Value to search for
        is_fuzzy (bool, optional): If True, performs partial string matching.
            Defaults to False.
        start_from_zero (bool, optional): If True, column indexing starts at 0.
            Defaults to False.

    Returns:
        list: Indices of rows containing the search value
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

def save_data_to_excel(data, filepath, worksheet="EnneadTab", open_after=True, freeze_row=None, freeze_column=None):
    """Save data to a new Excel file with formatting.

    Creates a new Excel workbook and writes data with preserved formatting.
    Supports cell colors, borders, and other formatting options.

    Args:
        data (list): Data to write, can include ExcelDataItem objects
        filepath (str): Target Excel file path
        worksheet (str, optional): Name for the worksheet. Defaults to "EnneadTab".
        open_after (bool, optional): If True, opens file after saving.
            Defaults to True.
        freeze_row (int, optional): 1-based row number to freeze panes at.
            Defaults to None.
        freeze_column (str | int, optional): Excel column letter or 0-based column number to freeze panes at.
            Defaults to None.

    Returns:
        bool: True if save successful, False otherwise
    """
    def legacy_method():
        # note to self: rework the format method in dataitem so can construct any combonation format
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
                if data.is_bold:
                    format_dict["bold"] = True
                if data.border_style:
                    format_dict["border"] = data.border_style
                if data.border_color:
                    format_dict["border_color"] = COLOR.rgb_to_hex(data.border_color)
                if data.top_border_style:
                    format_dict["top"] = data.top_border_style
                if data.bottom_border_style:
                    format_dict["bottom"] = data.bottom_border_style
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

        worksheet_item = workbook.add_worksheet(worksheet)
        for data_entry in data:
            write_data_item(worksheet_item, data_entry)

        column_max_width_dict = dict()
        for entry in data:
            column, item = entry.column, entry.item
            if column not in column_max_width_dict.keys():
                column_max_width_dict[column] = 0
            column_max_width_dict[column] = max(
                column_max_width_dict[column], 1.1 * len(str(item))
            )

        for column in column_max_width_dict.keys():
            worksheet_item.set_column(column, column, column_max_width_dict[column])

        if freeze_row:
            worksheet_item.freeze_panes(freeze_row, 0)

        try:
            workbook.close()
            if not open_after:
                NOTIFICATION.messenger(main_text="Excel saved at '{}'".format(filepath))
        except Exception as e:
            print (ERROR_HANDLE.get_alternative_traceback())

        return True


    def new_method():
        job_data = {
            "mode": "write",
            "filepath": filepath,
            "worksheet": worksheet,
            "freeze_row": freeze_row,
            "freeze_column": freeze_column,
            "data": ExcelDataItem.convert_datas_to_dict(data)
        }
    
        DATA_FILE.set_data(job_data, "excel_handler_input.sexyDuck")
        DATA_FILE.set_data(job_data, "DEBUGER_excel_handler_input.sexyDuck")

        EXE.try_open_app("ExcelHandler")
        max_wait = 100
        wait = 0
        while wait<max_wait:
            job_data = DATA_FILE.get_data("excel_handler_input.sexyDuck")
            if job_data.get("status") == "done":
                break
            time.sleep(0.1)
            wait += 1

        return True
    
    if not new_method():
        print ("new method failed, using legacy method")
        legacy_method()
    
    if open_after and os.path.exists(filepath):
        os.startfile(filepath)


def check_formula(excel, worksheet, highlight_formula=True):
    """Validate and highlight Excel formulas in a worksheet.

    Checks for formula validity and optionally highlights cells containing formulas.
    Useful for debugging and auditing Excel files.

    Args:
        excel (str): Path to Excel file
        worksheet (str): Name of worksheet to check
        highlight_formula (bool, optional): If True, highlights formula cells.
            Defaults to True.

    Returns:
        dict: Formula validation results and cell locations
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


def parse_excel_data(data, key_name, header_row=1, ignore_keywords=None):
    """Parse Excel data into a structured format with dot notation access.
    
    Converts raw Excel data into a dictionary of objects where each row becomes a data entry.
    The value in the key_name column becomes the dictionary key, and all other columns
    become properties accessible via dot notation or dictionary-style access.
    
    Args:
        data (dict): Excel data as dict of coordinates and values
        key_name (str): Column header to use as key for each entry
        header_row (int, optional): Row number of the header row (1-based index). Defaults to 1.
        ignore_keywords (list, optional): List of keywords to ignore when creating entries. Defaults to None.
    
    Returns:
        dict: Dictionary of data objects with property access via dot notation
    """
    # Initialize variables
    ignore_keywords = ignore_keywords or []
    header_dict = {}
    header_indices = {}
    
    # First pass: collect headers
    for key, value_dict in data.items():
        row, column = key
        if row == header_row:
            header = value_dict["value"]
            if not header or header == "None":
                continue
            header_dict[column] = header
            header_indices[header] = column
    
    # Validate key column exists
    if key_name not in header_indices:
        print("Error: Key column '{}' not found in headers".format(key_name))
        return {}
    
    # Define the RowData class for dot notation access
    class RowData:
        """Container for row data with both dot notation and dictionary-style access."""
        
        def __init__(self, properties):
            """Initialize with column data from a row."""
            # Store both original and sanitized versions of properties
            self._original_keys = {}
            self._data = {}
            
            for key, value in properties.items():
                # Create a Python-friendly attribute name
                safe_key = key.replace(" ", "_")
                if value == "None":
                    value = None
                    
                # Set the attribute and track mappings
                setattr(self, safe_key, value)
                self._original_keys[safe_key] = key
                self._data[key] = value
                self._data[safe_key] = value
        
        def __getattr__(self, name):
            """Handle attribute access with helpful error messages."""
            # Try case-insensitive matching for keys with spaces
            original_spaces = name.replace("_", " ")
            for key in self._original_keys.values():
                if key.lower() == original_spaces.lower():
                    safe_key = key.replace(" ", "_")
                    return getattr(self, safe_key)
            
            # Show available attributes in error message
            attrs = [k for k in self.__dict__.keys() if not k.startswith('_')]
            raise AttributeError(
                "'RowData' object has no attribute '{}'. Available attributes: {}".format(
                    name, ", ".join(attrs)
                )
            )
        
        def get(self, key, default=None):
            """Access data dictionary-style with fallback support."""
            # Try direct access
            if key in self._data:
                return self._data[key]
            
            # Try with spaces converted to underscores
            safe_key = key.replace(" ", "_")
            if safe_key in self._data:
                return self._data[safe_key]
                
            # Try case-insensitive matching
            for k in self._data:
                if k.lower() == key.lower():
                    return self._data[k]
                    
            return default
        
        def __str__(self):
            """Generate a readable representation of the row data."""
            attrs = []
            for key, value in sorted(self.__dict__.items()):
                if key.startswith('_'):  # Skip internal attributes
                    continue
                    
                # Format based on type
                formatted_value = str(value) if value is not None else "None"
                
                # Show both access methods for keys with spaces
                orig_key = self._original_keys.get(key, key)
                key_info = "{} ('{}')".format(key, orig_key) if " " in orig_key else key
                attrs.append("  {}: {}".format(key_info, formatted_value))
            
            return "{\n" + "\n".join(attrs) + "\n}"
        
        def __repr__(self):
            """Return the same formatted string as __str__."""
            return self.__str__()

    # Function to check if a key should be ignored
    def should_ignore(key_value):
        """Check if key contains any ignore keywords."""
        if not ignore_keywords:
            return False
        return any(keyword in key_value for keyword in ignore_keywords)

    # Process rows into structured data
    result = {}
    current_row = None
    row_data = {}
    # Use a list for flag variables that need to be modified in nested functions
    duplicate_keys = [False]
    
    # Helper function to process each row's data - MOVED HERE before it's used
    def _process_row_data(row_data, result_dict):
        if key_name not in row_data:
            return
            
        key_value = row_data[key_name]
        if not key_value or key_value == "" or should_ignore(key_value):
            return
        if key_value == "None":
            return
                    
        if key_value in result_dict:
            print("Warning: Key '{}' already exists in output dictionary".format(key_value))
            duplicate_keys[0] = True
        
        result_dict[key_value] = RowData(row_data)
    
    # Sort keys to process row by row
    sorted_keys = sorted(data.keys())
    
    for location_key in sorted_keys:
        row, column = location_key
        if row <= header_row:
            continue
            
        # If we've moved to a new row, process the previous row
        if current_row is not None and current_row != row and row_data:
            _process_row_data(row_data, result)
            row_data = {}
        
        current_row = row
        
        # Get the header for this column
        if column in header_dict:
            header = header_dict[column]
            value = data[location_key]["value"]
            row_data[header] = value
    
    # Process the last row if it exists
    if current_row is not None and row_data:
        _process_row_data(row_data, result)
    
    # Report duplicate keys if found
    if duplicate_keys[0]:
        NOTIFICATION.messenger("Warning: some keys already exist in output dictionary. See details in console.")


    return result

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
    # filename = __file__
    # UNIT_TEST.pretty_test(test_dict, filename)
    # data = read_data_from_excel("J:\\2142\\0_BIM\\10_BIM Management\\10_BIM Resources\\Extended_DB.xlsx", worksheet="Keynote Extended DB", return_dict=True)
    # data = parse_excel_data(data, "KEYNOTE ID", ignore_keywords=["[Branch]", "[Category]"])

    # print (data)
    # for item in data.values():
        # print ("###############")
        # print (item.KEYNOTE_ID)
        # print (item.KEYNOTE_DESCRIPTION)
        # print (item.get("KEYNOTE ID"))
        # print (item.get("KEYNOTE DESCRIPTION"))

    collection = ExcelDataCollection()
    collection.set_headers(["Name", "Age", "City"], width_list=[10, 10])
    collection.add_row(["John", 30, "New York"])
    collection.add_row(["Jane", 25, "Los Angeles"])
    collection.add_row(["Jim", 35, "Chicago"])
    collection.add_row(["Jill", 28, "San Francisco"])
    collection.set_pointer_lower_right()
    collection.next_row()
    collection.add("That is many cities")
    collection.set_col_by_header("Age")
    collection.add(35)
    collection.prev_col()
    collection.add("Average age")
    collection.prev_row()
    collection.add("will override")
    collection.add(ExcelDataItem("as dedicated item", 10, "B"))
    collection.save("output.xlsx")
