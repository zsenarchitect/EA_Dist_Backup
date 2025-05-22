#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
UI module for Revit2Rhino export tool.
Provides a modern, category-based interface for selecting and exporting Revit elements to Rhino.
"""

import os   
import traceback
from pyrevit import forms
from pyrevit.framework import wpf, Windows, Media
import System
from EnneadTab import ENVIRONMENT, NOTIFICATION, ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB  # pyright: ignore
import revit2rhino_action
import revit2rhino_script

logger = revit2rhino_script.logger
DIR_PATH = os.path.dirname(__file__)

CATEGORY_CHECKBOX_MAP = {
    "curtain_wall_panels_checkbox": DB.BuiltInCategory.OST_CurtainWallPanels,
    "curtain_wall_mullions_checkbox": DB.BuiltInCategory.OST_CurtainWallMullions,
    "walls_checkbox": DB.BuiltInCategory.OST_Walls,
    "windows_checkbox": DB.BuiltInCategory.OST_Windows,
    "doors_checkbox": DB.BuiltInCategory.OST_Doors,
    "floors_checkbox": DB.BuiltInCategory.OST_Floors,
    "roofs_checkbox": DB.BuiltInCategory.OST_Roofs,
    "ceilings_checkbox": DB.BuiltInCategory.OST_Ceilings,
    "stairs_checkbox": DB.BuiltInCategory.OST_Stairs,
    "stair_railings_checkbox": DB.BuiltInCategory.OST_StairsRailing,
    "furniture_checkbox": DB.BuiltInCategory.OST_Furniture,
    "generic_model_checkbox": DB.BuiltInCategory.OST_GenericModel,
    "columns_checkbox": DB.BuiltInCategory.OST_Columns,
    "fixtures_checkbox": DB.BuiltInCategory.OST_PlumbingFixtures,
    "railings_checkbox": DB.BuiltInCategory.OST_Railings,
    "ramps_checkbox": DB.BuiltInCategory.OST_Ramps,
    "massing_checkbox": DB.BuiltInCategory.OST_Mass,
    "model_text_checkbox": DB.BuiltInCategory.OST_ModelText,
}



def get_elements_by_category(doc, category):
    """Collect elements of a given BuiltInCategory from the active view."""
    collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(category).WhereElementIsNotElementType().ToElements()
    return list(collector)

class Revit2RhinoUI(forms.WPFWindow):
    """WPF UI window for the Revit2Rhino export tool."""
    def __init__(self, doc):
        self.doc = doc
        self.xaml_source = os.path.join(DIR_PATH, 'revit2rhino_UI.xaml')
        wpf.LoadComponent(self, self.xaml_source)
        self._load_logo()
        self.Title = "EnneadTab Revit2Rhino"
        self.selected_instances = None

    def _load_logo(self):
        """Load the logo image if available."""
        try:
            logo_paths = [
                os.path.join(DIR_PATH, "logo_vertical_light.png"),
                os.path.join(ENVIRONMENT.IMAGE_FOLDER, "logo_vertical_light.png") if hasattr(ENVIRONMENT, 'IMAGE_FOLDER') else None,
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(DIR_PATH))))),
                    "lib", "images", "logo_vertical_light.png"
                )
            ]
            logo_paths = [path for path in logo_paths if path]
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    bitmap = Media.Imaging.BitmapImage(System.Uri(logo_path))
                    self.logo_img.Source = bitmap
                    logger.debug("Successfully loaded logo from {}".format(logo_path))
                    return
            self.logo_img.Visibility = Windows.Visibility.Collapsed
        except Exception:
            self.logo_img.Visibility = Windows.Visibility.Collapsed

    def mouse_down_main_panel(self, sender, args):
        self.DragMove()

    @ERROR_HANDLE.try_catch_error()
    def select_families_click(self, sender, args):
        """Handle Select Families button click."""
        
        selected_categories = [
            cat for cb, cat in CATEGORY_CHECKBOX_MAP.items()
            if getattr(self, cb).IsChecked
        ]
        if not selected_categories:
            NOTIFICATION.messenger("Please select at least one category")
            return
            
        all_elements = []
        empty_categories = []
        
        # Collect elements from each category
        for bic in selected_categories:
            try:
                elements = get_elements_by_category(self.doc, bic)
                if elements:
                    all_elements.extend(elements)
                else:
                    # Track categories with no elements
                    category_name = bic.ToString().replace("OST_", "")
                    empty_categories.append(category_name)
            except Exception as e:
                logger.debug("Error collecting elements for category {}: {}".format(bic, str(e)))
                continue
                
        if not all_elements:
            NOTIFICATION.messenger("No elements found in selected categories")
            return
            
        # Show warning if some categories had no elements
        if empty_categories:
            NOTIFICATION.messenger("Note: No elements found in these categories: {}".format(", ".join(empty_categories)))

        # Group elements by family name and type
        family_dict = {}
        for el in all_elements:
            family_name = FamilyTemplateListItem(el).name
            
            if family_name not in family_dict:
                family_dict[family_name] = []
            family_dict[family_name].append(el)
        family_names = sorted(list(family_dict.keys()))
        selected_family_names = forms.SelectFromList.show(
            family_names,
            multiselect=True,
            title="Select Families to Export",
            button_name="Export Selected Families"
        )

        if not selected_family_names:
            self.selection_info.Text = "No families selected for export."
            self.export_button.IsEnabled = False
            return
       
        self.selected_instances = []
        for family_name in selected_family_names:
            self.selected_instances.extend(family_dict[family_name])
        self.selection_info.Text = "Selected {} unique families.".format(len(self.selected_instances))
        self.export_button.IsEnabled = True
        

    @ERROR_HANDLE.try_catch_error()
    def export_click(self, sender, args):
        """Handle Export to Rhino button click."""

        if not self.selected_instances:
            NOTIFICATION.messenger("No elements selected for export")
            return
        revit2rhino_action.export_elements_to_rhino(self.doc, self.selected_instances)


    def close_click(self, sender, args):
        self.Close()

    def check_all_btn_Click(self, sender, args):
        """Check all category checkboxes."""
        for cb_name in CATEGORY_CHECKBOX_MAP.keys():
            getattr(self, cb_name).IsChecked = True

    def check_none_btn_Click(self, sender, args):
        """Uncheck all category checkboxes."""
        for cb_name in CATEGORY_CHECKBOX_MAP.keys():
            getattr(self, cb_name).IsChecked = False

    def toggle_checked_btn_Click(self, sender, args):
        """Toggle all category checkboxes."""
        for cb_name in CATEGORY_CHECKBOX_MAP.keys():
            cb = getattr(self, cb_name)
            cb.IsChecked = not cb.IsChecked if cb.IsChecked is not None else True

class FamilyTemplateListItem(forms.TemplateListItem):
    """Display item for selection dialog, showing detailed family and type information."""
    def __init__(self, element):
        self.element = element

    @property
    def name(self):
        try:
            if hasattr(self.element, 'Symbol'):
                family = self.element.Symbol.Family
                family_name = family.Name
                type_name = self.element.Symbol.LookupParameter("Type Name").AsString()
                in_place = family.IsInPlace
                category_name = family.FamilyCategory.Name
                return "[{}]:<{}> {}".format(category_name, family_name, type_name)

            elif hasattr(self.element, 'WallType'):
                wall_type = self.element.WallType
                if hasattr(wall_type, "Kind"):
                    wall_kind = wall_type.Kind
                    if "basic" in str(wall_kind).lower():
                        wall_kind = "Basic"
                    else:
                        wall_kind = "Curtain"
                    return "[Wall {}]:{}".format(wall_kind, wall_type.LookupParameter("Type Name").AsString())
                return "[Wall In-Place]:{}".format(wall_type.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'RoofType'):
                roof_type = self.element.RoofType
                if not hasattr(roof_type, "FamilyName"):
                    return "[Roof]:{}".format(roof_type.LookupParameter("Type Name").AsString())
                
                family_name = roof_type.FamilyName
                if family_name in ["Basic Roof", "Sloped Glazing", "Fascia", "Gutter", "Roof Soffit"]:
                    roof_kind = family_name
                    if "basic" in roof_kind.lower():
                        roof_kind = "Basic"
                    if "soffit" in roof_kind.lower():
                        roof_kind = "Soffit"
                    return "[Roof {}]:{}".format(roof_kind, roof_type.LookupParameter("Type Name").AsString())
                
                try:
                    family = self._get_family_by_name(family_name)
                    if family and family.IsInPlace:
                        return "[Roof In-Place]:[{}]{}".format(family_name, roof_type.LookupParameter("Type Name").AsString())
                except Exception as e:
                    print(traceback.format_exc())
                return "[Roof]:{}".format(roof_type.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'FloorType'):
                return "[Floor]:{}".format(self.element.FloorType.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'StairsType'):
                return "[Stair]:{}".format(self.element.StairsType.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'RailingType'):
                return "[Railing]:{}".format(self.element.RailingType.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'CeilingType'):
                return "[Ceiling]:{}".format(self.element.CeilingType.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'RampType'):
                return "[Ramp]:{}".format(self.element.RampType.LookupParameter("Type Name").AsString())

            elif hasattr(self.element, 'ModelTextType'):
                return "[ModelText]:{}".format(self.element.ModelTextType.LookupParameter("Type Name").AsString())

            else:
                category_name = self.element.Category.Name if hasattr(self.element, 'Category') else 'Unknown'
                type_name = self.element.LookupParameter("Type Name").AsString() if hasattr(self.element, 'LookupParameter') else self.element.Name
                return "[{}]:{}".format(category_name, type_name)

        except Exception as e:
            print(traceback.format_exc())
            return "[Unknown]:{}".format(str(self.element))

    def _get_family_by_name(self, name):
        """Helper method to get family by name."""
        all_families = DB.FilteredElementCollector(self.element.Document).OfClass(DB.Family).ToElements()
        family = filter(lambda x: x.Name == name, all_families)
        return next(family, None) if family else None

def show_dialog():
    doc = REVIT_APPLICATION.get_doc()
    dlg = Revit2RhinoUI(doc)
    return dlg.ShowDialog()

if __name__ == "__main__":
    pass
