# # Reference the Revit API
# import clr

# clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')

from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, LOG
__title__ = "Create\nWorksets"
DEFAULT_LIST = [
    '0_Shared Levels & Grids', 
    '0_References', 
    '1_Core', 
    '1_FF&E', 
    '1_Shell', 
    '1_Interiors', 
    '1_Site', 
    '1_Structure',
    '2_RVT Links', 
    '3_CAD Links'
] 
__doc__ = """Create Worksets following the standard Ennead Workset Structure.
You can the options to create any or all from below:"""
for item in DEFAULT_LIST:
    __doc__ += "\n+< " + item + " >"
__tip__ = True
__is_popular__ = True

# Obtain the document object
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    # # get all existing workset names
    # names = [ws.Name for ws in DB.FilteredWorksetCollector(doc) if ws.Kind == DB.WorksetKind.UserWorkset]
    # print names

    

    # return
    if not doc.IsWorkshared:
        print ("This document is not workshared. Cannot Create Worksets.")
        return
    # A list of workset names
    default_workset_names = DEFAULT_LIST
    selected_workset_names = forms.SelectFromList.show(default_workset_names,
                                                       title = "Select Ennead Standard Worksets To Add",
                                                       multiselect  = True)
    if not selected_workset_names:
        return
    

    t = DB.Transaction(doc, 'Create Worksets')

    t.Start()
    existing_worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)
    for exsiting_workset in existing_worksets:
        if exsiting_workset.Name == "Workset1":
            print ("Workset <{}> renamed to <{}>".format(exsiting_workset.Name, selected_workset_names[0]))
            DB.WorksetTable.RenameWorkset(doc, exsiting_workset.Id,selected_workset_names[0])
            selected_workset_names.remove(selected_workset_names[0])


    for name in selected_workset_names:
        if not DB.WorksetTable.IsWorksetNameUnique(doc, name):
            print ("Workset name <{}> already exists. Skipping".format(name))
            continue
        DB.Workset.Create(doc, name)
        print ("Created Workset: {}".format(name))

    t.Commit()

if __name__ == '__main__':
    main()
    
