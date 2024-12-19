#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Merge\nObject Style"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import forms
# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


class SubCategoryItem(forms.TemplateListItem):
    @property
    def name(self):
        parent_category = self.item.Parent.Name
        sub_category = self.item.Name
        return "{}: {}".format(parent_category, sub_category)

class DocumentChangeTracker:
    def __init__(self):
        self.changes = []
        
    def on_doc_changed(self, sender, args):
        # Track modifications
        for id in args.GetModifiedElementIds():
            self.changes.append(("Modified", id))
        # Track deletions
        for id in args.GetDeletedElementIds():
            self.changes.append(("Deleted", id))
            
    def clear(self):
        self.changes = []

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def merge_ost(doc):
    bad_sub_category = select_sub_category("Bad")
    if not bad_sub_category:
        return
    target_sub_category = select_sub_category("Target", bad_sub_category.Parent.Name)
    if not target_sub_category:
        return
    
    print(bad_sub_category)
    print(target_sub_category)
    
    # Setup change tracker
    change_tracker = DocumentChangeTracker()
    doc.Application.DocumentChanged += change_tracker.on_doc_changed
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    doc.Delete(bad_sub_category.Id)
    
    # Print affected elements
    print("Changes detected during subcategory deletion:")
    print("delete {}: {}".format(bad_sub_category.Parent.Name, bad_sub_category.Name))
    print(change_tracker.changes)
    for change_type, element_id in change_tracker.changes:
        try:
            element = doc.GetElement(element_id)
            if element:
                category_name = element.Category.Name if element.Category else "No Category"
                if isinstance(element, DB.Family):
                    print("\t{}: Family '{}' (ID: {})".format(change_type, element.Name, element_id))
                else:
                    print("\t{}: {} - {} (ID: {})".format(change_type, category_name, element.GetType().Name, element_id))
            else:
                print("\t{}: Deleted Element (ID: {})".format(change_type, element_id))
        except Exception as e:
            print("\t{}: Error getting element info - {} (ID: {})".format(change_type, str(e), element_id))
    
    t.RollBack()
    
    # Cleanup event handler
    doc.Application.DocumentChanged -= change_tracker.on_doc_changed

def output_element_info(doc, element_id):
    try:
        element = doc.GetElement(element_id)
        return "{} - ID: {}".format(element.GetType().Name, element_id)
    except:
        return "Unknown Element - ID: {}".format(element_id)

def select_sub_category(task, limited_category = None):
    sub_categories = []
    all_categories = DOC.Settings.Categories
    for category in sorted(all_categories, key=lambda x: x.Name):
        if limited_category and category.Name != limited_category:
            continue
        for sub_category in category.SubCategories:
            sub_categories.append(SubCategoryItem(sub_category))
    
    sub_categories.sort(key=lambda x: x.name)
    res = forms.SelectFromList.show(sub_categories, 
                                    button_name="Select {} SubCategory".format(task),
                                    title="Select {} SubCategory".format(task))
                                 
    return res




################## main code below #####################
if __name__ == "__main__":
    merge_ost(DOC)







