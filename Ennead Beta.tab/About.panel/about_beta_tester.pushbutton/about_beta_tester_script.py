#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Details on your responsibility as a beta tester"
__title__ = "About\nBeta Tester"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI
doc = __revit__.ActiveUIDocument.Document

def about_beta_tester():
    try:
        og_pdf = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\bin\beta_tester_welcome.pdf"
        new_pdf = EnneadTab.FOLDER.copy_file_to_local_dump_folder(og_pdf)
        #print new_pdf
        EnneadTab.EXE.open_file_in_default_application(new_pdf)
    except Exception as e:
        print e
        EnneadTab.EXE.open_file_in_default_application(og_pdf)
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    about_beta_tester()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)












