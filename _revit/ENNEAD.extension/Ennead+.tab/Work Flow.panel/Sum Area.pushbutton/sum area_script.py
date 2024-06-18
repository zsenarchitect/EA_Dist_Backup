__doc__ = "select multiple filled region and get summed area.\n\nGood for glazzing area ratio, bird friendly ratio so much more."
__title__ = "Sum FillRegions Area"

from pyrevit import revit,forms, script


if __name__== "__main__":

    """
    cats = revit.doc.Settings.Categories
    for cat in cats:
        #print cat.Name
        if "Filled region" == cat.Name:
            break
    use PICK script to prefilter type and change to pick by rec or click?
    """


    def format_area(total):
        return '\t= {} square feet\n' \
            '\t= {} square meters'.format(total,
                                        total/10.7639)


    selection = revit.get_selection()

    if len(selection) == 0:
        forms.alert("Please select at least one filled region.")
        script.exit()

    sum = 0
    for element in selection:
        #print element.Category.Name
        if "Detail Items" != element.Category.Name:
            forms.alert("There are non-detail items in the selection.")
            script.exit()
        try:
            sum += element.LookupParameter("Area").AsDouble()
        except:
            forms.alert("There are item in the selection that has no area value.")
            script.exit()

    forms.alert( "{} elements total area:\n".format(len(selection)) + format_area(sum)  )
