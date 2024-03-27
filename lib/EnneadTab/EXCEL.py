#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
try:
    # 设定了输出的环境为utf8
    sys.setdefaultencoding('utf-8')
except:
    pass


import ENVIRONMENT
import EXE
import NOTIFICATION

if ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
    sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
    import xlrd
    import xlsxwriter


class ExcelDataItem():
    def __init__(self, item, row, column):
        self.item = item
        self.row = row
        self.column = column


def get_all_worksheets(filepath):

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def read_data_from_excel(filepath, worksheet = "Sheet1", by_line = True, return_dict=False):


    wb = xlrd.open_workbook(filepath,formatting_info=return_dict)#, encoding_override = "cp1252")#""big5")#"iso2022_jp_2")#"gb18030")#"gbk")#"hz")  #"gb2312")   #"utf8"
    try:
        sheet = wb.sheet_by_name(worksheet)
    except:
        
        NOTIFICATION.messenger(main_text = "Cannot open worksheet: {}".format(worksheet))
        return None
    #print sheet.cell_value(2, 1)
    
    
    if not return_dict:
    
        OUT = []

        for i in range(0, sheet.nrows):
            OUT.append(sheet.row_values(i))
        return OUT
    
    
    # from collections import OrderedDict
    # OUT = OrderedDict()
    
    
    # OUT = {}
    # for i in range(0, sheet.nrows):
    #     for j in range(sheet.ncols):
    #         cell = sheet.cell(i, j)
    #         text_value = cell.value
            

    #         # Get color
    #         xf_index = sheet.cell_xf_index(i, j)
    #         xf = wb.xf_list[xf_index]
    #         bgx = xf.background.pattern_colour_index
    #         rgb = wb.colour_map.get(bgx) 

    #         # Store in dictionary
    #         OUT[(i, j)] = {'value': text_value, 'color': rgb}
    #         # if i == 2:
    #         #     print (OUT[(i, j)])
            
    # return OUT
    
    
    import clr
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel
    excel_app = Excel.ApplicationClass()
    excel_app.Visible = False

    workbook = excel_app.Workbooks.Open(filepath)
    sheet = workbook.Sheets[worksheet]
    
    import COLOR
    OUT = {}
    for i in range(1, sheet.UsedRange.Rows.Count + 1):
        for j in range(1, sheet.UsedRange.Columns.Count + 1):
            cell = sheet.Cells[i, j]
            decimal_color = cell.Interior.Color
            rgb_color = COLOR.decimal_to_rgb(decimal_color)
            cell_value = cell.Value2 if cell.Value2 is not None else ""
            
            # note to self, use i-1 and j-1 becaome the index starting method is different for clr called method
            OUT[(i-1, j-1)] = {'value': cell_value, 'color': rgb_color}
            
            
    workbook.Close(False)
    excel_app.Quit()
    # print OUT

    return OUT



def save_data_to_excel(data, filepath, worksheet = "EnneadTab", open_after = True):
    """_summary_

    Args:
        data (list): list of Excel Data item that has row, column, item attr.
        the order is handled before the data entry
        
        
        filepath (_type_): _description_
        worksheet (str, optional): _description_. Defaults to "EnneadTab".
        open_after (bool, optional): _description_. Defaults to True.
    """


    def write_data_item(worksheet, data):
        worksheet.write(data.row,
                        data.column,
                        data.item)

    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet(worksheet)
    for data_entry in data:
        write_data_item(worksheet, data_entry)


    column_max_width_dict = dict()
    for entry in data:
        column, item = entry.column, entry.item
        if column not in column_max_width_dict.keys():
            column_max_width_dict[column] = 0
        column_max_width_dict[column] = max(column_max_width_dict[column], 1.2 * len(str(item)))

    for column in column_max_width_dict.keys():
        worksheet.set_column(column,column , column_max_width_dict[column])

    import RHINO

    try:
        workbook.close()
        if not open_after:


            RHINO.RHINO_FORMS.notification(main_text = "Excel saved at '{}'".format(filepath), height = 500)
    except:
        RHINO.RHINO_FORMS.notification(main_text = "the excel file you picked is still open, cannot override. Writing cancelled.", height = 500)
        return

    if open_after:
        EXE.open_file_in_default_application(filepath)


def unit_test():
    return
    import xlrd
    import WEB

    # Replace this with your SharePoint URL
    sharepoint_url = "https://enneadarch-my.sharepoint.com/:x:/g/personal/scott_mackenzie_ennead_com/Eey-gTYaVIdGuU9Jg65gig8BIUBmc32Aie-0nNsjVSgUfQ?rtime=4PY2woUX3Eg"

    # Open the Excel file from the URL
    str = WEB.get_request(sharepoint_url)
    print (str)
    workbook = xlrd.open_workbook(file_contents=str)

    # Select the first sheet (you can change the sheet index as needed)
    sheet = workbook.sheet_by_index(0)

    # Iterate through rows and print each row
    for row_num in range(sheet.nrows):
        row = sheet.row_values(row_num)
        print(row)



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")