__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Flip Sytem Panel"

from pyrevit import DB, revit,forms,script


selection = revit.get_selection()

walltype_id = DB.FilteredElementCollector(revit.doc)\
  .OfClass(DB.WallType)\
  .WhereElementIsElementType()\
  .FirstElementId()


with revit.Transaction("FlipSyetmPanel"):
    panels = []
    for el in selection:
        #print el.Category.Name
        if el.Category.Name == "Curtain Panels":
            panels.append(el)
            #el.rotate()
            #flipHand()
            #flipFacing()
            print(el.Mirrored)
            print(el)
            original_type_id = el.PanelType.Id
            temp_wall_id = el.ChangeTypeId(walltype_id)#-----change it to wall type [0], then flip face, then change it back to original type id
            print(temp_wall_id)
            #temp_wall = revit.UI.Selection.SetElementIds(temp_wall_id)
            temp_wall = revit.doc.GetElement(temp_wall_id)
            print(temp_wall)
            #el.flipFacing()
            #el.flipHand()
            temp_wall.Flip()
            #el.rotate()
            #temp_wall.ChangeTypeId(original_type_id)
            print(el.Mirrored)
            #el.Mirrored = not el.Mirrored

print(panels)
