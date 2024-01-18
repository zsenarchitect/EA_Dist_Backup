__doc__ = "get all detail number a prefix so you can safely renumber them"
__title__ = "Temp\nDetail Number"

from pyrevit import forms, DB, revit, script, output


################## main code below #####################






def change_detail_num(sel_sheets):

    for sheet in sel_sheets:
        #for view on current sheet
        for view_id in sheet.GetAllViewports():
            view = revit.doc.GetElement(view_id)# this view is actually viewport class, not view class
            if revit.doc.GetElement(view.ViewId).ViewType.ToString() == "Legend":
                continue

            refill_title = False
            detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            detail_num = "temp_" + view.Parameter[detail_num_para_id].AsString() #get view detail num
            #print detail_num
            try:
                view.Parameter[detail_num_para_id].Set(detail_num)
            except:
                print "Skip {}".format(view.Name)

################# main code below #############
if __name__== "__main__":
    sel_sheets = forms.select_sheets(title='Select Sheets That to up the detail number.')
    with revit.Transaction("Rename detail number"):
        change_detail_num(sel_sheets)
