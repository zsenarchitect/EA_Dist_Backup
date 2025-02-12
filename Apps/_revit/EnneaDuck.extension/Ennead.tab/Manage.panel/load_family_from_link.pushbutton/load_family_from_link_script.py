#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Load family from linked revit file without open those links."
__title__ = "Load Family\nFrom Link"
__tip__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, UI
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_FAMILY, REVIT_APPLICATION
from pyrevit.revit import ErrorSwallower

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def load_family_from_link():
    link_doc = REVIT_SELECTION.pick_revit_link_docs(select_multiple=False)
    if not link_doc:
        return

    families = REVIT_SELECTION.pick_family(link_doc, 
                                         multi_select=True)
    if not families:
        return

    def loader(family, doc):
        with ErrorSwallower() as swallower:
            family_doc = link_doc.EditFamily(family)
            REVIT_FAMILY.load_family(family_doc, doc)
            family_doc.Close(False)


            
    UI.progress_bar(families, 
                    lambda x:loader(x, DOC), 
                    label_func=lambda x: "Loading Family [{}]".format(x.Name), 
                    title="Loading Families")


    



################## main code below #####################
if __name__ == "__main__":
    load_family_from_link()







