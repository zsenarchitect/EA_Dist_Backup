#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Fire UP ChatGPT in Revit.\n\nIt can answer any questions you might have."
__title__ = "ChatGPT"
__context__ = 'zero-doc'
__youtube__ = "https://youtu.be/NoJmQ7GFzMs"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29655"
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
doc = __revit__.ActiveUIDocument.Document

def ChatGPT():
    #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_2.stack\chatGPT.pushbutton\chatGPT_script.py
    module_path = "{}\ENNEAD.extension\Ennead.tab\Utility.panel\exe_2.stack\chatGPT.pushbutton\chatGPT_script.py".format(EnneadTab.ENVIRONMENT.get_EnneadTab_For_Revit_root())
    func_name = "main"
    EnneadTab.MODULE_HELPER.run_func_in_module(module_path, func_name)


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    ChatGPT()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
