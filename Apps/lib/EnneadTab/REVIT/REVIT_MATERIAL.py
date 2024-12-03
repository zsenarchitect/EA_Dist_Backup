# -*- coding: utf-8 -*-



import REVIT_APPLICATION
try:

    from Autodesk.Revit import DB # pyright: ignore
    UIDOC = REVIT_APPLICATION.get_uidoc() 
    DOC = REVIT_APPLICATION.get_doc()
    

    
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()


def get_material_by_name(material_name, doc = DOC):
    all_materials = DB.FilteredElementCollector(doc).OfClass(DB.Material).ToElements()
    
    for material in all_materials:
        if material.Name == material_name:
            return material
    return None


