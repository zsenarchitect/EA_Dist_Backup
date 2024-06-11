__doc__ = "compare the difference between several print set"
__title__ = "Compare\nPrint Set"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28506"

from pyrevit import revit, DB, forms, script
output = script.get_output()

def final_print_table(data):

    columns = [ "SheetNum or View Type", "Name"]

    for set in selected_print_set:
        columns.append(set.Name)
    #print columns

    output.print_table(table_data=data,title="Comparing Print Sets",columns=columns)


def compare_sheetsets(print_set_collections):
    all_views = []
    #get views in each sheet set
    for print_set in print_set_collections:
        all_views.extend(print_set.Views)

    unique_names = []
    unique_set = []
    for view in all_views:
        if view.Name not in unique_names:
            unique_names.append(view.Name)
            unique_set.append(view)


    #remoce duplicate and sort the name
    unique_set = list(set(unique_set))
    unique_set.sort(key = lambda x: x.SheetNumber if hasattr(x,"SheetNumber") else x.ViewType)

    #make data table item (sheet number if is sheet, name, yes, no, no )
    data = []
    for view in unique_set:
        #print view.Name
        #print view

        containment_status = []
        for print_set in print_set_collections:
            if print_set.Views.Contains(view):
                containment_status.append("Yes")

            else:
                containment_status.append("---No")
        #print containment_status

        try:
            data_item = [view.SheetNumber, view.Name]
        except:
            data_item = [view.ViewType, view.Name]
        data_item.extend(containment_status)
        data.append(data_item)





    #print table
    final_print_table(data)



############## main code below #############
if __name__== "__main__":
    #get all view sheetset
    all_view_sheet_sets = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSheetSet).ToElements()



    # let user pick multuple sheetsets
    selected_print_set = forms.SelectFromList.show(all_view_sheet_sets,
                                    multiselect=True,
                                    name_attr='Name',
                                    button_name='Select Print Sets',
                                    title = "select several print sets to comapre their content")
    if not selected_print_set:
        script.exit()



    # compare sheet sets
    compare_sheetsets(selected_print_set)
