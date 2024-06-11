#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "So you don't want to hear the EnneadTab Talkie ever again..."
__title__ = "(un)Mute That\nTalkie Lady!"
__context__ = 'zero-doc'
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def kill_TTS():
    import imp
    full_file_path = r'C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_1.stack\text2speech.pushbutton\TTS_script.py'
    if not EnneadTab.USER.is_SZ():
        full_file_path = EnneadTab.FOLDER.remap_filepath_to_folder(full_file_path)
    ref_module = imp.load_source("TTS_script", full_file_path)

    ref_module.kill_TTS()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    kill_TTS()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
