#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Pick a text you might want to use in your document.\n\nYou can also \
find commonly used symmbol in sheet schedule such as\nblack square ‎■\nbalck circle ●\nblack triangle ▲"
__title__ = "Pick Emoji Text"
__context__ = "zero-doc"
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def pick_emoji_text():
    EA_UTILITY.pick_emoji_text()

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print "Wrapper func for EA Log -- Begin:"
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print str(e)
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    pick_emoji_text()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
