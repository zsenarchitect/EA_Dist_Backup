#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Set linked view for projects by a map."
__title__ = "Set Linked View"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, USER
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

MAPPING_DICT_EWING_COLE = {
    "title": "20230633_A24_CENTRAL",
    "level_maps": {
        "B1": "N/A",
        "L1": "FINAL CONCEPT PLAN - LEVEL 1_OPT 1",
        "L2": "L2",
        "L3": "FINAL CONCEPT PLAN - LEVEL 3",
        "L4": "FINAL CONCEPT PLAN - LEVEL 4_SD Decentralized Core",
        "L5 MEP": "LEVEL 5 REFERENCE PLAN",
        "L6": "FINAL CONCEPT PLAN - LEVEL 6_LDR+NICU",
        "L7": "FINAL CONCEPT PLAN - LEVEL 7",
        "L8": "FINAL CONCEPT PLAN - LEVEL 8",
        "L9": "N/A",
        "L10": "N/A",
        "L11": "N/A",
        "L12": "N/A",
        "L13 MEP": "N/A",
        "ROOF LEVEL": "N/A",
        "T.O.CORE": "N/A",
    }
}

MAPPING_DICT_EXT = {
    "title": "2151_A_EA_NYULI_Hospital_EXT",
    "level_maps": {
        "B1": "T-000_10_T Tower B1(Phase I)",
        "L1": "T-001_10_T Tower L1(Phase I)",
        "L2": "T-002_10_T Tower L2(Phase I)",
        "L3": "T-003_10_T Tower L3(Phase I)",
        "L4": "T-004_10_T Tower L4(Phase I)",
        "L5 MEP": "T-005_10_T Tower L5 MEP(Phase I)",
        "L6": "T-006_10_T Tower L6(Phase I)",
        "L7": "T-007_10_T Tower L7(Phase I)",
        "L8": "T-008_10_T Tower L8(Phase I)",
        "L9": "T-009_10_T Tower L9(Phase I)",
        "L10": "T-010_10_T Tower L10(Phase I)",
        "L11": "T-011_10_T Tower L11(Phase I)",
        "L12": "T-012_10_T Tower L12(Phase I)",
        "L13 MEP": "T-013_10_T Tower L13 MEP(Phase I)",
        "ROOF LEVEL": "T-014_10_ROOF LEVEL(Phase I)",
        "T.O.CORE": "T-015_10_T Tower T.O.CORE(Phase I)",
    },
    # use view map for more detailed control such as context and phasing
    "view_maps": {
        "my view": "link view",
    }
}
PRINK_LINK_VIEW_NAMES = False
if USER.IS_DEVELOPER:
    PRINK_LINK_VIEW_NAMES = False # change to to True for personal debugging



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def set_linked_view(doc):
    t = DB.Transaction(doc, __title__)
    t.Start()
    REVIT_VIEW.process_link(doc, MAPPING_DICT_EWING_COLE, print_link_view_names = PRINK_LINK_VIEW_NAMES)
    REVIT_VIEW.process_link(doc, MAPPING_DICT_EXT, print_link_view_names = PRINK_LINK_VIEW_NAMES)
    t.Commit()





################## main code below #####################
if __name__ == "__main__":
    from pyrevit import script
    output = script.get_output()

    set_linked_view(DOC)





