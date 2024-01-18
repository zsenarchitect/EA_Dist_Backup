#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Honk Honk Honk Honk!\n(Hold ESC to get rid of goose. There is a progress bar on top-left corner when you hold ESC)\n\nBig thanks to Samperson for the fun creation and put it free online."
__title__ = "Hello\nGoose!"
__context__ = 'zero-doc'

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI
#doc = __revit__.ActiveUIDocument.Document

def show_goose():
    exe_location = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Project Settings\exe\DesktopGoose\GooseDesktop.exe - Shortcut"



    try:
        EA_UTILITY.open_file_in_default_application(exe_location)
        return
    except Exception as e:
        pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    show_goose()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
