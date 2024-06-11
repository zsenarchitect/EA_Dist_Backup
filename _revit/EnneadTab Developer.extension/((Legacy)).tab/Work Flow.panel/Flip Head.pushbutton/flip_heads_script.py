#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

__doc__ = "With pre-filtered selection, flips the heads of selected signle segment grids or levels. Multi-Segment Grids will be ignored per API limitation.\nIf it doesn't update immediately, it usually will be ok next time you open the project. If it still does not update, report a bug."
__title__ = "Flip Heads\nGrids/Levels"



def flip_heads(elements):

    for el in elements:


        end0 = el.IsBubbleVisibleInView(DB.DatumEnds.End0,revit.active_view)
        end1 = el.IsBubbleVisibleInView(DB.DatumEnds.End1,revit.active_view)
        #print "xxx"
        #print end0,end1
        #print "xxxx"
        if end0 == end1:
            #print "#1"
            continue

        elif end0 and not(end1):
            #print "#2"
            el.ShowBubbleInView(DB.DatumEnds.End1,revit.active_view)
            el.HideBubbleInView(DB.DatumEnds.End0,revit.active_view)

        elif not(end0) and end1:
            #print "#3"
            el.ShowBubbleInView(DB.DatumEnds.End0,revit.active_view)
            el.HideBubbleInView(DB.DatumEnds.End1,revit.active_view)

        else:
            print("something wrong")
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
with revit.Transaction("Flip Heads"):
    flip_heads(grids_and_levels)
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 33, tool_used = "Flip Heads", show_toast = True)

revit.doc.Regenerate()

if m_grid:
    forms.alert("{} Multi-Segement Grid detected, currently Revit API does not support bubble function for this type of grids. Please manually swicth bubbles.".format(len(m_grid)))
