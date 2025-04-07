#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Assign targets for symbol families. Pick a symbol family and assign glass/opaque targets."
__title__ = "Assign Target"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_EVENT
from pyrevit.forms import WPFWindow
from Autodesk.Revit import UI, DB # pyright: ignore 
from pyrevit import forms

import traceback

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()



class AssignTargetForm(WPFWindow):

    def update_glass_targets(self, symbol, ids):
        t = self.DB.Transaction(self.doc, "Assign Glass Targets")
        t.Start()
        symbol.Symbol.LookupParameter("_GlassTargetIds").Set(";".join(ids))
        t.Commit()

    def update_total_targets(self, symbol, ids):
        t = self.DB.Transaction(self.doc, "Assign Total Targets")
        t.Start()
        symbol.Symbol.LookupParameter("_TotalTargetIds").Set(";".join(ids))
        t.Commit()

        
    def register_events(self):
        self.func_list = ["update_glass_targets", "update_total_targets"]
        for func_name in self.func_list:
            
            setattr(self, "{}_event_handler".format(func_name), REVIT_EVENT.SimpleEventHandler(getattr(self, func_name)))
            setattr(self, "ext_event_{}".format(func_name), REVIT_EVENT.ExternalEvent.Create(getattr(self, "{}_event_handler".format(func_name))))

    
    """
    Modeless form for assigning targets to symbol families
    """
    def __init__(self):
        self.note = None
        self.doc = DOC
        self.DB = DB
        self.register_events()
        
        WPFWindow.__init__(self, "assign_target_ModelessForm.xaml")
        self.selected_symbol = None
        self.selected_glass = None
        self.selected_opaque = None
        self.Show()

    @ERROR_HANDLE.try_catch_error()
    def pick_symbol_click(self, sender, args):
        """Pick a symbol family from the model"""

        from EnneadTab.REVIT import REVIT_SELECTION
        sel = REVIT_SELECTION.get_selected_elements()
        if sel:
            self.selected_symbol = sel[0]
            self.note.Text = "Selected Family Symbol: {}".format(self.selected_symbol.Symbol.LookupParameter("Type Name").AsString())
            REVIT_SELECTION.clear_selection()

    @ERROR_HANDLE.try_catch_error()
    def pick_glass_click(self, sender, args):
        """Pick a glass target from the model"""
 
        from EnneadTab.REVIT import REVIT_SELECTION
        from EnneadTab import NOTIFICATION
        from Autodesk.Revit import DB # pyright: ignore 
        sel = REVIT_SELECTION.get_selected_elements()
        if sel:
            ids = []
            for x in sel:
                if self.is_filled_region(x):
                    ids.append(x.UniqueId)
            if self.selected_symbol:
                handler, ext_event = self.get_handler_event_by_keyword("update_glass_targets")
                handler.args = self.selected_symbol, ids
                ext_event.Raise()
                NOTIFICATION.messenger("Assigned {} Filled Region Glass Targets".format(len(ids)))
            REVIT_SELECTION.clear_selection()



    def is_filled_region(self, x):
        return x.Category.Name == "Detail Items" and hasattr(x, "IsMasking")
    
    @ERROR_HANDLE.try_catch_error()
    def pick_total_click(self, sender, args):
        """Pick a total target from the model"""
       
        from EnneadTab.REVIT import REVIT_SELECTION
        from EnneadTab import NOTIFICATION
        from Autodesk.Revit import DB # pyright: ignore 
        sel = REVIT_SELECTION.get_selected_elements()
        if sel:
            ids = []
            for x in sel:
                if self.is_filled_region(x):
                    ids.append(x.UniqueId)
            if self.selected_symbol:
                handler, ext_event = self.get_handler_event_by_keyword("update_total_targets")
                handler.args = self.selected_symbol, ids
                ext_event.Raise()
                NOTIFICATION.messenger("Assigned {} Filled Region Total Targets".format(len(ids)))
            REVIT_SELECTION.clear_selection()

    def get_handler_event_by_keyword(self, keyword):
        for func_name in self.func_list:
            if keyword not in func_name:
                continue
            handler = getattr(self, "{}_event_handler".format(func_name))
            ext_event = getattr(self, "ext_event_{}".format(func_name))
            return handler, ext_event

    def close_Click(self, sender, args):
        """Close the form"""
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        """Allow window dragging"""
        sender.DragMove()

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def assign_target(doc):
    """Main function to show the form"""
    form = AssignTargetForm()

################## main code below #####################
if __name__ == "__main__":
    assign_target(DOC)







