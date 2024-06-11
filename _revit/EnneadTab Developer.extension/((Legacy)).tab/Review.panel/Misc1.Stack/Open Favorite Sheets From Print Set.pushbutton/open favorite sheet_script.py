import time

t_start = time.time()

#from Autodesk.Revit import DB # pyright: ignore
from pyrevit import DB


from pyrevit import revit, forms
t_end = time.time()
#print t_end - t_start

doc = __revit__.ActiveUIDocument.Document # pyright: ignore
#print doc

__title__ = 'Open\nFave Sheets'
sel_sheets = forms.select_sheets(title='Select Sheets')
__doc__ = 'This is helpful when you are working on a group of sheets repeatedly. Makes for an easier morning.'



if sel_sheets:
	for sheet in sel_sheets:
		sheetId = sheet.Id
		window = revit.doc.GetElement(sheetId)
		revit.uidoc.ActiveView = window
