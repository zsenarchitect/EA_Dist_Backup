__doc__ = "[room speration line, area boundary line]\nturn them off across the project"
__title__ = "Kill\nPink Lines"





from pyrevit import DB, revit, forms, script

found = False
for category in revit.doc.Settings.Categories:
    if category.Name == "Curtain Panels":
        break
for sub_c in category.SubCategories:
    if sub_c.Name == "ID":
        found = True
        break
ID_category = sub_c

def kill_category(view):
    """
    print(view.Name,view.Id,view.CanEnableTemporaryViewPropertiesMode(),view.CanCategoryBeHiddenTemporary(DB.ElementId(DB.BuiltInCategory.OST_RoomReference)))
    print(DB.ElementId(DB.BuiltInCategory.OST_RoomReference))
    print(DB.ElementId(DB.BuiltInCategory.OST_RoomReferenceVisibility))
    print(DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines))
    """


    if kill_rm_sp_line:
        view.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_RoomSeparationLines), True)
    if kill_rm_ref:
        view.SetCategoryHidden (DB.ElementId(DB.BuiltInCategory.OST_RoomReferenceVisibility), True)
    if kill_area_bd_line:
        view.SetCategoryHidden (DB.ElementId(DB.BuiltInCategory.OST_AreaSchemeLines), True)
    if kill_area_ref:
        view.SetCategoryHidden (DB.ElementId(DB.BuiltInCategory.OST_AreaReferenceVisibility), True)

    if kill_mass:
        view.SetCategoryHidden (DB.ElementId(DB.BuiltInCategory.OST_Massing), True)

    if kill_ID:
        view.SetCategoryHidden (DB.ElementId(ID_category.Id), True)



######### main code below ########

#print DB.BuiltInCategory.OST_RoomSeparationLines
#options = [DB.BuiltInCategory.OST_RoomSeparationLines,]



sel_sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()



kill_ID = False
kill_rm_sp_line = False
kill_rm_ref = False
kill_area_bd_line = False
kill_area_ref = False
kill_mass = False
options = ["Room Speration Line", "Room Reference","Area Boundary Line","Area Reference","Mass"]
if found:
    options.append("ID")
sel_category = forms.SelectFromList.show(options , title='Select category you want to KILL from sheets', multiselect = True)
if "Room Speration Line" in sel_category:
    kill_rm_sp_line = True
if "Room Reference" in sel_category:
    kill_rm_ref = True
if "Area Boundary Line" in sel_category:
    kill_area_bd_line = True
if "Area Reference" in sel_category:
    kill_area_ref = True
if "Mass" in sel_category:
    kill_mass = True
if "ID" in sel_category:
    kill_ID = True


with revit.TransactionGroup("Kill Category"):
    original_view = revit.doc.ActiveView
    for sheet in sel_sheets:
        for view_id in sheet.GetAllPlacedViews():

            view = revit.doc.GetElement(view_id)
            print(view.ViewType)
            if str(view.ViewType) in ["FloorPlan","CeilingPlan","Elevation","ThreeD","AreaPlan","Section","Detail"]:
                print("GO")
            else:
                print("No Go")
                continue

            view_template = revit.doc.GetElement(view.ViewTemplateId)
            print("\t\t view template = {}".format(view_template))
            """
            if str(view.ViewType) in ["DraftingView","ThreeD"]:
                continue
            """

            try:
                kill_category(view_template)
            except:
                kill_category(view)
            #except Exception as e:
                #print (e)
    #revit.uidoc.ActiveView = original_view
