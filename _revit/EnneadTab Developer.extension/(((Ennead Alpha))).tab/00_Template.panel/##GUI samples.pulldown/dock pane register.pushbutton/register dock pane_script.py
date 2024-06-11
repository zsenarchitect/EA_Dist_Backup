
import sys
import time
import os.path as op

from pyrevit import HOST_APP, framework
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import routes



# test dockable panel =========================================================

class DockableExample(forms.WPFPanel):
    panel_title = "123pyRevit Dockable Panel Title"
    panel_id = "0110e336-f81c-4927-87da-4e0d30d4d64a"
    panel_source = op.join(op.dirname(__file__), "DockableExample.xaml")

    def do_something(self, sender, args):
        forms.alert("EA Voila!!!")


forms.register_dockable_panel(DockableExample, True)
print("regiester ok")
