__doc__ = "In a table, show you which sheet is using which revision.\nThis tool will become useless after 2024 revision schedule"
__title__ = "List\nRevisions"

from pyrevit import forms, DB, revit, script

def print_revision(sheet):
    print sheet.Name
    for id in sheet.GetAllRevisionIds():
        rev = revit.doc.GetElement(id)
        print "\t{}\t{}".format(rev.Name, rev.RevisionDate )
    print "-"*20



def sheet_rev_data(sheet):

    data = ["{}-{}".format(sheet.SheetNumber, sheet.Name)]
    data.append("[Yes]" if sheet.LookupParameter("Appears In Sheet List").AsInteger() else "-")
    map(lambda rev: data.append("Yes" if rev.Id in sheet.GetAllRevisionIds() else "-"), _rev_collection)
    #print data
    """
    for id in _rev_id_collection:
        print id
        print sheet.GetAllRevisionIds()[0]
    """
    _data_table.append( data )


def final_print_table(table_data):
    output = script.get_output()
    output.set_title("List Revision")
    columns = ["Sheet Name", "In Sheet List?"]

    for rev in _rev_collection:
        columns.append( "{}-->{}".format(rev.Name, rev.RevisionDate ))

    output.print_table(table_data=table_data,title="Review those revision on sheets",columns = columns)

################## main code below #####################
if __name__== "__main__":
    all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    """
    map(print_revision, filter(lambda x: str(x.ViewType) == "DrawingSheet", all_views))
    """


    _data_table =[]
    _rev_collection = [revit.doc.GetElement(id) for id in DB.Revision.GetAllRevisionIds(revit.doc)]
    sheets = filter(lambda x: str(x.ViewType) == "DrawingSheet", all_views)
    sheets.sort(key = lambda x: x.SheetNumber, reverse = False)


    sel = forms.alert(msg = "Sort by sheets that is not sheet list?\nI will check [Appears In Sheet List] checkbox for you.", options = ["Yes, put those sheets at the buttom of the list", "No, just rank them by sheet number only"])
    if "No" in sel or sel == None:#no need to change
        pass
    else:#take out the sheets that is not on sheet list
        sheets.sort(key = lambda x: x.LookupParameter("Appears In Sheet List").AsInteger(), reverse = True)

    map(sheet_rev_data, sheets)
    final_print_table(_data_table)

