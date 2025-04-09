#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Get a sample excel to fill out data in similar format.
Using those format will make it easy to generate dummy sheets in Revit.
Please note that Chinese translation will require special care when saving excel format."""
__title__ = "Open Sample Excel"
__context__ = "zero-doc"
__tip__ = True

from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, EXE, FOLDER, ENVIRONMENT, LOG
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_sample_excel():
    
    excel_path = "{}\EnneadTab.tab\ACE.panel\Project Starter.pushbutton\Make Sheet With Excel.xls".format(ENVIRONMENT.REVIT_PRIMARY_EXTENSION)
    copy = FOLDER.copy_file_to_local_dump_folder(excel_path,
                                                "Sample Sheet Creation Data.xls")
    EXE.try_open_app(copy)


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    open_sample_excel()
    











