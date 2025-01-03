#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Set the smallest detail number on sheet viewport to be 10."
__title__ = "Auto Detail Num"

#
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def auto_detail_num():
    


    t = DB.Transaction(doc, __title__)
    t.Start()
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    for sheet in all_sheets:
        views = [doc.GetElement(x) for x in sheet.GetAllPlacedViews ()]
        for view in views:
            if view.ViewType not in [DB.ViewType.FloorPlan,
                                    DB.ViewType.CeilingPlan,
                                    DB.ViewType.Elevation,
                                    DB.ViewType.ThreeD,
                                    DB.ViewType.DraftingView,
                                    DB.ViewType.Section,
                                    DB.ViewType.Detail]:
                continue
            if view.LookupParameter("Detail Number").AsString() == "1":
                view.LookupParameter("Detail Number").Set("10")
                break
    t.Commit()


"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    auto_detail_num()
    





