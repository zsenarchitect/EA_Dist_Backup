#!/usr/bin/python
# -*- coding: utf-8 -*-


__context__ = 'zero-doc'
__doc__ = "Get the detail report of what happened to a person."
__title__ = "Review\nError Reports"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI
#doc = __revit__.ActiveUIDocument.Document
import ENNEAD_LOG
def review_error_log():
    ENNEAD_LOG.print_error_log()
    """
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
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
    review_error_log()
