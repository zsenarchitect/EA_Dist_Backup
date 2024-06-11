
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script



__doc__ = "try to convert rhino shape into exisitiong revit element previously converted by this tool. It will preserve certain annotations relationship such as dimension and tag"
__title__ = "Update Revit\nBy Rhino"

output = script.get_output()
output.self_destruct(60)

forms.alert( "Work in progress. \nThank you for checking:)")
