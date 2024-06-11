#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Create BetaTester Annoucement"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import sys
sys.path.append(r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\lib")
import EnneadTab
import ENNEAD_LOG

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def create_beta_tester_annoucement():

    
    #EnneadTab.NOTIFICATION.publish_new_topic(topic = "2023-06-01: Update Setting", beta_tester_only = True)
    EnneadTab.NOTIFICATION.publish_new_topic(topic = "2023-06-20: Update UI", beta_tester_only = True)

   
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    create_beta_tester_annoucement()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)




