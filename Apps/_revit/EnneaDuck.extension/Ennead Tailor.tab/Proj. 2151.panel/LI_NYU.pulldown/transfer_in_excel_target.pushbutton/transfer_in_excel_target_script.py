#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Transfer In Excel Target"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, EXCEL
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def transfer_in_excel_target(doc):

    excel_path = "J:\\2151\\2_Master File\\B-70_Programming\\04_Area\\2025-03-06 Program Comparison 549 BED.xlsx"
    
    data = EXCEL.read_data_from_excel(excel_path, sheet_name="Hospital Program 549 bed")


    B_index = EXCEL.letter_to_index("B")

    for pointer in sorted(data.keys()):
        row, col = pointer
        col = EXCEL.column_number_to_letter(col)
        if col != "T":
            continue

        target_cell = data[pointer]
        target_cell_value = target_cell["value"]
        if not target_cell_value or target_cell_value == "":
            continue

        program_name = data[row, B_index]["value"]
        




    t = DB.Transaction(doc, __title__)
    t.Start()
    pass
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    transfer_in_excel_target(DOC)







