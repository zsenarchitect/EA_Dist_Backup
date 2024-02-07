#!/usr/bin/python
# -*- coding: utf-8 -*-


__context__ = 'zero-doc'
__doc__ = "Do you want to know where you are ranking among everyone who is using EnneadTab for Revit?\nCheck this out, the result might shock you!"
__title__ = "Check Mini Bank\nLeader Board"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
#doc = __revit__.ActiveUIDocument.Document

def check_mini_bank_leader_board():
    ENNEAD_LOG.print_leader_board()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    check_mini_bank_leader_board()

    #ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__, show_toast = True)
