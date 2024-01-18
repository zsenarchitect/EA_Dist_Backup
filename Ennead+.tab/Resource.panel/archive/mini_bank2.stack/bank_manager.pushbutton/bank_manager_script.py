#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Manager people's saving account."
__title__ = "Bank Manager"
__context__ = 'zero-doc'
# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI


def bank_manager():
    if not EnneadTab.USER.is_SZ():
        EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "This function is only available to Sen Zhang.")
        return

    ENNEAD_LOG.manual_transaction()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    bank_manager()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
