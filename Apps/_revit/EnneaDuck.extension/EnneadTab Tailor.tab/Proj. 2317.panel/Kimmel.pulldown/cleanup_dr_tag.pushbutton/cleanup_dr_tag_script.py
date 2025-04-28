#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Cleanup Dr Tag"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_TAG
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def cleanup_dr_tag(doc):
    bad_name = "TAG_Door_work"

    t = DB.Transaction(doc, __title__)
    t.Start()
    all_tags = DB.FilteredElementCollector(doc).OfClass(DB.IndependentTag).WhereElementIsNotElementType().ToElements()
    all_tags = [el for el in all_tags if doc.GetElement(el.GetTypeId()).FamilyName == bad_name]

    for tag in all_tags:
        tagged_elements = REVIT_TAG.get_tagged_elements(tag, doc)
        if not tagged_elements:
            continue
            
        for element in tagged_elements:
            if element and hasattr(element, "Symbol") and "NEST" in element.Symbol.LookupParameter("Type Mark").AsString():
                doc.Delete(tag.Id)
                break
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    cleanup_dr_tag(DOC)







