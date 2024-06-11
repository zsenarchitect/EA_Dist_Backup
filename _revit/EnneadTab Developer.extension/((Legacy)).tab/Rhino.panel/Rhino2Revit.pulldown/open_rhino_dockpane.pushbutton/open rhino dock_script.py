__title__ = 'Open Rhino2Revit Panel'

from pyrevit import forms
import Rhino_DockPane


panel_uuid = Rhino_DockPane.PANEL_ID
print(panel_uuid)
forms.open_dockable_panel(panel_uuid)
