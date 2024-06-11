__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Reset All\nTemp View Template"

from pyrevit import DB, revit, forms, script

all_views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

with revit.Transaction("Reset temp view"):
    for view in all_views:

        if str(view.ViewType) in ["Schedule","ProjectView","ProjectBrowser","SystemBrowser"]:
            continue

        try:
            view.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryViewProperties)
        except Exception as e:
            print (e)
            print(view.ViewType)
