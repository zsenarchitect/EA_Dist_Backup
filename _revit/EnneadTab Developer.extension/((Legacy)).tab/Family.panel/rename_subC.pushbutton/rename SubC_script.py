__doc__ = "Replace one part of the SubCategory name with another text. Both keyword to search will be asked."
__title__ = "Rename SubC"
__context__ = "doc-family"
from pyrevit import forms, DB, revit, script

def main():

    ParentCategory = revit.doc.OwnerFamily.FamilyCategory
    subCs = ParentCategory.SubCategories
    for subC in subCs:
        print(subC.Name)


    subC_name_to_replace = forms.ask_for_string( default = subC.Name, prompt = "which text in the name you do not like", title = "change what?")
    if not subC_name_to_replace:
        return
    subC_name_to_insert = forms.ask_for_string( default = "???", prompt = "Changing {} to what?".format(subC_name_to_replace), title = "insert what?")
    if not subC_name_to_insert:
        return




    with revit.Transaction("rename subC name"):
        for subC in subCs:
            old_name = subC.Name
            try:
                new_name = old_name.replace(subC_name_to_replace, subC_name_to_insert)
                subC.Name = new_name
            except Exception as e:
                print (e)
                print("bad subC: {}".format(old_name))

################## main code below #####################
output = script.get_output()
output.close_others()
if __name__ == "__main__":
    main()
