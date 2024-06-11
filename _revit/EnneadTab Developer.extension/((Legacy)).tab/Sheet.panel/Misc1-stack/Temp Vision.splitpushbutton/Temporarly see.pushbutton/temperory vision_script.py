__doc__ = "[room speration line, area boundary line, room reference, area reference]\npick any of those to turnon at tempery view template across many sheet"
__title__ = "Temporary\nVision"



"""
ask for some category to pick, [room speration line, area boundary line, room reference, area reference]
turn on temperory view mode, every thing else half tone


"""

from pyrevit import DB, revit, forms, script




def turn_on_category(view):
    """
    print(view.Name,view.Id,view.CanEnableTemporaryViewPropertiesMode(),view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_RoomReference)))
    print(DB.ElementId(DB.BuiltInCategory.OST_RoomReference))
    print(DB.ElementId(DB.BuiltInCategory.OST_RoomReferenceVisibility))
    print(DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines))
    """


    view.EnableTemporaryViewPropertiesMode(view.Id)
    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_RoomSeparationLines)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_RoomSeparationLines), not(show_rm_sp_line))
    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_RoomReferenceVisibility)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_RoomReferenceVisibility), not(show_rm_ref))



    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines), not(show_area_bd_line))
    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_AreaReferenceVisibility)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_AreaReferenceVisibility), not(show_area_ref))
    #revit.doc.GetElement(DB.BuiltInCategory.OST_RoomSeparationLines).SetLineWeight(6,DB.GraphicSyleType.Projection)
    override_setting = DB.OverrideGraphicSettings().SetProjectionLineWeight(9)
    view.SetCategoryOverrides(DB.ElementId(DB.BuiltInCategory.OST_RoomSeparationLines),override_setting)
    view.SetCategoryOverrides(DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines),override_setting)

    """
    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_Massing)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_Massing), not(show_mass))
    """

    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_SectionBox)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_SectionBox), not(show_sectionbox))


    if view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_Levels)):
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_Levels), not(show_level))


######### main code below ########

#print DB.BuiltInCategory.OST_RoomSeparationLines
#options = [DB.BuiltInCategory.OST_RoomSeparationLines,]



sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')
if len(sel_sheets) == 0:
    forms.alert("Please pick at least one sheet")
    script.exit()



show_rm_sp_line = False
show_rm_ref = False
show_area_bd_line = False
show_area_ref = False
show_sectionbox = False
show_level = False
#show_mass = False
sel_category = forms.SelectFromList.show(["Room Speration Line", "Room Reference","Area Boundary Line","Area Reference", "Section Box", "Level"], title='Select category you want to turn on at temperory template.', multiselect = True)
if len(sel_category) == 0:
    forms.alert("Please pick at least one category")
    script.exit()
if "Room Speration Line" in sel_category:
    show_rm_sp_line = True
if "Room Reference" in sel_category:
    show_rm_ref = True
if "Area Boundary Line" in sel_category:
    show_area_bd_line = True
if "Area Reference" in sel_category:
    show_area_ref = True
if "Section Box" in sel_category:
    show_sectionbox = True
if "Level" in sel_category:
    show_level = True
"""
if "Mass" in sel_category:
    show_mass = True
"""

with revit.TransactionGroup("Tempory See Category"):
    original_view = revit.doc.ActiveView
    for sheet in sel_sheets:
        for view_id in sheet.GetAllPlacedViews():

            view = revit.doc.GetElement(view_id)
            """
            if str(view.ViewType) in ["DraftingView","ThreeD"]:
                print("Skipping '{}' becasue it is a {} viewtype.".format(view.Name, view.ViewType))
                continue
            """
            #revit.uidoc.ActiveView = view
            if view.CanEnableTemporaryViewPropertiesMode():
                with revit.Transaction("temp view mode"):
                    try:
                        turn_on_category(view)
                    except Exception as e:
                        print("~~~~~~skipping view")
                        print(view.ViewType, view.Name,e)
                        print("~~~~")
    revit.uidoc.ActiveView = original_view
