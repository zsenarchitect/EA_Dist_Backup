#!/usr/bin/python
# -*- coding: utf-8 -*-

INTERNAL_TEXTNOTE_TYPE_NAME = "_internal_note"
__doc__ = """Handle internal textnotes in the project.
This tool allows you to show or hide all internal textnotes at once."""

__title__ = "Internal Textnote\nHandler"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, DATA_CONVERSION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


class InternalTextnoteHandler:
    """Handler class for managing internal textnotes visibility."""
    
    def __init__(self, doc):
        """Initialize the handler.
        
        Args:
            doc: Current Revit document
        """
        self.doc = doc
        self.internal_textnotes = []
        self.editable_notes = []
        self.unchanged = 0
        self.unchanged_owners = set()
        self.modified = 0
        
    def get_internal_textnotes(self):
        """Get all internal textnotes in the project."""
        collector = DB.FilteredElementCollector(self.doc).OfClass(DB.TextNote)
        all_textnotes = list(collector.ToElements())
        
        self.internal_textnotes = [note for note in all_textnotes 
                                 if note.TextNoteType.LookupParameter("Type Name").AsString() == INTERNAL_TEXTNOTE_TYPE_NAME]
        return bool(self.internal_textnotes)
        
    def get_user_choice(self):
        """Show dialog for user to choose show/hide action.
        
        Returns:
            bool: True for show, False for hide, None if cancelled
        """
        options = ["Show all internal notes", "Hide all internal notes"]
        res = REVIT_FORMS.dialogue(main_text="Internal Textnote Visibility",
                                  sub_text="Choose action for internal textnotes",
                                  options=options)
        
        if not res:
            return None
        return res == options[0]
        
    def process_textnotes(self):
        """Process textnotes to separate editable and non-editable ones."""
        self.editable_notes = []
        self.unchanged = 0
        self.unchanged_owners = set()
        
        for note in self.internal_textnotes:
            if REVIT_SELECTION.is_changable(note):
                self.editable_notes.append(note)
            else:
                self.unchanged += 1
                owner = REVIT_SELECTION.get_owner(note)
                if owner:
                    self.unchanged_owners.add(owner)
                    
        return bool(self.editable_notes)
        
    def modify_visibility(self, show_notes):
        """Modify visibility of each textnote in its owner view and dependent views.
        
        Args:
            show_notes: True to show, False to hide
        """
        self.modified = 0
        self.show_notes = show_notes  # Store the state for reporting
        t = DB.Transaction(self.doc, __title__)
        t.Start()
        
        for note in self.editable_notes:
            view_id = note.OwnerViewId
            view = self.doc.GetElement(view_id)
            
            # Get all views to process (main view + dependent views)
            views_to_do = [view]
            dependent_view_ids = list(view.GetDependentViewIds())
            if dependent_view_ids:
                views_to_do.extend([self.doc.GetElement(x) for x in dependent_view_ids])
            
            # Process each view (main + dependent)
            for current_view in views_to_do:
                if not current_view:
                    print("Cannot process view: {}".format(view.Name if view else "Unknown"))
                    continue
                
                # Check if view is owned by others
                if not REVIT_SELECTION.is_changable(current_view):
                    owner = REVIT_SELECTION.get_owner(current_view)
                    print("Skipping view '{}' - owned by: {}".format(current_view.Name, owner if owner else "others"))
                    continue
                
                element_ids = DATA_CONVERSION.list_to_system_list([note.Id])
                if show_notes:
                    current_view.UnhideElements(element_ids)
                else:
                    current_view.HideElements(element_ids)
            
            self.modified += 1
            
        t.Commit()
        
    def report_results(self):
        """Generate and show results message."""
        message = "Modified {} internal textnotes as {}.".format(self.modified, "visible" if self.show_notes else "hidden")
        if self.unchanged > 0:
            message += "\n{} internal textnotes unchanged due to ownership by:".format(self.unchanged)
            for owner in sorted(self.unchanged_owners):
                message += "- {}\n".format(owner)
                
        NOTIFICATION.messenger(message)
        
    def execute(self):
        """Execute the textnote visibility handling process."""
        if not self.get_internal_textnotes():
            NOTIFICATION.messenger("No internal textnotes found in project.\nThe type name used for searching is: [{}]".format(INTERNAL_TEXTNOTE_TYPE_NAME))
            return
            
        show_notes = self.get_user_choice()
        if show_notes is None:
            return
            
        if not self.process_textnotes():
            NOTIFICATION.messenger("No editable internal textnotes found.")
            return
        
        self.modify_visibility(show_notes)
        self.report_results()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def handle_internal_textnote(doc):
    """Main function to handle internal textnotes visibility."""
    handler = InternalTextnoteHandler(doc)
    handler.execute()

################## main code below #####################
if __name__ == "__main__":
    handle_internal_textnote(DOC)







