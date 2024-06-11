#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Open Dock Template Button"

from pyrevit import forms #
from pyrevit import script #
from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 

app = __revit__
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
app = doc.Application



from Autodesk.Revit import UI # pyright: ignore
uiapp = UI.UIApplicationapp
uidoc = UI.UIDocument
#optional
host_app = pyrevit._HostApplication
app = host_app.app
uiapp = host_app.uiapp
uidoc = host_app.uidoc


from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc


################## main code below #####################
output = script.get_output()
output.close_others()
