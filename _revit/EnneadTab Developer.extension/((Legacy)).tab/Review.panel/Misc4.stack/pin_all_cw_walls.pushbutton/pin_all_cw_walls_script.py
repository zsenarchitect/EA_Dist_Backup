#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Pin or Unpin all curtain walls in the projects."
__title__ = "(un)Pin All CW Walls"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


class Solution:



    def pin_all_cw_walls(self):



        options = ["Pin All CW Walls", "Un-Pin All CW Walls"]
        res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = options, main_text = "I want to [.....]")
        if not res:
            return


        if res == options[1]:
            self.pin_option = False
        elif res == options[0]:
            self.pin_option = True

        walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

        # for x in walls:
        #     print str(x.WallType.Kind)

        walls = filter(lambda x: str(x.WallType.Kind) == "Curtain", walls)

        self.count = 0
        t = DB.Transaction(doc, __title__)
        t.Start()
        map(self.update_pin, walls)
        t.Commit()
        action = "Pin" if self.pin_option else "Un-pin"
        text = '{} {} curtain walls'.format(action, self.count)
        already_fixed_count = len(walls) - self.count
        text += '\n{} curtain wall were already {}ed.'.format(already_fixed_count, action)
        print(text)

    def update_pin(self, element):
        if element.Pinned != self.pin_option:
            element.Pinned = self.pin_option
            self.count += 1
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    Solution().pin_all_cw_walls()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



