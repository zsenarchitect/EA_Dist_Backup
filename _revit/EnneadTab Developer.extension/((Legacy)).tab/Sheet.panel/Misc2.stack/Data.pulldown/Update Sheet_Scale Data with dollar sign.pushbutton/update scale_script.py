__doc__ = "Find a valid view scale on viewports in sheet, and apply it to the \
hosting sheet to 'Sheet_$Scale' parameter. This scale parameter is a EA standard\
if the file was created from EA template."
__title__ = "update $scale on sheet"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

with revit.Transaction("update scale number"):
    for sheet in sheets:
        temp_scale = sheet.LookupParameter("Scale").AsString()

        if temp_scale == "As indicated":
            found_scale = False
            #print "xxx"
            for view_id in sheet.GetAllPlacedViews():
                view = revit.doc.GetElement(view_id)
                #print view.ViewType
                if str(view.ViewType) in ["FloorPlan","CeilingPlan","Elevation", "ThreeD", "DraftingView", "AreaPlan", "Section", "Detail"]:
                    temp_scale = "1 : {}".format(view.Scale)
                    found_scale = True
                    #print "ok"
                    break
                    #print "xxxxxxxx"
                    #print temp_scale
            if not found_scale:
                temp_scale = "N/A"
                #print "bad"
        #print "xx"
        #print temp_scale
        if len(str(temp_scale)) == 0:
            temp_scale = "N/A"
        sheet.LookupParameter("Sheet_$Scale").Set(temp_scale)
        if len(sheet.LookupParameter("Sheet_$Scale").AsString()) == 0:
            sheet.LookupParameter("Sheet_$Scale").Set("N/A")
