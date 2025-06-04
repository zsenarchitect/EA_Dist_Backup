#!/usr/bin/python
# -*- coding: utf-8 -*-

INTERNAL_TEXTNOTE_TYPE_NAME = "_internal_note"
__doc__ = """Handle internal textnotes in the project.
This tool allows you to show or hide all internal textnotes at once.
The type name used for searching is: [{}]""".format(INTERNAL_TEXTNOTE_TYPE_NAME)

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
        
    def group_by_view(self):
        """Group textnotes by their owner view.
        
        Returns:
            dict: Dictionary mapping view_id to list of notes
        """
        textnotes_by_view = {}
        for note in self.editable_notes:
            view_id = note.OwnerViewId
            if view_id not in textnotes_by_view:
                textnotes_by_view[view_id] = []
            textnotes_by_view[view_id].append(note)
        return textnotes_by_view
        
    def modify_visibility(self, textnotes_by_view, show_notes):
        """Modify visibility of textnotes in their respective views.
        
        Args:
            textnotes_by_view: Dictionary of textnotes grouped by view
            show_notes: True to show, False to hide
        """
        self.modified = 0
        self.show_notes = show_notes  # Store the state for reporting
        t = DB.Transaction(self.doc, __title__)
        t.Start()
        
        for view_id, notes in textnotes_by_view.items():
            view = self.doc.GetElement(view_id)
            if not view:
                continue
                
            element_ids = DATA_CONVERSION.list_to_system_list([note.Id for note in notes])
            if show_notes:
                view.UnhideElements(element_ids)
            else:
                view.HideElements(element_ids)
            self.modified += len(notes)
        
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
        
        textnotes_by_view = self.group_by_view()
        self.modify_visibility(textnotes_by_view, show_notes)
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







