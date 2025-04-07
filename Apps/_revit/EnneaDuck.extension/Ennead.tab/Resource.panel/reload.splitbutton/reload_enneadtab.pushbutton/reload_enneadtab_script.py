#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Reload entire UI so can get newer buttons....."
__title__ = "Reload\nEnneadTab"
__context__ = "zero-doc"
__tip__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from pyrevit.loader import sessionmgr
from pyrevit.loader import sessioninfo
from pyrevit import script
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def reload_EnneadTab():
    try:
        logger = script.get_logger()
        results = script.get_results()

        # re-load pyrevit session.
        logger.info('Reloading....')
        sessionmgr.reload_pyrevit()

        results.newsession = sessioninfo.get_session_uuid()
    except Exception as e:
        print ("Having issue reloading EnneadTab, please check company portal to update pyrevit.")
        ERROR_HANDLE.print_note(e)



################## main code below #####################
if __name__ == "__main__":
    if False and REVIT_APPLICATION.is_version_at_least(2025):
        NOTIFICATION.messenger("Please use pyrevit reload for Revit 2025 and above.")
    else:
        reload_EnneadTab()







