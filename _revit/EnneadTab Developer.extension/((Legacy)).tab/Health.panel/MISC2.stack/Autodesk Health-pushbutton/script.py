from pyrevit import forms
from pyrevit import script

__title__ = 'Autodesk Cloud Health'
__context__ = 'zero-doc'
__doc__ = 'Check what is going on in autodek server'


script.open_url("https://health.autodesk.com/")
import ENNEAD_LOG
ENNEAD_LOG.use_enneadtab(coin_change = 30, tool_used = "Check Autodesk Server Health.", show_toast = True)
