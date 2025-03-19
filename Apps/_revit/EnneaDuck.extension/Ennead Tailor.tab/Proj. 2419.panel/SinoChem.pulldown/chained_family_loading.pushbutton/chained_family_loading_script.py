#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Chained Family Loading"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

from pyrevit import forms


# Define family loading orders for different design scenarios
LOADING_ORDERS = {
    "reveal": [
        ("sample_panel_flat_Revised", "tower_reveal_panel_main", False),
    ],
    
    "tower": [
        # Tower loading order to be defined
    ],
    
    "podium": [
        ("sample_panel_flat", "sample_panel_flat_host", False),
        ("sample_panel_flat_host", "podium_panel_main", False), 
        ("sample_panel_flat", "sample_panel_arc_helper", True),
        ("sample_panel_arc_helper", "sample_panel_arc_host", True),
        ("sample_panel_arc_host", "podium_panel_main", True)
    ]
}

# Get user selection for which design scenario to load
design = forms.SelectFromList.show(sorted(LOADING_ORDERS.keys()), 
                                 title="Select Design Scenario",
                                 multiselect=False)

# Set loading order based on selection
ORDER = LOADING_ORDERS.get(design, [])


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def chained_family_loading(doc):


    for order_detail in ORDER:
        source_family, target_family, should_close_source = order_detail
        print ("{} --> {}".format(source_family, target_family))
        source_family_doc = REVIT_APPLICATION.get_document_by_name(source_family)
        target_family_doc = REVIT_APPLICATION.get_document_by_name(target_family)
        if source_family_doc is None:
            print ("source family {} not found".format(source_family))
            continue
        if target_family_doc is None:
            print ("target family {} not found".format(target_family))
            continue
        REVIT_FAMILY.load_family(source_family_doc, target_family_doc)
        if should_close_source:
            REVIT_APPLICATION.switch_away_from_family(source_family)
            try:
                source_family_doc.Close(False)
            except:
                pass
        


################## main code below #####################
if __name__ == "__main__":
    chained_family_loading(DOC)







