#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Monitor for new views in the project and allow quick renaming through a non-blocking interface."
__title__ = "Place Views\nOn Sheets"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_AUTO, REVIT_EVENT
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit.forms import WPFWindow
import clr # pyright: ignore
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import TextBox, DialogResult, Form # pyright: ignore
import System # pyright: ignore
import re
import time

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

def save_current_view_state(doc):
    """
    Save all current view IDs to track which ones are new later
    
    Args:
        doc: The current Revit document
    """
    try:
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab import DATA_FILE, NOTIFICATION # pyright: ignore
        
        all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        all_view_ids = [view.Id.IntegerValue for view in all_views]
        DATA_FILE.set_data({"all_views": all_view_ids}, "all_current_views")
        NOTIFICATION.messenger("View state saved with {} views".format(len(all_view_ids)))
    except Exception as e:
        from EnneadTab import NOTIFICATION # pyright: ignore
        NOTIFICATION.messenger("Error saving view state: {}".format(str(e)))


class ViewsMonitorForm(WPFWindow):
    """Modeless window for monitoring and renaming newly created views"""
    
    class SheetItem:
        """Wrapper for sheet objects"""
        def __init__(self, sheet):
            self.sheet = sheet
            self.Id = sheet.Id.IntegerValue
            self.Name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
        
        def __repr__(self):
            return self.Name
    
    class ScopeBoxItem:
        """Wrapper for scope box objects"""
        def __init__(self, scope_box):
            self.scope_box = scope_box
            self.Id = scope_box.Id.IntegerValue
            self.Name = scope_box.Name
        
        def __repr__(self):
            return self.Name
    
    class ViewTemplateItem:
        """Wrapper for view template objects"""
        def __init__(self, template):
            self.template = template
            self.Id = template.Id.IntegerValue
            self.Name = template.Name
        
        def __repr__(self):
            return self.Name
    
    class ViewItem:
        """Wrapper class for Revit view objects to be displayed in the DataGrid"""
        def __init__(self, view, doc, parent_class):
            # Import inside method to handle scope issues
            from Autodesk.Revit import DB # pyright: ignore
            from EnneadTab import ERROR_HANDLE # pyright: ignore
            
            try:
                self.view = view
                self.doc = doc
                self.parent = parent_class  # Store reference to the parent class
                self.Name = view.Name
                self.Id = view.Id.IntegerValue
                self.ViewType = str(view.ViewType)
                
                # Sheet information
                self._sheet_info = None
                self._all_sheets = None
                self._selected_sheet = None
                
                # Scope box information
                self._all_scope_boxes = None
                self._selected_scope_box = None
                
                # View template information
                self._all_view_templates = None
                self._selected_view_template = None
                
                # Initialize data
                self._initialize_data()
            except Exception as e:
                ERROR_HANDLE.print_traceback()
        
        @ERROR_HANDLE.try_catch_error()
        def _initialize_data(self):
            """Initialize all the data for this view item"""
            # Import inside method to handle scope issues
            from Autodesk.Revit import DB # pyright: ignore
            
            # Get list of all sheets
            sheets = self._get_all_sheets()
            # Use parent reference instead of global class name
            self._all_sheets = [self.parent.SheetItem(s) for s in sheets]
            
            # Get the sheet this view is placed on (if any)
            sheet_id = self._get_sheet_id()
            if sheet_id:
                sheet = self.doc.GetElement(sheet_id)
                if sheet:
                    # Create sheet info text
                    self._sheet_info = "On Sheet: {} - {}".format(sheet.SheetNumber, sheet.Name)
                    
                    # Find the matching SheetItem in the list
                    for sheet_item in self._all_sheets:
                        if sheet_item.Id == sheet.Id.IntegerValue:
                            self._selected_sheet = sheet_item
                            break
                    
                    # If not found in the list (unlikely), create it
                    if not self._selected_sheet:
                        self._selected_sheet = self.parent.SheetItem(sheet)
            else:
                self._sheet_info = "Not placed on sheet"
            
            # Get list of all scope boxes
            scope_boxes = self._get_all_scope_boxes()
            # Use parent reference instead of global class name
            self._all_scope_boxes = [self.parent.ScopeBoxItem(sb) for sb in scope_boxes]
            
            # Get current scope box if any
            current_scope_box_id = self._get_current_scope_box_id()
            if current_scope_box_id:
                scope_box = self.doc.GetElement(current_scope_box_id)
                if scope_box:
                    for sb_item in self._all_scope_boxes:
                        if sb_item.Id == scope_box.Id.IntegerValue:
                            self._selected_scope_box = sb_item
                            break
            
            # Get list of all view templates
            templates = self._get_all_view_templates()
            # Use parent reference instead of global class name
            self._all_view_templates = [self.parent.ViewTemplateItem(t) for t in templates]
            
            # Get current view template if any
            current_template_id = self._get_current_template_id()
            if current_template_id:
                template = self.doc.GetElement(current_template_id)
                if template:
                    for t_item in self._all_view_templates:
                        if t_item.Id == template.Id.IntegerValue:
                            self._selected_view_template = t_item
                            break
        
        @ERROR_HANDLE.try_catch_error()
        def _get_sheet_id(self):
            """Get the sheet ID this view is placed on"""
            from Autodesk.Revit import DB # pyright: ignore
            
            # Check if view is on a sheet
            sheet_id = None
            all_sheets = DB.FilteredElementCollector(self.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
            
            for sheet in all_sheets:
                view_ids = sheet.GetAllPlacedViews()
                if self.view.Id in view_ids:
                    return sheet.Id
            
            return None
        
        @ERROR_HANDLE.try_catch_error()
        def _get_all_sheets(self):
            """Get all sheets in the document"""
            from Autodesk.Revit import DB # pyright: ignore
            
            return DB.FilteredElementCollector(self.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        
        @ERROR_HANDLE.try_catch_error()
        def _get_all_scope_boxes(self):
            """Get all scope boxes in the document"""
            from Autodesk.Revit import DB # pyright: ignore
            
            return DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
        
        @ERROR_HANDLE.try_catch_error()
        def _get_current_scope_box_id(self):
            """Get the current scope box ID assigned to this view"""
            from Autodesk.Revit import DB # pyright: ignore
            
            param = self.view.get_Parameter(DB.BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
            if param and param.HasValue:
                return param.AsElementId()
            return None
        
        @ERROR_HANDLE.try_catch_error()
        def _get_all_view_templates(self):
            """Get all view templates in the document"""
            from Autodesk.Revit import DB # pyright: ignore
            
            all_views = DB.FilteredElementCollector(self.doc).OfClass(DB.View).ToElements()
            return [v for v in all_views if v.IsTemplate]
        
        @ERROR_HANDLE.try_catch_error()
        def _get_current_template_id(self):
            """Get the current view template ID assigned to this view"""
            from Autodesk.Revit import DB # pyright: ignore
            
            if self.view.ViewTemplateId and self.view.ViewTemplateId.IntegerValue != -1:
                return self.view.ViewTemplateId
            return None
        
        @property
        def SheetInfo(self):
            return self._sheet_info
        
        @property
        def AllSheets(self):
            return self._all_sheets
        
        @property
        def SelectedSheet(self):
            return self._selected_sheet
        
        @SelectedSheet.setter
        def SelectedSheet(self, value):
            self._selected_sheet = value
        
        @property
        def AllScopeBoxes(self):
            return self._all_scope_boxes
        
        @property
        def SelectedScopeBox(self):
            return self._selected_scope_box
        
        @SelectedScopeBox.setter
        def SelectedScopeBox(self, value):
            self._selected_scope_box = value
        
        @property
        def AllViewTemplates(self):
            return self._all_view_templates
        
        @property
        def SelectedViewTemplate(self):
            return self._selected_view_template
        
        @SelectedViewTemplate.setter
        def SelectedViewTemplate(self, value):
            self._selected_view_template = value
        
        def __repr__(self):
            return self.Name
    
    class TextInputForm(Form):
        """Simple input dialog for renaming views"""
        def __init__(self, title, label, default_value=""):
            # Explicitly import required modules
            import clr # pyright: ignore
            clr.AddReference("System.Windows.Forms")
            import System # pyright: ignore
            from System.Windows.Forms import TextBox, DialogResult, Form # pyright: ignore
            
            self.Text = title
            self.Width = 400
            self.Height = 150
            self.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
            self.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
            self.MaximizeBox = False
            self.MinimizeBox = False
            
            # Label
            self.label = System.Windows.Forms.Label()
            self.label.Text = label
            self.label.Location = System.Drawing.Point(10, 10)
            self.label.Width = 380
            self.Controls.Add(self.label)
            
            # TextBox
            self.textbox = TextBox()
            self.textbox.Text = default_value
            self.textbox.Location = System.Drawing.Point(10, 40)
            self.textbox.Width = 380
            self.Controls.Add(self.textbox)
            
            # OK Button
            self.ok_button = System.Windows.Forms.Button()
            self.ok_button.Text = "OK"
            self.ok_button.DialogResult = DialogResult.OK
            self.ok_button.Location = System.Drawing.Point(220, 80)
            self.Controls.Add(self.ok_button)
            
            # Cancel Button
            self.cancel_button = System.Windows.Forms.Button()
            self.cancel_button.Text = "Cancel"
            self.cancel_button.DialogResult = DialogResult.Cancel
            self.cancel_button.Location = System.Drawing.Point(310, 80)
            self.Controls.Add(self.cancel_button)
            
            # Set default button and accept/cancel buttons
            self.AcceptButton = self.ok_button
            self.CancelButton = self.cancel_button
            
    def __init__(self):
        """Initialize the monitor form"""
        self.doc = DOC
        self.register_events()
        self.is_interacting = False  # Flag to track user interaction
        WPFWindow.__init__(self, "place_views_on_sheets_ModelessForm.xaml")
        
        # Set up auto-refresh
        self.auto_refresh_func = self.update_new_views
        self.updater = REVIT_AUTO.RevitUpdater(self.auto_refresh_func, interval=1)
        self.updater.start()
        
        # Initial update
        self.update_new_views()
        self.Show()
    
    @ERROR_HANDLE.try_catch_error()
    def get_new_views(self, doc):
        """
        Get all views created since the last run
        
        Args:
            doc: The current Revit document
            
        Returns:
            list: List of newly created view elements
        """
        # Explicitly import required modules inside the method to ensure they're available
        from EnneadTab import DATA_FILE, ERROR_HANDLE, NOTIFICATION
        from Autodesk.Revit import DB # pyright: ignore
        
        try:
            data = DATA_FILE.get_data("all_current_views")
            if not data:
                return []

            all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
            return [x for x in all_views if x.Id.IntegerValue not in data["all_views"]]
        except Exception as e:
            NOTIFICATION.messenger("Error getting new views: {}".format(str(e)))
            ERROR_HANDLE.print_traceback()
            return []
    
    @ERROR_HANDLE.try_catch_error()
    def register_events(self):
        """Register event handlers for Revit operations that need to run in the API context"""
        try:
            self.func_list = ["rename_view", "assign_to_sheet", "assign_scope_box", "assign_view_template"]
            for func_name in self.func_list:
                setattr(self, "{}_event_handler".format(func_name), REVIT_EVENT.SimpleEventHandler(getattr(self, func_name)))
                setattr(self, "ext_event_{}".format(func_name), REVIT_EVENT.ExternalEvent.Create(getattr(self, "{}_event_handler".format(func_name))))
        except Exception as e:
            from EnneadTab import NOTIFICATION # pyright: ignore
            NOTIFICATION.messenger("Error registering events: {}".format(str(e)))
    
    @ERROR_HANDLE.try_catch_error()
    def get_handler_event_by_keyword(self, keyword):
        """Get the appropriate event handler and external event by keyword"""
        try:
            for func_name in self.func_list:
                if keyword not in func_name:
                    continue
                handler = getattr(self, "{}_event_handler".format(func_name))
                ext_event = getattr(self, "ext_event_{}".format(func_name))
                return handler, ext_event
            return None, None
        except Exception as e:
            from EnneadTab import NOTIFICATION # pyright: ignore
            NOTIFICATION.messenger("Error getting event handler: {}".format(str(e)))
            return None, None
    
    @ERROR_HANDLE.try_catch_error()
    def rename_view(self, view, new_name):
        """
        Rename a view with a transaction
        
        Args:
            view: The view element to rename
            new_name: New name for the view
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Explicitly import required modules
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab import NOTIFICATION, ERROR_HANDLE # pyright: ignore
        
        try:
            if not view or not new_name:
                NOTIFICATION.messenger("Invalid view or name provided")
                return False
            
            t = DB.Transaction(self.doc, "Rename View")
            t.Start()
            try:
                view.Name = new_name
                t.Commit()
                NOTIFICATION.messenger("View renamed to: {}".format(new_name))
                return True
            except Exception as e:
                t.RollBack()
                NOTIFICATION.messenger("Error renaming view: {}".format(str(e)))
                ERROR_HANDLE.print_traceback()
                return False
        except Exception as e:
            NOTIFICATION.messenger("Critical error in rename_view: {}".format(str(e)))
            ERROR_HANDLE.print_traceback()
            return False
    
    def assign_to_sheet(self, view, sheet_item):
        """
        Place a view on a sheet
        
        Args:
            view: The view to place
            sheet_item: SheetItem with the target sheet
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Explicitly import required modules
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab import NOTIFICATION # pyright: ignore
        
        if not sheet_item:
            return False
            
        sheet = sheet_item.sheet
        
        # Check if view already on this sheet
        all_sheets = DB.FilteredElementCollector(self.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        for s in all_sheets:
            view_ids = s.GetAllPlacedViews()
            if view.Id in view_ids:
                # View is already on a sheet
                if s.Id == sheet.Id:
                    # Already on the correct sheet - no need for transaction
                    return True
                else:
                    # On a different sheet - need to move it
                    break
        
        t = DB.Transaction(self.doc, "Place View on Sheet")
        t.Start()
        try:
            # Check if view already on a sheet
            all_sheets = DB.FilteredElementCollector(self.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
            for s in all_sheets:
                view_ids = s.GetAllPlacedViews()
                if view.Id in view_ids:
                    # View is already placed - need to remove it first
                    NOTIFICATION.messenger("View is already on another sheet. Moving to new sheet.")
                    # We need to find the viewport
                    viewports = DB.FilteredElementCollector(self.doc).OfClass(DB.Viewport).WhereElementIsNotElementType().ToElements()
                    for vp in viewports:
                        if vp.ViewId == view.Id:
                            self.doc.Delete(vp.Id)
                            break
            
            # Place view on sheet
            center_point = DB.XYZ(0,0,0)  # Default placement point
            DB.Viewport.Create(self.doc, sheet.Id, view.Id, center_point)
            t.Commit()
            NOTIFICATION.messenger("View placed on sheet {}".format(sheet.Name))
            return True
        except Exception as e:
            t.RollBack()
            NOTIFICATION.messenger("Error placing view: {}".format(str(e)))
            return False
    
    def assign_scope_box(self, view, scope_box_item):
        """
        Assign a scope box to a view
        
        Args:
            view: The view to modify
            scope_box_item: ScopeBoxItem with the target scope box
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Explicitly import required modules
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab import NOTIFICATION # pyright: ignore
        
        if not scope_box_item:
            return False
            
        scope_box = scope_box_item.scope_box
        
        # Check if view already has this scope box
        param = view.get_Parameter(DB.BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
        if param:
            current_id = param.AsElementId()
            if current_id and current_id == scope_box.Id:
                # Already using this scope box - no need for transaction
                return True
        
        t = DB.Transaction(self.doc, "Assign Scope Box")
        t.Start()
        try:
            param = view.get_Parameter(DB.BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
            if param:
                param.Set(scope_box.Id)
                t.Commit()
                NOTIFICATION.messenger("Scope box assigned: {}".format(scope_box.Name))
                return True
            else:
                t.RollBack()
                NOTIFICATION.messenger("This view does not support scope boxes")
                return False
        except Exception as e:
            t.RollBack()
            NOTIFICATION.messenger("Error assigning scope box: {}".format(str(e)))
            return False
    
    def assign_view_template(self, view, template_item):
        """
        Assign a view template to a view
        
        Args:
            view: The view to modify
            template_item: ViewTemplateItem with the target template
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Explicitly import required modules
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab import NOTIFICATION # pyright: ignore
        
        if not template_item:
            return False
            
        template = template_item.template
        
        # Check if view already has this template
        if view.ViewTemplateId == template.Id:
            # Already using this template - no need for transaction
            return True
        
        t = DB.Transaction(self.doc, "Assign View Template")
        t.Start()
        try:
            view.ViewTemplateId = template.Id
            t.Commit()
            NOTIFICATION.messenger("View template assigned: {}".format(template.Name))
            return True
        except Exception as e:
            t.RollBack()
            NOTIFICATION.messenger("Error assigning template: {}".format(str(e)))
            return False
    
    @ERROR_HANDLE.try_catch_error()
    def preserve_selection(self, current_id, view_items):
        """
        Find and restore the previously selected item
        
        Args:
            current_id: ID of currently selected item
            view_items: List of ViewItem objects
            
        Returns:
            ViewItem or None: The matching item, if found
        """
        try:
            if not current_id:
                return None
            
            for item in view_items:
                if item.Id == current_id:
                    return item
            return None
        except Exception as e:
            from EnneadTab import NOTIFICATION # pyright: ignore
            NOTIFICATION.messenger("Error preserving selection: {}".format(str(e)))
            return None
    
    @ERROR_HANDLE.try_catch_error()
    def update_new_views(self):
        """Update the list of new views in the document"""
        try:
            # Skip refresh if user is interacting with the UI
            if self.is_interacting:
                return
            
            new_views = self.get_new_views(self.doc)
            
            if new_views:
                # Store currently selected view ID to preserve selection after refresh
                selected_id = None
                selected_item = self.views_data_grid.SelectedItem
                if selected_item:
                    selected_id = selected_item.Id
                    
                # Create view items
                view_items = [self.ViewItem(view, self.doc, self) for view in new_views]
                
                # Update the grid
                self.views_data_grid.ItemsSource = view_items
                
                # Restore selection if possible
                selected_item = self.preserve_selection(selected_id, view_items)
                if selected_item:
                    self.views_data_grid.SelectedItem = selected_item
                    
                # Update status text
                self.status_text.Text = "Found {} new view(s)".format(len(view_items))
            else:
                self.views_data_grid.ItemsSource = []
                self.status_text.Text = "No new views found"
        except Exception as e:
            from EnneadTab import NOTIFICATION # pyright: ignore
            NOTIFICATION.messenger("Error updating view list: {}".format(str(e)))
    
    @ERROR_HANDLE.try_catch_error()
    def get_default_new_name(self, view_item):
        """
        Generate default name for the view based on active view + view type
        
        Args:
            view_item: The ViewItem to rename
            
        Returns:
            str: The suggested new name
        """
        # Explicitly import required modules
        from Autodesk.Revit import DB # pyright: ignore
        from EnneadTab.REVIT import REVIT_APPLICATION # pyright: ignore
        
        try:
            # Get the active view name
            active_view = REVIT_APPLICATION.get_uidoc().ActiveView
            if active_view:
                active_name = active_view.Name
                return "{} - {}".format(active_name, view_item.ViewType)
            else:
                return "{} - New".format(view_item.Name)
        except Exception as e:
            from EnneadTab import NOTIFICATION # pyright: ignore
            NOTIFICATION.messenger("Error generating default name: {}".format(str(e)))
            return view_item.Name
    
    def show_rename_dialog(self, view_item):
        """
        Display dialog for user to enter a new name
        
        Args:
            view_item: The ViewItem to rename
            
        Returns:
            tuple: (bool, string) - Success flag and new name
        """
        # Explicitly import required modules for this method
        import clr # pyright: ignore
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import DialogResult # pyright: ignore
        
        default_name = self.get_default_new_name(view_item)
        
        input_form = self.TextInputForm(
            "Rename View", 
            "Enter new name for view:", 
            default_name
        )
        
        result = input_form.ShowDialog()
        if result == DialogResult.OK and input_form.textbox.Text:
            new_name = input_form.textbox.Text
            if new_name != view_item.Name:
                return True, new_name
        return False, None
    
    @ERROR_HANDLE.try_catch_error()
    def refresh_click(self, sender, args):
        """Manual refresh button handler"""
        self.update_new_views()
    
    @ERROR_HANDLE.try_catch_error
    def rename_view_double_click(self, sender, args):
        """
        Handle double-click on a view name to rename it
        
        Args:
            sender: The sender of the event
            args: Event arguments
            
        Returns:
            None
        """
        selected_view_item = self.views_data_grid.SelectedItem
        if not selected_view_item:
            return
            
        should_rename, new_name = self.show_rename_dialog(selected_view_item)
        if should_rename:
            handler, ext_event = self.get_handler_event_by_keyword("rename_view")
            handler.args = selected_view_item.view, new_name
            ext_event.Raise()
            
            # Force update after renaming, regardless of interaction state
            was_interacting = self.is_interacting
            self.is_interacting = False  # Temporarily allow refresh
            self.update_new_views()
            self.is_interacting = was_interacting  # Restore previous state
    
    @ERROR_HANDLE.try_catch_error
    def sheet_selection_changed(self, sender, args):
        """
        Event handler for sheet selection changed
        Updates the sheet_text and triggers view placement if auto_place is enabled
        
        Args:
            sender: The sender of the event
            args: Event arguments
            
        Returns:
            None
        """
        self.update_sheet_text()
        
        # Auto place if enabled
        if self.auto_place and self.current_sheet_id:
            self.place_view_on_sheet()
    
    @ERROR_HANDLE.try_catch_error
    def make_view_name(self, current_view_name):
        """
        Creates a new view name by adding a suffix or incrementing the existing suffix
        
        Args:
            current_view_name: The current name of the view
        
        Returns:
            str: A new unique view name
        """
        try:
            # If the view name doesn't exist, return it as is
            if current_view_name not in self.all_view_names:
                return current_view_name
            
            # Check if the name ends with a numeric suffix in brackets
            match = re.search(r'(.*)\((\d+)\)$', current_view_name)
            if match:
                base_name = match.group(1)
                number = int(match.group(2)) + 1
                new_name = "{}({})".format(base_name, number)
            else:
                # If no numeric suffix, add (2)
                new_name = "{}(2)".format(current_view_name)
            
            # Ensure the new name is unique by incrementing if necessary
            while new_name in self.all_view_names:
                match = re.search(r'(.*)\((\d+)\)$', new_name)
                if match:
                    base_name = match.group(1)
                    number = int(match.group(2)) + 1
                    new_name = "{}({})".format(base_name, number)
            
            return new_name
        except Exception as e:
            NOTIFICATION.messenger("Error creating view name: {}".format(str(e)))
            # In case of error, add a unique timestamp
            return "{} (Copy-{})".format(current_view_name, int(time.time()) % 10000)
    
    @ERROR_HANDLE.try_catch_error()
    def scopebox_selection_changed(self, sender, args):
        """Handle selection change in the scope box dropdown"""
        # Get the view item from the ComboBox's Tag
        view_item = sender.Tag
        scope_box_item = sender.SelectedItem
        
        if view_item and scope_box_item:
            handler, ext_event = self.get_handler_event_by_keyword("assign_scope_box")
            handler.args = view_item.view, scope_box_item
            ext_event.Raise()
            
            # Update the view item
            view_item.SelectedScopeBox = scope_box_item
    
    @ERROR_HANDLE.try_catch_error()
    def template_selection_changed(self, sender, args):
        """Handle selection change in the view template dropdown"""
        # Get the view item from the ComboBox's Tag
        view_item = sender.Tag
        template_item = sender.SelectedItem
        
        if view_item and template_item:
            handler, ext_event = self.get_handler_event_by_keyword("assign_view_template")
            handler.args = view_item.view, template_item
            ext_event.Raise()
            
            # Update the view item
            view_item.SelectedViewTemplate = template_item
    
    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, args):
        """Close button click handler"""
        # Stop the auto-updater before closing
        self.updater.stop()
        self.Close()
    
    def mouse_down_main_panel(self, sender, args):
        """Allow dragging the window"""
        sender.DragMove()
    
    @ERROR_HANDLE.try_catch_error()
    def datagrid_mouse_enter(self, sender, args):
        """Pause auto-refresh when mouse enters the DataGrid"""
        self.is_interacting = True
        self.status_text.Text = "Auto-refresh paused. Click Manual Refresh if needed."
    
    @ERROR_HANDLE.try_catch_error()
    def datagrid_mouse_leave(self, sender, args):
        """Resume auto-refresh when mouse leaves the DataGrid"""
        self.is_interacting = False
        self.status_text.Text = "Auto-refresh resumed."


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def place_views_on_sheets(doc):
    """Monitor and manage new views in the project"""
    try:
        # Store current views in the project
        save_current_view_state(doc)
        
        # Launch the modeless form
        form = ViewsMonitorForm()
        return form
    except Exception as e:
        from EnneadTab import NOTIFICATION # pyright: ignore
        NOTIFICATION.messenger("Error starting view monitor: {}".format(str(e)))
        return None


################## main code below #####################
if __name__ == "__main__":
    place_views_on_sheets(DOC)







