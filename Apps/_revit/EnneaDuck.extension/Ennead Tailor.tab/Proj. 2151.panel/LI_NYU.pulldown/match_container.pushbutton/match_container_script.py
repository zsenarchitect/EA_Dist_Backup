#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """
Use container file as base to compare BIM data to other major NYULI docs for consistency.
"""
__title__ = "Match Container"
__context__ = "zero-doc"

import time
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from pyrevit import script

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, OUTPUT, TIME, USER
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_EVENT
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

IS_TESING_NEW_FUNC =  False and USER.IS_DEVELOPER


import file_getter as FG
# import system_family_checker as SFC
import family_checker as FC
import template_checker as TC
from model_health_checker import ModelHealthChecker
from data_holder import SentenceDataHolder



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
    NOTIFICATION.messenger("This will take a while(10~60mins)")
    
    REVIT_EVENT.set_family_load_hook_stage(stage=False)
    processor_collection = []
    processor_collection.append(SentenceDataHolder("## Objective:"))
    processor_collection.append(SentenceDataHolder(__doc__))

    processor_collection.append(SentenceDataHolder("## Icon Legend:"))
    for key in EMOJI_DICT.keys():
        emoji = EMOJI_DICT[key]
        processor_collection.append(SentenceDataHolder("{}: {}".format(key, emoji)))
        
    processor_collection.append(SentenceDataHolder("## Report Date:{}".format(TIME.get_formatted_current_time())))
    start_time = time.time()

    processor_collection.append(SentenceDataHolder("\n\n"))
    


        
    NYULI_list = [
        "2151_A_EA_NYULI_Hospital_EXT",
        "2151_A_EAEC_NYULI_Hospital_INT",
        "2151_A_EA_NYULI_Site",
        "2151_A_EA_NYULI_Parking East",
        "2151_A_EA_NYULI_Parking West",
        "2151_A_EA_NYULI_CUP_EXT"
    ]


    if IS_TESING_NEW_FUNC:
        NYULI_list = NYULI_list[5:]
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
    if IS_TESING_NEW_FUNC:
        sys_cates_with_compound = []
    for sys_cate in sys_cates_with_compound:
        processor = FC.FamilyProcessor(sys_cate, 
                                        container_doc, 
                                        working_docs, 
                                        has_compound = True, 
                                        is_loadable=False)
        processor.process()
        processor_collection.append(processor)

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
    if IS_TESING_NEW_FUNC:
        sys_cates_without_compound = ["TextNotes"]
    for sys_cate in sys_cates_without_compound:
        processor = FC.FamilyProcessor(sys_cate, 
                                        container_doc, 
                                        working_docs, 
                                        has_compound = False, 
                                        is_loadable=False)
        processor.process()
        processor_collection.append(processor)


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
        "FurnitureSystems",
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
    if IS_TESING_NEW_FUNC:
        family_cates = ["TitleBlocks"]
    for family_cate in family_cates:
        processor = FC.FamilyProcessor(family_cate, 
                                        container_doc, 
                                        working_docs, 
                                        has_compound = False, 
                                        is_loadable=True)
        processor.process()
        processor_collection.append(processor)


    for processor in processor_collection:
        processor.print_data()

    if not IS_TESING_NEW_FUNC:
        TC.process_template(container_doc, working_docs)


    for doc in working_docs:
        ModelHealthChecker(doc).check()

    time_lapse = time.time() - start_time
    print ("Time Used To Run Checks: {}".format(TIME.get_readable_time(time_lapse)))

    OUTPUT.display_output_on_browser()

    for family_doc in REVIT_APPLICATION.get_all_family_docs():
        family_doc.Close(False)

    NOTIFICATION.messenger("Comparision Done!\nView your report in browser.")
    REVIT_EVENT.set_family_load_hook_stage(stage=True)




################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others(True)
    match_container()







