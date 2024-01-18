#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "<Available When Editing Family>\nChange family unit to different display style. So you can quickly convert family from Imperial Library to Metric Unit. \n\nNote that the actauly dimension might comes with extra digits after unit changed."
__title__ = "Change Family Unit"
__context__ = "doc-family"
# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # fastest DB
# from Autodesk.Revit import UI
doc = __revit__.ActiveUIDocument.Document

def change_family_unit():

    family_docs = EnneadTab.REVIT.REVIT_APPLICATION.select_family_docs(select_multiple = True, including_current_doc = True)
    if not family_docs:
        return

    target_units = ["Millimeters + Square Meters", "Feet + Square Feet", "Inches + Square Feet"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue( title = "EnneadTab",
                                                main_text = "Which unit system to use?",
                                                sub_text = "For Length and Area unit",
                                                options = target_units)

    if not res:
        return

    if res == target_units[0]:
        unit_type_length = "millimeters"
        unit_type_area = "squareMeters"
    elif res == target_units[1]:
        unit_type_length = "feet"
        unit_type_area = "squareFeet"
    else:
        unit_type_length = "inches"
        unit_type_area = "squareFeet"

    unit_type_length = EnneadTab.REVIT.REVIT_UNIT.lookup_unit_id(unit_type_length)
    unit_type_area = EnneadTab.REVIT.REVIT_UNIT.lookup_unit_id(unit_type_area)

    map(lambda x: process_family(x, unit_type_length, unit_type_area), family_docs)


    note = ""
    for doc in family_docs:
        note += "\n{}".format(doc.Title)
    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "The following family unit have been changed to {}".format(res), sub_text = note )


def process_family(family_doc, unit_type_length, unit_type_area):
    #print unit_type_length
    t = DB.Transaction(family_doc, __title__)
    t.Start()
    family_unit = family_doc.GetUnits()

    length_spec = EnneadTab.REVIT.REVIT_UNIT.lookup_unit_spec_id("length")
    format_option = family_unit.GetFormatOptions (length_spec)
    format_option.SetUnitTypeId  (unit_type_length)
    family_unit.SetFormatOptions (length_spec, format_option)

    area_spec = EnneadTab.REVIT.REVIT_UNIT.lookup_unit_spec_id("area")
    format_option = family_unit.GetFormatOptions (area_spec)
    format_option.SetUnitTypeId (unit_type_area)
    family_unit.SetFormatOptions (area_spec, format_option)


    family_doc.SetUnits(family_unit)
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    change_family_unit()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
