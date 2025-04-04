#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Facade Glass vs Opaque Study for Cost estimation"
__title__ = "Window Wall Ratio Sum"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, TIME
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def self_update_region_area(piece_type):
    if piece_type.LookupParameter("_GlassTargetIds").HasValue:
        ids =  piece_type.LookupParameter("_GlassTargetIds").AsString().split(";")
        elements = [DOC.GetElement(id) for id in ids]
        area = 0
        for element in elements:
            if element is None:
                continue
            area += element.LookupParameter("Area").AsDouble()
        if area > 0:    
            print ("Based on the glass targets, the region area is {}".format(area))
            piece_type.LookupParameter("Glass Area").Set(area)

    if piece_type.LookupParameter("_OpaqueTargetIds").HasValue:
        ids =  piece_type.LookupParameter("_OpaqueTargetIds").AsString().split(";")
        elements = [DOC.GetElement(id) for id in ids]
        area = 0
        for element in elements:
            if element is None:
                continue
            area += element.LookupParameter("Area").AsDouble()  
        if area > 0:
            print ("Based on the opaque targets, the region area is {}".format(area))
            piece_type.LookupParameter("Opaque Area").Set(area)

FMILY_NAME = "Area Percentages_Annotation Symbol"
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def window_wall_ratio_sum(doc):

    t = DB.Transaction(doc, __title__)
    t.Start()


    
    # get all types of the family
    all_types = REVIT_FAMILY.get_all_types_by_family_name(FMILY_NAME)

    for type in all_types:
        self_update_region_area(type)



    order = 0
    keywords = ["North", "South", "East", "West"]
    grand_glass_area_total = 0
    grand_opaque_area_total = 0

    # for each orientation, sum the Glass Area and Opaque area, fill for type Orientation_Total
    # for north south east west orientation get all types containing those keywords
    for keyword in keywords:
        order += 1
        print ("\n\nWorking for keyword: {}".format(keyword))
        piece_types = [type for type in all_types if keyword in type.LookupParameter("Facade Side").AsString() and "Total" not in type.LookupParameter("Facade Orientation").AsString()]
        glass_area_sum = 0
        opaque_area_sum = 0
        for i, piece_type in enumerate(piece_types):
            print ("{}/{} Getting type {}".format(i+1, len(piece_types), piece_type.LookupParameter("Facade Orientation").AsString()))
           
            # get the glass area of the piece type
            glass_area = piece_type.LookupParameter("Glass Area").AsDouble()
            print ("Glass area: {}".format(glass_area))
            glass_area_sum += glass_area
            # get the opaque area of the piece type
            opaque_area = piece_type.LookupParameter("Opaque Area").AsDouble()
            print ("Opaque area: {}".format(opaque_area))
            opaque_area_sum += opaque_area

            piece_type.LookupParameter("_order").Set("{}_{}".format(order, keyword))
            

        summery_type = [type for type in all_types if keyword in type.LookupParameter("Facade Side").AsString() and "Total" in type.LookupParameter("Facade Orientation").AsString()][0]
        summery_type.LookupParameter("Glass Area").Set(glass_area_sum)
        summery_type.LookupParameter("Opaque Area").Set(opaque_area_sum)
        summery_type.LookupParameter("_order").Set("{}_{}".format(order, keyword))

        grand_glass_area_total += glass_area_sum
        grand_opaque_area_total += opaque_area_sum

    order += 1
    print ("\n\nGrand total:")
    print ("Glass area: {}".format(grand_glass_area_total))
    print ("Opaque area: {}".format(grand_opaque_area_total))
    grand_summery_type = REVIT_FAMILY.get_family_type_by_name(FMILY_NAME, "Grand Total")
    grand_summery_type.LookupParameter("Glass Area").Set(grand_glass_area_total)
    grand_summery_type.LookupParameter("Opaque Area").Set(grand_opaque_area_total)
    grand_summery_type.LookupParameter("_order").Set("{}_{}".format(order, "Grand Total"))




    schedule = REVIT_VIEW.get_view_by_name("Glass vs Opaque Facade Percentages")
    if schedule:
        schedule.LookupParameter("Last_Update_Date").Set(TIME.get_formatted_current_time())

    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    window_wall_ratio_sum(DOC)







