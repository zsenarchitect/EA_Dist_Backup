#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Excel2Diagram"

# from pyrevit import forms #
from calendar import c
import re
from weakref import ref
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, EXCEL, FOLDER, NOTIFICATION, TIME
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_VIEW, REVIT_SELECTION
from Autodesk.Revit import DB 
# from Autodesk.Revit import UI
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()



EXCEL_FILE = "J:\\1643\\2_Master File\\B-70_Programming\\01_Program & Analysis\\EA 2024-03-21 EA Program Responsibilities.xlsx"
FAMILY_NAME = "AreaShader"
WORKING_VIEW = "SK-G09_10_Program Shading"


# just the key is important now... the value is ingored
CONTAINER_FACTOR_MAP = {
    "10.0":3,
    "10.1":1.8,
    "11.0":2,
    "13.0":1.8,
    "14.0":1.8,
    "15.0":2,
    "15.1":1.5,
    "15.3":1.5,
    "15.4":1.5,
    "16.0":1.4,
    "16.1":1.2
    }


@ERROR_HANDLE.try_catch_error
def excel_to_diagram():
    REVIT_VIEW.set_active_view_by_name(WORKING_VIEW)
    solid_id = REVIT_SELECTION.get_solid_fill_pattern_id(doc)

    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    temp = FOLDER.copy_file_to_local_dump_folder(EXCEL_FILE, "temp.xls")
    data = EXCEL.read_data_from_excel(temp, worksheet="LHH_Public Program")

    data = data[6:] # remove header roows
    color = -1,-1,-1

    for line in data:

        
        line = line[6:] # remove bad columns from left
        
        if line[0] == line[1] == line[2] == "":
            #empty line
            continue

        
        print ("\n\n")
        print (line)

        if line[0] != "":
            ref_num = line[0]
            title = line[1]
        else:
            ref_num = line[1]
            title = line[2]

        # ignote this line, just make sense in excel, not related to diagram
        if  "TOTAL PUBLIC, ADMIN., BLDG. SUPPORT" in str(ref_num):
            continue
        if "NEED AMBULANCE/EMERGENCY DEPARTMENT CATEGORY" in str(ref_num):
            continue
            
        #round to 2 digit
        if isinstance(ref_num, float):
            ref_num = round(float(ref_num), 3)
            ref_num = str(ref_num)


        count = line[3] if line[3] != "" else 1
        unit_area = line[4] if line[4] != "" else -1

  
        for index in [6, 8, 10]:
            program_area_DGSF = line[index]
            try:
                program_area_DGSF = float(program_area_DGSF)
                if program_area_DGSF == 0:
                    continue
                if index == 10:
                    is_remote = True
                else:
                    is_remote = False
                break
            except:
                pass
        try:
            program_area_NSF = float(line[5])
        except:
            program_area_NSF = 0

            

        note = str(line[7])

        if line[14] != "":
            color = line[14].split("-")
            color = [int(x) for x in color]
        
        
        if title == "Mother/Baby Dedicated Discharge":
            ref_num = "11.10"

        print ("ref num = " + ref_num)
        print ("title = " + title)
        print ("count = " + str(count))
        print ("unit area = " + str(unit_area))
        print ("DGSF program area = " + str(program_area_DGSF))
        print ("NSF program area = " + str(program_area_NSF))
        print ("note = " + note)
        print ("color = " + str(color))

        
        graphic_override = DB.OverrideGraphicSettings ()
        graphic_override.SetSurfaceForegroundPatternColor (DB.Color(*color))
        graphic_override.SetSurfaceForegroundPatternId  (solid_id)

        
        if ref_num not in CONTAINER_FACTOR_MAP:
            # all the smallest bubble
            process_line(ref_num, title, count, unit_area, program_area_NSF or program_area_DGSF, note, graphic_override, is_remote)
        else:
            if ref_num.endswith("0"):
                # all the top level container
                process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)
            else:
                # all the middle level container, it need to show twice

                # show as inside top level containner
                process_line(ref_num, title, count, unit_area, program_area_NSF or program_area_DGSF, note, graphic_override, is_remote)


                # show as in containing all the smaller
                title += "_SmallContainer"
                process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)



    t.Commit()
    NOTIFICATION.messenger("Bubble diagram data updated from Excel")


def process_line(ref_num, title, count, unit_area, program_area, note, graphic_override, is_remote):
    is_ok = False

    try:
        program_area = float(program_area)
        if program_area != 0:
            is_ok = True
    except:
        pass

    if not is_ok:
        NOTIFICATION.messenger("Invalid program area for " + ref_num + " " + title)
        program_area = 99999
        note = "!!!!!!!!INVALID AREA: " + note


    # try find instance with ref_num, if not exist, create one
    type_name = "{}_{}".format(ref_num, title)

    family_type = REVIT_FAMILY.get_family_type_by_name(FAMILY_NAME, type_name, create_if_not_exist=True)

    instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(FAMILY_NAME, type_name)
    if len(instances) == 0:
        instance = doc.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), family_type, doc.ActiveView)
        if program_area > 0:
            instance.LookupParameter("W").Set(program_area**0.5)
    elif len(instances) == 1:
        instance = instances[0]
        
    elif len(instances) > 1:
        NOTIFICATION.messenger("More than one instance of type {} found, badddddddd!".format(type_name))


    if note.startswith("CANCEL:"):
        family_type.LookupParameter("is_cancel").Set(1)
    else:
        family_type.LookupParameter("is_cancel").Set(0)

    

    # print (family_type)
    # update the data to instance
    family_type.LookupParameter("Count").Set(count)
    family_type.LookupParameter("UnitArea").Set(unit_area)

    if program_area <= 0:
        program_area = 99
        note = "NO VALID AREA: " + note
        
    family_type.LookupParameter("ProgramArea").Set(program_area)
    family_type.LookupParameter("Note").Set(note)
    family_type.LookupParameter("RefNum").Set(ref_num)

    if "_SmallContainer" in title:
        title = title.replace("_SmallContainer", "")
    family_type.LookupParameter("Title").Set(title)

    if is_remote:
        family_type.LookupParameter("is_remote").Set(1)
        family_type.LookupParameter("RemoteNote").Set("(REMOTE)")
    else:
        family_type.LookupParameter("is_remote").Set(0)
        family_type.LookupParameter("RemoteNote").Set("")


    # do not scale up becasue now using seperate container and it is eaiser to find a balanced number manuall and keep using that
    # container_factor = CONTAINER_FACTOR_MAP.get(ref_num, 1)
    # family_type.LookupParameter("container_factor").Set(container_factor)

    
    doc.ActiveView.SetElementOverrides (instance.Id, graphic_override)


    instance.LookupParameter("Comments").Set("Updated {}".format(TIME.get_formatted_current_time()))





################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    excel_to_diagram()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







