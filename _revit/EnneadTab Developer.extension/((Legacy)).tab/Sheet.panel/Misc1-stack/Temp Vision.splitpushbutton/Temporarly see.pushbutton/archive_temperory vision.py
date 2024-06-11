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







######### main code below ########



sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')


show_rm_sp_line = False
show_rm_ref = False
show_area_bd_line = False
show_area_ref = False
sel_category = forms.SelectFromList.show(["Room Speration Line", "Room Reference","Area Boundary Line","Area Reference"], title='Select category you want to turn on at temperory template.', multiselect = True)
if "Room Speration Line" in sel_category:
    show_rm_sp_line = True
if "Room Reference" in sel_category:
    show_rm_ref = True
if "Area Boundary Line" in sel_category:
    show_area_bd_line = True
if "Area Reference" in sel_category:
    show_area_ref = True



with revit.TransactionGroup("Tempory See Category"):
    original_view = revit.doc.ActiveView
    for sheet in sel_sheets:
        for view_id in sheet.GetAllPlacedViews():

            view = revit.doc.GetElement(view_id)

            if str(view.ViewType) in ["DraftingView","ThreeD"]:
                continue
            #revit.uidoc.ActiveView = view
            if view.CanEnableTemporaryViewPropertiesMode():
                with revit.Transaction("temp view mode"):
                    try:
                        turn_on_category(view)
                    except Exception as e:
                        print(view.ViewType, view.Name,e)
    revit.uidoc.ActiveView = original_view
