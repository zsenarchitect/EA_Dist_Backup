#!/usr/bin/python
# -*- coding: utf-8 -*-


__context__ = 'zero-doc'
__doc__ = "Check out the action history of a specific user from the Mini Bank Log. The result will include recent working files, current coins, and recent actions."
__title__ = "Check User History"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
#doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def check_history():
    ENNEAD_LOG.print_history()

    """
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    check_history()
    #ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__, show_toast = True)
