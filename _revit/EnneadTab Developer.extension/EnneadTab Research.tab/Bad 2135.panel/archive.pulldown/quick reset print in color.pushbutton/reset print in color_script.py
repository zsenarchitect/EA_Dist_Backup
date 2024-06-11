__doc__ = "Reset print in color setting for the sheets."
__title__ = "reset print in color!!"

from pyrevit import forms, revit, script #
from Autodesk.Revit import DB # pyright: ignore 
"""
from Autodesk.Revit import UI # pyright: ignore
uiapp = UI.UIApplicationapp
uidoc = UI.UIDocument
#optional
host_app = pyrevit._HostApplication
app = host_app.app
uiapp = host_app.uiapp
uidoc = host_app.uidoc



doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
"""
"""
from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc
"""

################## main code below #####################
script.exit()





output = script.get_output()
output.close_others()
#ideas:

sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

with revit.Transaction("reset print in color"):
    for sheet in sheets:
        sheet.LookupParameter("Print_In_Color").Set(1)
        #print sheet.SheetNumber
