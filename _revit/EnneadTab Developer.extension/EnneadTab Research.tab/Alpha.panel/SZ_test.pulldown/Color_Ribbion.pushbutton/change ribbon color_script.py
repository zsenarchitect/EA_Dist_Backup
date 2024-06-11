from pyrevit import revit, UI,DB

__doc__ = "**try access the project browser and ribbon property"
__title__ = "proj. browser\nribbon property"

project_browser_id = UI.DockablePanes.BuiltInDockablePanes.ProjectBrowser
#project_browser = revit.doc.GetElement(project_browser_id)

print(project_browser_id)


ribbon_panel = UI.RibbonPanel
print(ribbon_panel.Name,ribbon_panel.Title)
