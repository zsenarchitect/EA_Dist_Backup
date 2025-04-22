#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "The big different from the Revit version is that you can use this to fix the wrong view type template that was resulted from duplicating wrong view teyp and cause revit default type group to display wrongly."
__title__ = "Make Template\nFrom Current View"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def make_template_from_current_view(doc):

    # get current view
    current_view = doc.ActiveView

    # Check if there is a template applied, then remove template, but record the template name
    template_name = current_view.Name
    original_template = None
    
    if current_view.ViewTemplateId and current_view.ViewTemplateId != DB.ElementId.InvalidElementId:
        original_template = doc.GetElement(current_view.ViewTemplateId)
        if original_template:
            template_name = original_template.Name

    # Create a new view template using pyrevit form
    new_template_name = forms.ask_for_string(
        default=template_name,
        prompt="Enter a name for the new view template",
        title="Create View Template"
    )

    is_overriding = new_template_name == template_name
    
    if not new_template_name:
        return

    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # If there is a template applied, remove it first
    if original_template:
        if is_overriding:
            original_template.Name += " - past"
        current_view.ViewTemplateId = DB.ElementId.InvalidElementId
    
    # Create a new view template from current view
    new_template = current_view.CreateViewTemplate()
    new_template.Name = new_template_name


    doc.ActiveView.ViewTemplateId = new_template.Id

    if original_template:
        all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
        for view in all_views:
            if view.ViewTemplateId == original_template.Id:
                view.ViewTemplateId = new_template.Id
        doc.Delete(original_template.Id)
    
    t.Commit()


################## main code below #####################
if __name__ == "__main__":
    make_template_from_current_view(DOC)







