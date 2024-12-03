#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "This tool updates life safety parameters in a Revit project, ensuring compliance with occupancy and egress requirements."
__title__ = "Update Life Safety"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

import traceback

from Autodesk.Revit import DB # pyright: ignore 

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_LIFE_SAFETY, REVIT_SELECTION, REVIT_VIEW, REVIT_FORMS

from pyrevit import forms
# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_life_safety(doc):

    data_source = REVIT_LIFE_SAFETY.SpatialDataSource(
                source = "Room",
                area_scheme_name = "Apple",
                 para_name_load_per_area = "Rooms_$LS_Occupancy AreaPer",
                 para_name_load_manual = "Rooms_$LS_Occupancy Load_Dummy",
                 para_name_target = "Rooms_$LS_Occupancy Load_Target",
                 para_name_egress_id = "Door_$LS_Exit Name",
                 para_name_door_width = "Door_$LS_Clear Width",
                 para_name_door_capacity_required = "Door_$LS_Capacity_Required",
                 para_name_stair_width = "Door_$LS_Stair Width"
                 )
    t = DB.Transaction(doc, "Load Life Safety Calculator")
    t.Start()
    REVIT_LIFE_SAFETY.load_life_safety_calculator(doc, force_reload = False)
    REVIT_LIFE_SAFETY.secure_dump_view(doc)
    t.Commit()
    
    t = DB.Transaction(doc, "Life Safety Update")
    t.Start()
    try:
        REVIT_LIFE_SAFETY.update_life_safety(doc, data_source)
        REVIT_LIFE_SAFETY.purge_tags_on_non_egress_door(doc, 
                                                        tag_family_name="LS Door Data", 
                                                        tag_family_type_name="SD")
    except Exception as e:
        print (traceback.format_exc())
        t.RollBack()
        return
    t.Commit()

    options = ["yes", "no"]
    res = REVIT_FORMS.dialogue("Display Egress Targets", main_text = "Do you want to display egress targets?", sub_text = "this can help you check if all room are getting correct target.", options = options)
    if res == options[0]:
        # views = REVIT_VIEW.ViewFilter().filter_archi_views().to_views()
        views = forms.select_views()
        if not views:
            return
        REVIT_LIFE_SAFETY.display_room_targets(doc, views)


################## main code below #####################
if __name__ == "__main__":
    update_life_safety(DOC)







