__doc__ = "xxxxxxxxx"
__title__ = "Clear Shaft Solid"


from pyrevit import DB, revit, forms

def clear_existing_solid_shaft():

    all_generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    success_count = 0
    solid_count = 0
    fail_count = 0
    for item in all_generic_models:
        if item.LookupParameter("Comments").AsString() == global_comment:
            solid_count += 1
            try:
                ####if pinned then unpin

                
                revit.doc.Delete(item.Id)



                success_count += 1
            except:
                fail_count += 1

    if solid_count == 0:
        display_text = "No shaft-solid found."


    else:
        if success_count == solid_count:
            display_text = "All {} visualied shaft solid have been removed from the project".format(success_count)
        else:
            display_text = "{} visualised shaft solid are removed.\n{} visualied shaft solid cannot be removed.".format(success_count,fail_count)

    forms.alert(display_text)


########## main code below ##########


with revit.Transaction("Clear Visualized Shaft Solid"):
    #clear cur3ent visulised shaft with comment "$$EnneadTab_VisualisedShaft Tool"
    global_comment = "$$EnneadTab_VisualisedShaft Tool"
    clear_existing_solid_shaft()
