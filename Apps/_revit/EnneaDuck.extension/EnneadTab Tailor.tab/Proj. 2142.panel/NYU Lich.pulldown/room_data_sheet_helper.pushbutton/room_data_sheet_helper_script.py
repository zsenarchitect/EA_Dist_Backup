#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Room Data Sheet Helper"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def room_data_sheet_helper(doc):
    if not doc.IsFamilyDocument:
        print("This is not a family document. Please open a family document.")
        return

    # Print all TextElement elements in the current document
    print("All TextElement elements in the current document:")
    print("=" * 60)
    idx = 0
    for elem in DB.FilteredElementCollector(doc).OfClass(DB.TextElement).WhereElementIsNotElementType().ToElements():
        try:
            name = elem.Name if hasattr(elem, "Name") else "<No Name>"
        except:
            name = "<No Name>"
        print("[{}]".format(idx))
        print("  Name: {}".format(name))
        print("  Element Id: {}".format(elem.Id))
        print("  Element Type: {}".format(type(elem)))
        print("  Parameters:")
        try:
            for param in elem.Parameters:
                try:
                    pname = param.Definition.Name
                    pval = param.AsValueString() or param.AsString() or str(param.AsInteger())
                except:
                    pname = "<Unknown>"
                    pval = "<Unknown>"
                print("    {}: {}".format(pname, pval))
                # Try to extract referenced parameter(s) for 'Label' property
                if pname == "Label":
                    try:
                        # Try to get as ElementId (may be a single or list)
                        ids = param.AsElementId()
                        if isinstance(ids, DB.ElementId):
                            ids = [ids]
                        print("    Label parameter references ElementIds: {}".format([id.IntegerValue for id in ids]))
                        for id in ids:
                            ref_elem = doc.GetElement(id)
                            if ref_elem:
                                ref_name = getattr(ref_elem, 'Name', '<No Name>')
                                print("      -> Referenced element: {}, Name: {}".format(ref_elem, ref_name))
                    except Exception as e:
                        print("    Label parameter could not be resolved as ElementId list: {}".format(e))
        except:
            print("    <No Parameters>")
        print("-" * 60)
        idx += 1

################## main code below #####################
if __name__ == "__main__":
    room_data_sheet_helper(DOC)







