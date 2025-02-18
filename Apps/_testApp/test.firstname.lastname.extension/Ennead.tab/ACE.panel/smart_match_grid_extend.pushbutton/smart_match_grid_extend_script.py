#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ =  """Get all floor plans and area plans
for each view, find all grids. Then for each end of 
the grid decide if it should show bubble or not based 
on the status of same bubble from same level in REF dict."""
    
__title__ = "Smart Match\nGrid Extend"
__tip__ = True
import proDUCKtion # pyright: ignore 
from pyrevit import script # pyright: ignore 
proDUCKtion.validify()

import os
import time

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, DATA_FILE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW, REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()







def set_base_leaders(ref_view_grid_mapping):
    leader_record = {}
    for view in [REVIT_VIEW.get_view_by_name(x) for x in ref_view_grid_mapping.values()]:
        all_grids = DB.FilteredElementCollector(DOC, view.Id).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()

        for grid in all_grids:
            for grid_end in [DB.DatumEnds.End0, DB.DatumEnds.End1]:

                try:
                    key = "{}_{}".format(grid.Id.IntegerValue, grid_end)
                    if key in leader_record:
                        # reuse existing leader setting.
                        current_leader = grid.GetLeader (grid_end, view)
                        if not current_leader:
                            grid.AddLeader (grid_end, view)
                        if grid.IsLeaderValid  (grid_end, view, leader_record[key]):
                            grid.SetLeader (grid_end, view, leader_record[key] )
                        else:
                            print ("Leader not valid: {}, {}, {}".format(output.linkify(view.Id, title=view.Name), grid.Name, grid_end))
                    else:
                        #first time encountering, no need to change graphic, just record leader
                        leader = grid.GetLeader (grid_end, view)
                        if leader:
                            leader_record[key] = leader
                except:
                    print ("Give up: {}, {}, {}".format(output.linkify(view.Id, title=view.Name), grid.Name, grid_end))
                    
    return True


    
@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def smart_match_grid_extend():

    script_folder = os.path.dirname(__file__)
    for file in os.listdir(script_folder):
        if not file.endswith(".sexyDuck"):
            continue
        if DOC.Title.lower() in file.lower():
            break
    else:
        NOTIFICATION.messenger("Cannot find any reference data for project [{}]".format(DOC.Title))
        return
    
    ref_view_grid_mapping = DATA_FILE.get_data(os.path.join(script_folder, file))


    
    t = DB.Transaction(DOC, __title__)
    t.Start()
    

    ops = ["Yes", "No"]
    res = REVIT_FORMS.dialogue(main_text="Do you want to set base leader first for the ref views?")
    if res == ops[0]:
        set_base_leaders(ref_view_grid_mapping)
        t.Commit()
        return

    
    all_plans = DB.FilteredElementCollector(DOC).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    all_plans = [x for x in all_plans if x.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.AreaPlan]]
    all_plans = [x for x in all_plans if x.Name not in ref_view_grid_mapping.values()]
    all_plans = [x for x in all_plans if not x.IsTemplate ]
    all_plans.sort(key = lambda x: x.Name)

    all_levels = DB.FilteredElementCollector(DOC).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()
    all_level_names = [x.Name for x in all_levels]

    ref_views_resolved = {k: REVIT_VIEW.get_view_by_name(v) for k, v in ref_view_grid_mapping.items()}
    for k,v in sorted(ref_views_resolved.items()):
        if k not in all_level_names:
            output.print_md(":question_mark: Cannot find this level: {}".format(k))
        if v is None:
            output.print_md(":question_mark: Cannot find this refernce view: {}".format(v.Name))

    for view in all_plans:
        start_time = time.time()
        all_grids = DB.FilteredElementCollector(DOC, view.Id).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()
        if not all_grids:
            continue

        level_name = view.GenLevel.Name
        if level_name not in ref_view_grid_mapping:
            
            continue
        
        ref_view = ref_views_resolved[level_name]
        if ref_view is None:
            continue
        print ("\nWorking on {}".format(output.linkify(view.Id, title=view.Name)))
        for grid in all_grids:
            for grid_end in [DB.DatumEnds.End0, DB.DatumEnds.End1]:
                try:
                    is_show_bubble = grid.IsBubbleVisibleInView(grid_end, ref_view)
                    if is_show_bubble:
                        grid.ShowBubbleInView(grid_end, view)
                    else:
                        grid.HideBubbleInView(grid_end, view)


                    extent_type = grid.GetDatumExtentTypeInView  (grid_end, ref_view)
                    curves = grid.GetCurvesInView (extent_type, ref_view)
                    grid.SetDatumExtentType (grid_end, view, extent_type)
                    grid.SetCurveInView (extent_type, view, curves[0])

                    
                    leader = grid.GetLeader (grid_end, ref_view)
                    if leader and grid.IsLeaderValid  (grid_end, view, leader):
                        current_leader = grid.GetLeader (grid_end, view)
                        if not current_leader:
                            grid.AddLeader (grid_end, view)
                        grid.SetLeader (grid_end, view, leader )
                    
                        
                except Exception as e:
                    print ("Skip <{}> in <{}> becasue {}".format(grid.Name, output.linkify(view.Id, title=view.Name), e))

        end_time = time.time()
        print ("Done in {} seconds".format(end_time - start_time))
                

    t.Commit()
    print ("\n\n\n\n\n\nFinished")
    NOTIFICATION.messenger("Done!")



################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    smart_match_grid_extend()







