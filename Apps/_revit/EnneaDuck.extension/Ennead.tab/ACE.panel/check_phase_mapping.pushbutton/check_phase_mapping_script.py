#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Get the phase mapping of mutiple documents."
__title__ = "Check\nPhase Mapping"
__tip__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_PHASE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def check_phase_mapping():
    docs = REVIT_APPLICATION.select_top_level_docs()
    if not docs:
        return
    for doc in docs:
        REVIT_PHASE.pretty_print_phase_map(doc)



################## main code below #####################
if __name__ == "__main__":
    check_phase_mapping()







