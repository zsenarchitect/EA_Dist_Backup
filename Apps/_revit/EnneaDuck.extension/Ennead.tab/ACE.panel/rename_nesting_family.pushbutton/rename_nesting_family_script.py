#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Scans through project families and their nested components to remove '*ConflictingName' string.
            
PROCESS:
- Iterates through all families in current project
- Opens each family document
- Checks nested families for '*ConflictingName' string
- Renames affected nested families by removing the conflicting string
- Loads modified families back to project
- Logs all changes made during the process

You can also requist to locate and rename based on other rules.
"""
__title__ = "Rename\nNesting Family"
__is_popular__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from pyrevit.revit import ErrorSwallower

from EnneadTab import ERROR_HANDLE, LOG, UI
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

class NestingFamilyRenamer:
    """Handles the renaming of nested families to remove '*ConflictingName' string.
    
    Attributes:
        doc: Current Revit document
        changes_made: List to track all renaming operations
    """
    
    def __init__(self, doc):
        self.doc = doc
        self.changes_made = []

    def process_family(self, family):
        """Process a single family and its nested components.
        
        Args:
            family: Revit Family element to process
        """
        if not family.IsEditable:
            return
            

        family_doc = self.doc.EditFamily(family)
        needs_update = False
        
        # Start transaction in family document
        t_family = DB.Transaction(family_doc, "Rename Nested Families")
        t_family.Start()
        
        nested_families = DB.FilteredElementCollector(family_doc).OfClass(DB.Family).ToElements()
        for nested in nested_families:
            attemp = 0
            while True:
                if attemp > 10:
                    break
                if "*ConflictingName" in nested.Name:
                    new_name = nested.Name.replace("*ConflictingName", "")
                    try:
                        nested.Name = new_name
                        needs_update = True
                        self.changes_made.append("In {}: Renamed {} to {}".format(
                            family.Name, nested.Name + "*ConflictingName", new_name))
                    except Exception as e:
                        print("Error renaming {} inside {} because {}".format(nested.Name, family.Name, e))
                        attemp += 1
                else:
                    break
        
        t_family.Commit()
        
        if needs_update:
            REVIT_FAMILY.load_family(family_doc, self.doc)
        family_doc.Close(False)

    def report_changes(self):
        """Report all changes made during the renaming process."""
        if self.changes_made:
            print("Changes made:")
            for change in self.changes_made:
                print(change)
        else:
            print("No conflicting family names found.")

    def process_all_families(self):
        """Process all families in the document."""
        all_families = DB.FilteredElementCollector(self.doc).OfClass(DB.Family).ToElements()

        with ErrorSwallower() as ES:
            UI.progress_bar(all_families, self.process_family)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def rename_nesting_family(doc):
    """Main function to process all families in the document."""
    renamer = NestingFamilyRenamer(doc)
    renamer.process_all_families()
    renamer.report_changes()

################## main code below #####################
if __name__ == "__main__":
    rename_nesting_family(DOC)







