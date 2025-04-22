# -*- coding: utf-8 -*-
import REVIT_APPLICATION

try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

def get_sheet_by_sheet_num( sheet_num, doc = DOC):
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements()
    
    for sheet in all_sheets:
        if sheet.SheetNumber == sheet_num:
            return sheet
    return None


def get_sheet_by_view(view, doc = DOC):
    if view.LookupParameter("Sheet Number") is None:
        return None
    if view.LookupParameter("Sheet Number").AsString() == "---":
        return None
    sheet_num = view.LookupParameter("Sheet Number").AsString()
    sheet = get_sheet_by_sheet_num(sheet_num, doc)
    return sheet

    sheet_id = view.OwnerViewId
    if sheet_id is None or sheet_id == DB.ElementId.InvalidElementId:
        return None
    sheet = doc.GetElement(sheet_id)
    if sheet is None or not isinstance(sheet, DB.ViewSheet):
        return None
    return sheet
