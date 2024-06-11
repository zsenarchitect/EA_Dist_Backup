__title__ = 'Open\n Sample Panel'
__context__ = "zero-doc"
from pyrevit import forms

""" make this UUID come from the woirking py file"""
panel_uuid = "3110e336-f81c-4927-87da-4e0d30d4d641"

forms.open_dockable_panel(panel_uuid)
