from pyrevit import forms
from pyrevit import EXEC_PARAMS

try:
    forms.alert(EXEC_PARAMS.event_args.CurrentActiveView.ViewName)
except:
    forms.alert(EXEC_PARAMS.event_args.CurrentActiveView.Name)
