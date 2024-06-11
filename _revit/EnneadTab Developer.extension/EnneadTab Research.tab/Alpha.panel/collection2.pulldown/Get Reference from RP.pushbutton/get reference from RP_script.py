__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Get Reference from RP"


from pyrevit import DB, revit, forms, script

selection = revit.get_selection()

for item in selection:
    print(item.GetReference().ElementReferenceType)
    print(item.GetReference().ElementId)
