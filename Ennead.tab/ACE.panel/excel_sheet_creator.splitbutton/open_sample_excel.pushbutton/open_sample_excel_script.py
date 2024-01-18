#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Get a sample excel to fill out data in similar format.
Using those format will make it easy to generate dummy sheets in Revit.
Please note that Chinese translation will require special care when saving excel format."""
__title__ = "Open Sample Excel"
__context__ = "zero-doc"
__tip__ = True

from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()



     
@EnneadTab.ERROR_HANDLE.try_catch_error
def open_sample_excel():
    
    excel_path = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\Ennead.tab\ACE.panel\Project Starter.pushbutton\Make Sheet With Excel.xlsx"
    copy = EnneadTab.FOLDER.copy_file_to_local_dump_folder(excel_path,
                                                           "Sample Sheet Creation Data.xlsx")
    EnneadTab.EXE.open_file_in_default_application(copy)


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    open_sample_excel()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)











