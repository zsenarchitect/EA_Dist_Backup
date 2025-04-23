#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Powerful batch cutting utility for curtain wall systems.

This tool enables efficient creation of void cuts across multiple curtain panels.
Features:
- Batch process curtain walls or individual panels
- Support for multiple selection methods
- Intelligent void detection and validation
- Transaction-safe operations with error handling

Usage:
1. Select curtain walls or panels
2. Choose void geometry
3. Apply cuts across all selected elements
"""
__title__ = "Batch Cut\nElements"
__is_popular__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ENVIRONMENT, ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_SYNC
from Autodesk.Revit import DB, UI # pyright: ignore 
from pyrevit import forms, script
from pyrevit.revit import ErrorSwallower

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

def get_panels_from_walls(walls):
    """Extract panels from selected curtain walls."""
    panels = []
    for wall in walls:
        if not isinstance(wall, DB.Wall):
            continue
        panel_ids = wall.CurtainGrid.GetPanelIds()
        panels.extend([DOC.GetElement(x) for x in panel_ids])
    return panels

def get_generic_models_by_comment(text):
    """Find generic models containing specified text in comments."""
    models = DB.FilteredElementCollector(DOC).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    valid_models = []
    for model in models:
        param = model.LookupParameter("Comments")
        if not param:
            continue
        param_value = param.AsString()
        if not param_value:
            continue
        if text.lower() in param_value.lower():
            valid_models.append(model)
    return valid_models

def get_void_masses():
    """Collect void masses with specific description."""
    masses = DB.FilteredElementCollector(DOC).OfCategory(DB.BuiltInCategory.OST_Mass).WhereElementIsNotElementType().ToElements()
    valid_masses = []
    for mass in masses:
        if not mass.Symbol:
            continue
        param = mass.Symbol.LookupParameter("Description")
        if not param:
            continue
        param_value = param.AsString()
        if not param_value:
            continue
        if param_value.lower() == "{} void".format(ENVIRONMENT.PLUGIN_NAME).lower():
            valid_masses.append(mass)
    return valid_masses

class VoidOption(forms.TemplateListItem):
    """Custom list item for void selection."""
    @property
    def name(self):
        return self.Symbol.Family.Name

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_cut():
    """Main function to execute batch cutting operation."""
    # Selection method options
    opts = [
        "Get CW panels by selection walls",
        "Use selected floors or CW panels",
        "Use Generic Models by comments"
    ]
    
    res = forms.SelectFromList.show(opts, multiselect=False, title="How do you want to find the elements to cut")
    if not res:
        return

    # Collect elements based on selection method
    if res == opts[0]:
        walls = UIDOC.Selection.PickObjects(UI.Selection.ObjectType.Element, "Pick curtainwalls with panels to cut")
        walls = [DOC.GetElement(x) for x in walls]
        all_elements_to_cut = get_panels_from_walls(walls)
        if not all_elements_to_cut:
            NOTIFICATION.messenger("No panels found in selected walls")
            return
            
    elif res == opts[1]:
        all_elements_to_cut = REVIT_SELECTION.get_selection(UIDOC)
        
    else:  # opts[2]
        text_to_search = forms.ask_for_string(prompt="Enter text to search for in comments",
                                              title=ENVIRONMENT.PLUGIN_NAME,
                                              default_value="something something something darkside, something something something completed")
        all_elements_to_cut = get_generic_models_by_comment(text_to_search)
        if not all_elements_to_cut:
            NOTIFICATION.messenger("No generic models found with comments: {}".format(text_to_search))
            return

    if not all_elements_to_cut:
        NOTIFICATION.messenger("No elements found")
        return

    # Get and validate void masses
    masses = get_void_masses()
    if not masses:
        NOTIFICATION.messenger("No voids found. Expected description: [{} void]".format(ENVIRONMENT.PLUGIN_NAME))
        return

    # Select void to use
    masses = [VoidOption(x) for x in masses]
    select_void = forms.SelectFromList.show(masses, multiselect=False, title="Select voids to cut")
    if not select_void:
        NOTIFICATION.messenger("No void selected")
        return

    # Confirm sync and close preference
    is_sync_and_close = REVIT_SYNC.do_you_want_to_sync_and_close_after_done()

    # Execute cutting operation
    t = DB.Transaction(DOC, __title__)
    t.Start()
    
    with ErrorSwallower() as ES:
        for element in all_elements_to_cut:
            try:
                DB.SolidSolidCutUtils.AddCutBetweenSolids(DOC, element, select_void)
            except Exception as e:
                print("Failed to cut element: {}: {}".format(output.linkify(element.Id), e))

    t.Commit()

    if is_sync_and_close:
        REVIT_SYNC.sync_and_close()

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    batch_cut()







