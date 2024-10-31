#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Temp Excel Reader"
__context__ = "zero-doc"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import os

from EnneadTab import ERROR_HANDLE, LOG, EXCEL
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()
DEPARTMENT_PARA_MAPPING = {"DIAGNOSTIC AND TREATMENT": "D&T",
                        "AMBULATORY CARE": "AMBULATORY CARE",
                        "EMERGENCY DEPARTMENT": "ED",
                        "INPATIENT CARE": "BEDS",
                        "PUBLIC SUPPORT": "PUBLIC SUPPORT",
                        "ADMINISTRATION AND STAFF SUPPORT": "ADMIN",
                        "CLINICAL SUPPORT": "CLINICAL SUPPORT",
                        "BUILDING SUPPORT": "BUILDING SUPPORT",
                        "UNASSIGNED": "UNASSIGNED"}

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def temp_excel_reader():
    source_excel = "{}\\DC\\ACCDocs\\Ennead Architects LLP\\2151_NYULI\\Project Files\\00_EA-EC Teams Files\\4_Programming\\_Public Shared\\Web Portal Only_ACTIVE.NYULI_Program_EA.EC.xls".format(os.getenv("USERPROFILE"))
    # source_excel = FOLDER.get_EA_dump_folder_file("temptemp.xlsx")
    # NOTIFICATION.duck_pop(main_text="using testing file for now.")
    data = EXCEL.read_data_from_excel(source_excel, worksheet="EA Benchmarking DGSF Tracker", return_dict=True)

    print(data)        
    key_column = "B"
    print ("avaibale excel departments: {}".format(EXCEL.get_column_values(data, key_column)))
    for department_name in DEPARTMENT_PARA_MAPPING.keys():
        row = EXCEL.search_row_in_column_by_value(data, key_column, search_value=department_name, is_fuzzy=True)

        target = data.get((row,EXCEL.get_column_index("P")), None)
        if target:
            target = float(target)
            print ("target value found for [{}]: {}".format(department_name, target))
            # dummy_target_data.update(self.option.DEPARTMENT_PARA_MAPPING[department_name], target)
            print ("\n\n")  


################## main code below #####################
if __name__ == "__main__":
    temp_excel_reader()







