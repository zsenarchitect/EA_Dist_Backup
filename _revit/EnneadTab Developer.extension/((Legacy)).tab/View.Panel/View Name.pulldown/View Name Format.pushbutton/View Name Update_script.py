from pyrevit import revit, DB
from pyrevit import forms, script
import EA_UTILITY
import EnneadTab

__title__ = 'View Name\nRe-Format'
__doc__ = 'Update the views names to one of format below: \n\n -  Detail Num + Sheet Num + Title on Sheet\n -  Sheet Num + Detail Num + Title on Sheet\n\nWill not change how the sheet appears but makes the project browser more organized.'


ATTEMPT = 0

def change_name(sel_sheets):
    global ATTEMPT
    if ATTEMPT > 3:
        return

    failed_sheets = set()
    all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    def is_user_view(view):
        if view.IsTemplate:
            return False
        if view.ViewType.ToString() in ["Legend", "Schedule"]:
            return False
        return True
    all_views = filter(lambda x: is_user_view(x), all_views)

    view_names_pool = [x.Name for x in all_views]

    for sheet in sel_sheets:
        sheet_num = sheet.SheetNumber

        #for view on current sheet
        for view_id in sheet.GetAllViewports():
            view = revit.doc.GetElement(view_id)# this view is actually viewport class, not view class

            current_owner = view.LookupParameter("Edited by").AsString()
            if current_owner != "" and current_owner != EA_UTILITY.get_application().Username:
                print("###################skip view owned by {}. View Name = {}".format(current_owner, view.Name))
                continue

            if EA_UTILITY.is_owned(view):
                print("skip view owned by other")
                continue




            if revit.doc.GetElement(view.ViewId).ViewType.ToString() == "Legend":
                continue

            #print revit.doc.GetElement(view.ViewId).Name
            if "{3D" in revit.doc.GetElement(view.ViewId).Name:
                continue


            refill_title = False
            detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            detail_num = view.Parameter[detail_num_para_id].AsString() #get view detail num

            title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
            title = view.Parameter[title_para_id].AsString() #get view title

            name_para_id = DB.BuiltInParameter.VIEW_NAME
            original_name = view.Parameter[name_para_id].AsString() #get view name,if none, then use view name
            if not(title):
                title = original_name
                refill_title = True

            if sheetnumfirst:
                new_view_name = str(sheet_num) + "_" + str(detail_num) + "_" + str(title)
            else:
                new_view_name = str(detail_num) + "_" + str(sheet_num) + "_" + str(title)
            #forms.alert(str(new_view_name))

            actual_view = revit.doc.GetElement(view.ViewId)
            if new_view_name == actual_view.Name:
                #print "Skip {}".format(new_view_name)
                continue

            if new_view_name in view_names_pool:
                #print new_view_name
                failed_sheets.add(sheet)

                print("Will try to visit <{}> again to avoid using same name.".format(actual_view.Name))
                view.Parameter[name_para_id].Set(new_view_name + "_Pending")
                #print view
                continue
            try:
                if refill_title:
                    view.Parameter[title_para_id].Set(original_name)
                view.Parameter[name_para_id].Set(new_view_name)
            except:
                print ("Skip {}".format(view.Name))


    # this is new
    if len(list(failed_sheets)) > 0:
        global ATTEMPT
        ATTEMPT += 1
        print("\n\nAttemp = {}".format(ATTEMPT))
        change_name(list(failed_sheets))
################# main code below #############
output = script.get_output()
output.close_others()
sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to update names.')



with revit.Transaction("Rename views"):
    if sel_sheets:

        res = EA_UTILITY.dialogue(main_text = "I want to use [.....] format for the names", options = [["SheetNum_DetailNum_Title","(Recommended)"], "DetailNum_SheetNum_Title"])
        #print res
        # res = forms.alert(options = ["SheetNum_DetailNum_Title", "DetailNum_SheetNum_Title"], msg = "I want to use [.....] format for the names",sub_msg = "Recommending SheetNumber first.")

        if "SheetNum_DetailNum" in res:
            sheetnumfirst = True
        elif "DetailNum_SheetNum" in res:
            sheetnumfirst = False
        else:
            script.exit()
        change_name(sel_sheets)


        import ENNEAD_LOG
        ENNEAD_LOG.use_enneadtab(coin_change = 50, tool_used = "Format View Names", show_toast = True)

##########     need to seperate the leng view so its name doesnt change
