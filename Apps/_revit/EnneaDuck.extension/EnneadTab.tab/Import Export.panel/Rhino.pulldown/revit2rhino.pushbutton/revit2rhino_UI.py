#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
UI module for Revit2Rhino export tool.
Provides interface for selecting export options and launching the export process.
"""

import os
import sys
import clr
import logging
import traceback
from pyrevit import forms, script
from pyrevit.framework import wpf, Windows, Media
import System

from EnneadTab import ENVIRONMENT, NOTIFICATION
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from Autodesk.Revit import DB  # pyright: ignore

# Local import for export action
import revit2rhino_action

# Get reference to logger from script module
import revit2rhino_script
logger = revit2rhino_script.logger

# Get the path to the current directory
DIR_PATH = os.path.dirname(__file__)

# Get document references
DOC = REVIT_APPLICATION.get_doc()

def get_family_instances_from_view(include_links=False):
    """
    Get family instances from the current view with option to include linked models.
    
    Args:
        include_links (bool): Whether to include elements from linked models
        
    Returns:
        tuple: (list of all instances, dictionary of instances by family name)
    """
    doc = DOC
    
    # Collect family instances from current view
    logger.info("Collecting family instances from current view...")
    all_family_instances = (
        DB.FilteredElementCollector(doc, doc.ActiveView.Id)
        .OfClass(DB.FamilyInstance)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    
    # If requested, also collect from linked models
    if include_links:
        logger.info("Including elements from linked documents...")
        linked_docs = []
        
        # Find linked documents
        linkInstances = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).ToElements()
        logger.debug("Found {} link instances in the document".format(len(list(linkInstances))))
        
        for linkInstance in linkInstances:
            if linkInstance.GetLinkDocument():
                linked_docs.append(linkInstance)
        
        logger.debug("Found {} linked documents with available content".format(len(linked_docs)))
        
        # Collect instances from each linked document
        for linkInstance in linked_docs:
            link_doc = linkInstance.GetLinkDocument()
            if not link_doc:
                continue
                
            # Skip if the link instance itself is not visible in the view
            # Use IsHidden property on View to check link visibility
            view_state = doc.ActiveView.GetLinkVisibility(linkInstance.Id)
            if view_state == DB.ViewVisibility.Hidden:
                logger.debug("Link '{}' is not visible in active view, skipping...".format(link_doc.Title))
                continue
                
            logger.debug("Processing linked document: {}".format(link_doc.Title))
            link_transform = linkInstance.GetTransform()
            
            # Use collector without viewId for linked documents
            linked_instances = (
                DB.FilteredElementCollector(link_doc)
                .OfClass(DB.FamilyInstance)
                .WhereElementIsNotElementType()
                .ToElements()
            )
            
            linked_instances_list = list(linked_instances)
            logger.debug("Found {} family instances in linked document".format(len(linked_instances_list)))
            
            # Store link info with the element for later processing
            count = 0
            for linked_element in linked_instances_list:
                # No need to check individual element visibility here
                # as we already confirmed the link is visible
                linked_element.link_transform = link_transform
                linked_element.link_doc = link_doc
                all_family_instances.append(linked_element)
                count += 1
            
            logger.debug("Added {} elements from linked document '{}'".format(count, link_doc.Title))
    
    # Organize by family
    family_dict = {}
    for instance in all_family_instances:
        try:
            # Handle both regular and linked elements
            if hasattr(instance, 'link_doc'):
                # This is from a linked model
                family_name = instance.Symbol.FamilyName + " (Linked)"
            else:
                family_name = instance.Symbol.FamilyName
                
            if family_name not in family_dict:
                family_dict[family_name] = []
            family_dict[family_name].append(instance)
        except:
            pass
    
    return all_family_instances, family_dict


class Revit2RhinoUI(forms.WPFWindow):
    """WPF UI window for the Revit2Rhino export tool."""
    
    def __init__(self):
        """Initialize the window."""
        self.xaml_source = os.path.join(DIR_PATH, 'revit2rhino_UI.xaml')
        
        # Load the xaml file
        wpf.LoadComponent(self, self.xaml_source)
        
        # Set the logo - using multiple approaches with robust error handling
        self.load_logo()
        
        # Set window title
        self.Title = "EnneadTab Revit2Rhino"
        
        # Initialize variables
        self.selected_families = None
        self.selected_instances = None
        self.all_instances = None
        self.families_dict = None
    
    def load_logo(self):
        """Load the logo image with a simple approach."""
        try:
            # Look for logo in standard locations
            logo_paths = [
                # Try the script directory
                os.path.join(DIR_PATH, "logo_vertical_light.png"),
                # Check if ENVIRONMENT has IMAGE_FOLDER
                os.path.join(ENVIRONMENT.IMAGE_FOLDER, "logo_vertical_light.png") if hasattr(ENVIRONMENT, 'IMAGE_FOLDER') else None,
                # Check in lib/images folder
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(DIR_PATH))))),
                    "lib", "images", "logo_vertical_light.png"
                )
            ]
            
            # Filter out None values
            logo_paths = [path for path in logo_paths if path]
            
            # Try to load the first logo file that exists
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    bitmap = Media.Imaging.BitmapImage(System.Uri(logo_path))
                    self.logo_img.Source = bitmap
                    logger.debug("Successfully loaded logo from {}".format(logo_path))
                    return
                
            # If no logo found, hide the logo space
            self.logo_img.Visibility = Windows.Visibility.Collapsed
            logger.debug("Logo not found in any location, hiding the logo space")
        except Exception as e:
            # If anything fails, just hide the logo
            self.logo_img.Visibility = Windows.Visibility.Collapsed
            logger.debug("Error loading logo: {}".format(e))
    
    def mouse_down_main_panel(self, sender, args):
        """Allow dragging the window by clicking anywhere on it."""
        self.DragMove()
    
    def select_families_click(self, sender, args):
        """Handle Select Families button click."""
        # Call the function to collect and select families
        try:
            # Get all family instances from the current view
            self.all_instances, self.families_dict = get_family_instances_from_view(
                include_links=self.include_linked_elements_checkbox.IsChecked
            )
            
            if not self.families_dict:
                NOTIFICATION.messenger("No family instances found in the current view")
                return
            
            # Show family selection dialog
            family_names = sorted(list(self.families_dict.keys()))
            self.selected_families = forms.SelectFromList.show(
                family_names,
                multiselect=True,
                title="Select Families to Export",
                button_name="Export Selected Families"
            )
            
            if not self.selected_families:
                self.selection_info.Text = "No families selected for export."
                self.export_button.IsEnabled = False
                return
            
            # Collect selected instances
            self.selected_instances = []
            for family_name in self.selected_families:
                self.selected_instances.extend(self.families_dict[family_name])
            
            # Update UI
            self.selection_info.Text = "Selected {} instances from {} families.".format(
                len(self.selected_instances), 
                len(self.selected_families)
            )
            self.export_button.IsEnabled = True
            
        except Exception as e:
            print (traceback.format_exc())
            NOTIFICATION.messenger("Error selecting families: {}".format(str(e)))
            self.selection_info.Text = "Error occurred while selecting families."
            self.export_button.IsEnabled = False
    
    def export_click(self, sender, args):
        """Handle Export to Rhino button click."""
        try:
            if not self.selected_instances:
                NOTIFICATION.messenger("No elements selected for export")
                return
            
            # Check if this is a large export (more than 10000 elements)
            total_count = len(self.selected_instances)
            if total_count > 10000:
                # Show warning dialog for large exports
                options = ["Yes, proceed with export", "No, cancel export"]
                result = REVIT_FORMS.dialogue(
                    title="Large Export Warning",
                    main_text="You are about to export {} elements.".format(total_count),
                    sub_text="This operation may take a while to complete. Do you want to continue?",
                    options=options,
                    icon="warning"
                )
                
                if result == options[1]:
                    NOTIFICATION.messenger("Export canceled by user")
                    self.Close()
                    return
            
            # Execute the export with selected options
            preserve_family_layers = self.preserve_family_layer_checkbox.IsChecked
            
            # Show notification about EA_PackageBlockLayer if preserve family layers is checked
            if preserve_family_layers:
                # First close this window to prevent UI overlap
                self.Close()
                
                # Show dialog about using EA_PackageBlockLayer
                REVIT_FORMS.dialogue(
                    title="Layer Package Recommendation",
                    main_text="You've selected 'Preserve Family Layer'.",
                    sub_text="For best results with preserved family layers, please use 'EA_PackageBlockLayer' in EnneadTab for Rhino after export.",
                    options=["OK"],
                    icon="info"
                )
            else:
                # Close the window
                self.Close()
            
            # Call the export function from the action module
            revit2rhino_action.export_elements_to_rhino(
                self.selected_instances,
                preserve_family_layers=preserve_family_layers
            )
            
        except Exception as e:
            NOTIFICATION.messenger("Error during export: {}".format(str(e)))
    
    def close_click(self, sender, args):
        """Handle Close button click."""
        self.Close()


def show_dialog():
    """Show the Revit2Rhino UI dialog."""
    dlg = Revit2RhinoUI()
    return dlg.ShowDialog() 