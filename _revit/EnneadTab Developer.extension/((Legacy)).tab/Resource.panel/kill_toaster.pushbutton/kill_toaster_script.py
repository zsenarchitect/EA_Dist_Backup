#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "So you don't want to see the corner popup ever again...\nSad, but here you can gloablly turn that off. With the exception of a few key popup, most popup will be disabled.\n\nYou can enable them again in here as well."
__title__ = "(un)Kill Corner\nPopup Msg"
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

def kill_toaster():
    opts = [["Kill corner popup message! I hate it sooooo much!!!", "Do not show it anywhere, except super important messages."],
            "I like the popup message box to keep me informed."]
    res = EA_UTILITY.dialogue(main_text = "What do you want to do?", options = opts)

    dump_folder = EA_UTILITY.get_EA_local_dump_folder()
    file_name = "EA_TOASTER_KILL.kill"
    filepath = "{}\{}".format(dump_folder, file_name)
    if res == opts[0][0]:
        with open(filepath, 'w') as f:
            # f.writelines(list)
            f.write("Kill!")
    else:
        import os
        if EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder):
            os.remove(os.path.join(dump_folder, file_name))


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    kill_toaster()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
