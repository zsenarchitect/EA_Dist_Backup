__doc__ = "Turn multiple viewports bounrary on or off for the selected sheets."
__title__ = "Show/Hide\nCrop Region"


from pyrevit import DB, script, revit, forms




def set_all_viewport_crop(option):
    sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to update view crop.')


    #all_viewports = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport).WhereElementIsNotElementType().ToElements()

    all_viewport_ids = []

    for sheet in sel_sheets:
        all_viewport_ids.extend(sheet.GetAllViewports())

    count = 0
    for viewport_id in all_viewport_ids:
        view_id = revit.doc.GetElement(viewport_id).ViewId
        if revit.doc.GetElement(view_id).CropBoxVisible != option:
            revit.doc.GetElement(view_id).CropBoxVisible = option
            count += 1

    forms.alert("{0} view(s) crop boundary is turned {1}.".format(count, "on" if option else "off"))

def main():
    res = forms.alert(options = ["hide", "show"], msg = "I want to [     ] all viewport crop in the following sheets.")
    if not res:
        return

        
    if "hide" in res:
        option = False
    elif "show" in res:
        option = True
    else:
        script.exit()



    with revit.Transaction("Set All Viewport Crop"):
        set_all_viewport_crop(option)


if __name__ == "__main__":
    main()
