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


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ENVIRONMENT, MODULE_HELPER, LOG

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def ChatGPT():
    
    module_path = "{}\\Utility.panel\\exe_2.stack\\chatGPT.pushbutton\\chatGPT_script.py".format(ENVIRONMENT.REVIT_PRIMARY_TAB)
    func_name = "main"
    MODULE_HELPER.run_func_in_module(module_path, func_name)


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    ChatGPT()
    
