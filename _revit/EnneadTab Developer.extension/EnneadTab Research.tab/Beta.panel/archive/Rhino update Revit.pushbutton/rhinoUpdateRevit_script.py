
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script



__doc__ = "try to convert rhino shape into exisitiong revit element previously converted by this tool."
__title__ = "Update Revit\nBy Rhino"

output = script.get_output()
output.self_destruct(60)
