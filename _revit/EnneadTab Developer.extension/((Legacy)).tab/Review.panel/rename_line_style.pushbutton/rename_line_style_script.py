#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Replace part of name in linestyle to another user defined text. Handy when you want to rename linestyles from another firm."
__title__ = "Rename\nLine Style"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def rename_line_style():

    key = forms.ask_for_string(default = "keywords to search")
    replacement = forms.ask_for_string(default = "replacement to the keys")


    t = DB.Transaction(doc, "rename line style")
    t.Start()
    line_category = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    line_subcs = line_category.SubCategories
    line_style_name_pool = [x.Name for x in line_subcs]
    for line_style in line_subcs:

        type = doc.GetElement(line_style.Id)
        if type is None:
            continue
        #print line_style
        #print line_style.Name

        old_name = line_style.Name
        if key in old_name:
            new_name = old_name.replace(key, replacement)

            if new_name in line_style_name_pool:
                print("Cannot rename {}--->{} becasue there is a overlapping name.".format(old_name, line_style.Name))
                continue


            type.Name = new_name
            print("{}--->{}".format(old_name, line_style.Name))
            line_style_name_pool.remove(old_name)
            line_style_name_pool.append(new_name)


    t.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    rename_line_style()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
