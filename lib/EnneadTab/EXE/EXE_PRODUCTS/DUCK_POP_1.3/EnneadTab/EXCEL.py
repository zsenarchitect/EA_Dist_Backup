#!/usr/bin/python
# -*- coding: utf-8 -*-
import ENVIRONMENT
import EXE
import NOTIFICATION

import sys
#
# 设定了输出的环境为utf8
sys.setdefaultencoding('utf-8')
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
try:
    import xlrd
    import xlsxwriter
except:
    pass



class ExcelDataItem():
    def __init__(self, item, row, column):
        self.item = item
        self.row = row
        self.column = column


def get_all_worksheets(filepath):

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def read_data_from_excel(filepath, worksheet = "Sheet1", by_line = True):


    wb = xlrd.open_workbook(filepath)#, encoding_override = "cp1252")#""big5")#"iso2022_jp_2")#"gb18030")#"gbk")#"hz")  #"gb2312")   #"utf8"
    try:
        sheet = wb.sheet_by_name(worksheet)
    except:
        
        NOTIFICATION.messager(main_text = "Cannot open worksheet: {}".format(worksheet))
        return None
    #print sheet.cell_value(2, 1)
    OUT = []

    for i in range(0, sheet.nrows):
        OUT.append(sheet.row_values(i))
    return OUT



def save_data_to_excel(data, filepath, worksheet = "EnneadTab", open_after = True):



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


            RHINO.FORMS.notification(main_text = "Excel saved at '{}'".format(filepath), height = 500)
    except:
        RHINO.FORMS.notification(main_text = "the excel file you picked is still open, cannot override. Writing cancelled.", height = 500)
        return

    if open_after:
        EXE.open_file_in_default_application(filepath)



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")