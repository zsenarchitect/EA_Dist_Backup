from pyrevit import EXEC_PARAMS

if EXEC_PARAMS.executed_from_ui:
    __all__ = ['script', 'revit2rhino_script', 'revit2rhino_UI', 'revit2rhino_action'] 