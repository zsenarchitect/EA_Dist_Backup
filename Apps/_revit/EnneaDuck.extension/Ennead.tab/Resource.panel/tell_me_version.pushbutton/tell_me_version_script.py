#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Version information utility that displays the current build details for all EnneadTab components. This diagnostic tool provides complete version numbers, build dates, and update status for your installation - essential for troubleshooting, submitting bug reports, or verifying you have the latest features. Perfect for confirming compatibility when working with team members or when communicating with EnneadTab support."
__title__ = "Tell Me\nVersion"
__context__ = "zero-doc"
__tip__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab import VERSION_CONTROL
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def tell_me_version():
    VERSION_CONTROL.show_last_success_update_time()




################## main code below #####################
if __name__ == "__main__":
    tell_me_version()







