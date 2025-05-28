#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Warning tracking system that reveals error trends across your project history.

This powerful diagnostic tool displays comprehensive warning logs that have been automatically 
recorded by EnneadTab, allowing you to analyze warning patterns over time. 

Usage:
    Select one or more documents to analyze their warning history.
"""

__title__ = "Display Revit\nWarning History"
__tip__ = True

import os
from pyrevit import forms, script
from Autodesk.Revit import DB  # pyright: ignore

import proDUCKtion  # pyright: ignore
proDUCKtion.validify()

from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_HISTORY
from EnneadTab import ENVIRONMENT, NOTIFICATION, ERROR_HANDLE, LOG, FOLDER

doc = REVIT_APPLICATION.get_doc()


class WarningHistoryOption(forms.TemplateListItem):
    """Custom option class for warning history file selection."""
    
    @property
    def name(self):
        """Get the formatted name of the warning history file."""
        return self.item.replace("REVIT_WARNING_HISTORY_", "").replace(ENVIRONMENT.PLUGIN_EXTENSION, "")


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def display_warning_history():
    """Display warning history for selected documents."""
    show_detail = _get_detail_preference()
    if show_detail is None:
        return

    selected_files = _select_warning_history_files()
    if not selected_files:
        return

    _show_chart_js_hint()
    for file_item in selected_files:
        file_name = file_item.replace("REVIT_WARNING_HISTORY_", "").replace(ENVIRONMENT.PLUGIN_EXTENSION, "")
        REVIT_HISTORY.display_warning(file_name, show_detail=show_detail)

    print("Done")


def _get_detail_preference():
    """Get user preference for showing warning details.
    
    Returns:
        True for detailed view, False for graph only, None if cancelled
    """
    options = ["Yes, show details", "No details, just graph"]
    result = REVIT_FORMS.dialogue(
        main_text="Would you like to see the details of the warnings?",
        options=options
    )
    if not result:
        return None
    return result == options[0]


def _select_warning_history_files():
    """Select warning history files to analyze.
    
    Returns:
        List of selected files or None if cancelled
    """
    folder = FOLDER.SHARED_DUMP_FOLDER
    
    # Get all warning history files
    file_list = [
        WarningHistoryOption(x) 
        for x in os.listdir(folder) 
        if x.startswith("REVIT_WARNING_HISTORY_")
    ]
    

    
    # Sort files with current document first, then alphabetically
    def sort_key(x):
        if not doc.IsFamilyDocument and x.name == doc.Title:
            return (0, x.name)  # Current doc gets highest priority
        return (1, x.name)  # Other docs sorted alphabetically
    
    file_list.sort(key=sort_key)
    
    return forms.SelectFromList.show(
        file_list,
        button_name="Select Document(s)",
        multiselect=True,
        title="Select documents to analyze"
    )


def _show_chart_js_hint():
    """Display hint about JavaScript loading requirement."""
    hint_image = script.get_bundle_file("chart js hint.png")
    NOTIFICATION.messenger(
        main_text="When asked about loading java script, click 'yes'",
        image=hint_image
    )


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    display_warning_history()
    


