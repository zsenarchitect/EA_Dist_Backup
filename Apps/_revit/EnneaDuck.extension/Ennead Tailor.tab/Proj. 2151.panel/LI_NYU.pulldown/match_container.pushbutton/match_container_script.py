#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """
Use container file as base to compare BIM data to other major NYULI docs for consistency.

I am checking system family
Then loadable family
"""
__title__ = "Match Container"
__context__ = "zero-doc"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from pyrevit import script

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, OUTPUT, TIME, USER
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()
from collections import OrderedDict


EMOJI_DICT = OrderedDict()

dict_definitions = [
    ("Exist",":ballot_box_with_check:"),
    ("NotExist",":question_mark:"),
    ("NoMatchType",":question_mark:"),
    ("NoMatchTemplate",":question_mark:"),
    ("NoMatchPara",":double_exclamation_mark:"),
    ("NoMatchCategory",":double_exclamation_mark:"),
    ("NoMatchWorkset",":question_mark:"),
    ("NoSame",":face_with_raised_eyebrow:"),
    ("Same",":thumbs_up:")
]
for pair in dict_definitions:
    key, value = pair
    EMOJI_DICT[key] = value

IS_TESING_NEW_FUNC =  USER.IS_DEVELOPER


import file_getter as FG
# import system_family_checker as SFC
import family_checker as FC
import template_checker as TC



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def match_container():

    container_file_title = "EAEC_NYU-Langone Health_Container File"
    if REVIT_APPLICATION.get_doc() and REVIT_APPLICATION.get_doc().Title == container_file_title:
        NOTIFICATION.messenger("Your active doc is the container file. Nothing to compare.")
        return None
    container_doc = FG.get_NYU_doc(doc_title = container_file_title)
    if not container_doc:
        return

    output.print_md("## Objective:")
    print (__doc__)
    
    output.print_md("## Icon Legend:")
    for key in EMOJI_DICT.keys():
        emoji = EMOJI_DICT[key]
        output.print_md("{}: {}".format(key, emoji))
        
    output.print_md("## Report Date:{}".format(TIME.get_formatted_current_time()))

    print ("\n\n")


        
    NYULI_list = [
        "2151_A_EA_NYULI_Hospital_EXT",
        "2151_A_EAEC_NYULI_Hospital_INT",
        "2151_A_EA_NYULI_Site",
        "2151_A_EA_NYULI_Parking East",
        "2151_A_EA_NYULI_Parking West",
        "2151_A_EA_NYULI_CUP_EXT"
    ]


    if IS_TESING_NEW_FUNC:
        NYULI_list = NYULI_list[3:]
    working_docs = [FG.get_NYU_doc(doc_title = x) for x in NYULI_list]
    working_docs = [x for x in working_docs if x is not None]


    # if IS_TESING_NEW_FUNC:
    #     TC.process_template(container_doc, working_docs)
    #     NOTIFICATION.messenger("AAAAAAAAAAA Done!")
    #     OUTPUT.display_output_on_browser()
        


    
    sys_cates_with_compound = [
        "Walls",
        "Floors",
        "Roofs",
        "Ceilings"
    ]
    for sys_cate in sys_cates_with_compound:
        FC.process_family(sys_cate, 
                          container_doc, 
                          working_docs, 
                          has_compound = True, 
                          is_loadable=False)

    sys_cates_without_compound = [
        "Ramps",
        "Stairs",
        "Railings",
        "StairsRuns",
        "StairsRailing",
        "Dimensions",
        "Levels",
        "Grids",
        "Sections",
        "GridHeads",
        "LevelHeads",
        "TextNotes"
    ]
    for sys_cate in sys_cates_without_compound:
        FC.process_family(sys_cate, 
                          container_doc, 
                          working_docs, 
                          has_compound = False, 
                          is_loadable=False)


    family_cates = [
        "Doors",
        "Windows",
        "Columns",
        "StructuralColumns",
        "Parking",
        "Fixtures",
        "DetailComponents",
        "GenericAnnotation",
        "Furniture",
        "GenericModel",
        "CurtainWallPanels",
        "TitleBlocks",
        "AreaTags",
        "RoomTags",
        "DoorTags",
        "WindowTags",
        'KeynoteTags',
        "MaterialTags",
        "StairsTags",
        "ParkingTags",
        "WallTags",
        "FurnitureTags",
        "CaseworkTags"
    ]
    for family_cate in family_cates:
        FC.process_family(family_cate, 
                          container_doc, 
                          working_docs, 
                          has_compound = False, 
                          is_loadable=True)

    TC.process_template(container_doc, working_docs)


    OUTPUT.display_output_on_browser()

    NOTIFICATION.messenger("Comparision Done!")




################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    match_container()







