



#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__doc__ = "xxxx"
__title__ = "Turn off Heads\nGrids/Levels"



def turn_off_head(elements):

    for el in elements:



        el.HideBubbleInView(DB.DatumEnds.End1,revit.active_view)
        el.HideBubbleInView(DB.DatumEnds.End0,revit.active_view)


    return





#####################main code below###############
selection = revit.get_selection()

grids_and_levels = []
m_grid = []#multi-segement grid
#check if it is grid or levels,
for item in selection:
    #print item.Category.Name

    if item.Category.Name in ["Grids", "Levels"]:
        grids_and_levels.append(item)
    if item.Category.Name == "Multi-segmented Grid":
        m_grid.append(item)

#print grids_and_levels


#debug
'''
for p in item.Parameters:
    print(p.Definition.Name)

subs = item.GetGridIds
subs = item.GetGridIds.Astring()
print(subs)
for sub in subs:
    print(sub)
#print item.Parameter[DB.BuiltInParameter.GRID_BUBBLE_END_1].ToString()
#print item.Parameter[DB.BuiltInParameter.GRID_BUBBLE_END_2].ToString()
'''


#start transaction
with revit.Transaction("Turn off Heads"):
    turn_off_head(grids_and_levels)

if m_grid:
    forms.alert("{} Multi-Segement Grid detected, currently Revit API does not support bubble function for this type of grids. Please manually swicth bubbles.".format(len(m_grid)))
