#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Convert recent Rhino2Revit output jobs into Revit families and load them into the project.

This tool processes all recent output jobs from Rhino2Revit in Rhino and:
1. Creates new generic families from template
2. Converts job files to Revit elements using filename as subcategory
3. Saves families to temp location and loads into main project
4. Moves newly loaded families to origin point


"""
__title__ = "BigRhino2Revit(For Large Batch)"
__tip__ = ["Process multiple Rhino2Revit output files at once",
           "Creates families from template and loads into project",
           "Automatically moves families to origin"]
__is_popular__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from pyrevit import script
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION, FOLDER, TIME, ENVIRONMENT, UI, SAMPLE_FILE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS, REVIT_UNIT, REVIT_FAMILY, REVIT_MATERIAL, REVIT_CATEGORY
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit.revit import ErrorSwallower # pyright: ignore 
import clr # pyright: ignore 
import os
import time
import traceback
import re

UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()


def get_recent_output_files():
    """Get all recent output files from Rhino2Revit."""
    recent_out_data = DATA_FILE.get_data("rhino2revit_out_paths")
    files = []
    if recent_out_data:
        if recent_out_data.get("3dm_out_paths"):
            for path in recent_out_data["3dm_out_paths"]:
                if os.path.exists(path):
                    files.append(path)
        if recent_out_data.get("dwg_out_paths"):
            for path in recent_out_data["dwg_out_paths"]:
                if os.path.exists(path):
                    files.append(path)
    return files


def create_family_from_template():
    """Create a new family document from template."""
    try:
        template_path = SAMPLE_FILE.get_file("GM_Blank.rfa")
        
        with ErrorSwallower() as swallower:
            family_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(template_path)
            
            # Check for swallowed errors
            errors = swallower.get_swallowed_errors()
            if errors:
                print("Warnings/errors swallowed during template opening: {}".format(errors))
                
        return family_doc
    except Exception as e:
        NOTIFICATION.messenger("Failed to create family from template: {}".format(str(e)))
        return None


def sanitize_revit_name(name):
    """Remove all prohibited characters from a name for use in Revit subcategories/materials, and replace '.' with '_'."""
    original_name = name
    name = name.replace('.', '_')
    # Remove all forbidden characters for Revit names
    # Based on Revit error message: "{, }, [, ], |, ;, less-than sign, greater-than sign, ?, `, ~"
    # Also including other common problematic characters: \, :, <, >
    prohibited = r'[\\:\{\}\[\]\|;<>\?`~]'
    cleaned_name = re.sub(prohibited, '', name)
    
    # Debug logging if name was changed
    if cleaned_name != name:
        print("Sanitized name '{}' -> '{}'".format(original_name, cleaned_name))
    
    return cleaned_name


def convert_file_to_family_elements(family_doc, file_path, log_messages):
    """Convert file to Revit elements in family document."""
    file_name = FOLDER.get_file_name_from_path(file_path)
    file_name_naked = os.path.splitext(file_name)[0]
    safe_name = sanitize_revit_name(file_name_naked)
    extension = FOLDER.get_file_extension_from_path(file_path).lower()
    
    print("Processing file: '{}' -> subcategory name: '{}'".format(file_name, safe_name))
    
    converted_elements = []
    
    if extension == ".3dm":
        # Convert 3dm file using ShapeImporter
        try:
            with ErrorSwallower() as swallower:
                geos = DB.ShapeImporter().Convert(family_doc, file_path)
                geo_count = 0
                for geo in geos:
                    try:
                        converted_elements.append(DB.FreeFormElement.Create(family_doc, geo))
                        geo_count += 1
                    except Exception as e:
                        log_messages.append("Cannot import this part of file, skipping: {}".format(geo))
                
                # Check for swallowed errors
                errors = swallower.get_swallowed_errors()
                if errors:
                    log_messages.append("Warnings/errors swallowed during 3dm import: {}".format(errors))
                    
        except Exception as e:
            log_messages.append("Failed to convert 3dm file: {}".format(str(e)))
            
    elif extension == ".dwg":
        # Convert DWG file
        try:
            # Capture existing import object styles before import
            existing_import_OSTs = get_current_import_object_styles(family_doc)
            
            with ErrorSwallower() as swallower:
                options = DB.DWGImportOptions()
                cad_import_id = clr.StrongBox[DB.ElementId]()
                
                # Import CAD file and check for success
                if not family_doc.Import(file_path, options, family_doc.ActiveView, cad_import_id):
                    log_messages.append("Failed to import DWG file. It might be empty, contain unsupported geometry, or be corrupt. File: {}".format(file_path))
                    return []

                if cad_import_id.Value == DB.ElementId.InvalidElementId:
                    log_messages.append("Imported DWG has an invalid ID, indicating a problem with the import. File: {}".format(file_path))
                    return []

                cad_import = family_doc.GetElement(cad_import_id.Value)
                if not cad_import:
                    log_messages.append("Could not retrieve the imported DWG instance from the document. File: {}".format(file_path))
                    return []

                # Get geometry from CAD import
                try:
                    geo_elem = cad_import.get_Geometry(DB.Options())
                    geo_elements = []
                    for geo in geo_elem:
                        if isinstance(geo, DB.GeometryInstance):
                            geo_elements.extend([x for x in geo.GetSymbolGeometry()])
                except Exception as geo_error:
                    log_messages.append("Failed to extract geometry from CAD import: {}".format(str(geo_error)))
                    geo_elements = []
                
                # Convert solids to FreeForm elements
                solid_count = 0
                for gel in geo_elements:
                    if isinstance(gel, DB.Solid):
                        try:
                            converted_elements.append(DB.FreeFormElement.Create(family_doc, gel))
                            solid_count += 1
                        except Exception as e:
                            log_messages.append("Cannot convert solid from file '{}': {}".format(file_path, str(e)))
                
                # Delete the CAD import
                try:
                    # Validate the element still exists before attempting to delete
                    if cad_import and cad_import.Id != DB.ElementId.InvalidElementId and family_doc.GetElement(cad_import.Id):
                        # Unpin the element first if it's pinned
                        cad_import.Pinned = False
                        # print("Unpinned CAD import element before deletion")
                        
                        # Now delete the element
                        family_doc.Delete(cad_import.Id)
                        # print("Successfully deleted CAD import element")
                    else:
                        log_messages.append("CAD import element no longer exists or has invalid ID, skipping deletion")
                except Exception as delete_error:
                    log_messages.append("Warning: Could not delete CAD import element: {}".format(str(delete_error)))
                    # Continue processing even if deletion fails
                
                # Check for swallowed errors
                errors = swallower.get_swallowed_errors()
                if errors:
                    log_messages.append("Warnings/errors swallowed during DWG import: {}".format(errors))
            
            # --- CLEANUP MUST HAPPEN HERE, WHILE DOCUMENT IS STILL OPEN ---
            try:
                clean_import_object_style(family_doc, existing_import_OSTs)
            except Exception as cleanup_error:
                log_messages.append("Warning: Failed to clean up imported object styles: {}".format(str(cleanup_error)))
            # --- END CLEANUP ---
            
        except Exception as e:
            error_message = str(e)
            if "Index was out of range" in error_message:
                error_message += "\nThis might be due to an empty or invalid DWG file."
            elif "ElementId cannot be deleted" in error_message:
                error_message += "\nThis might be due to the CAD import element being invalid or already deleted."
            log_messages.append("Failed to convert DWG file '{}'.\nError: {}".format(file_path, error_message))
            log_messages.append(traceback.format_exc())
    
    # Assign subcategory to converted elements
    print("Creating subcategory with material for: '{}'".format(safe_name))
    subC = REVIT_CATEGORY.get_or_create_subcategory_with_material(family_doc, safe_name)
    if subC:
        for element in converted_elements:
            try:
                element.Subcategory = subC
            except Exception as e:
                log_messages.append("Cannot assign subcategory: {}".format(str(e)))
    
    return converted_elements





def get_current_import_object_styles(family_doc):
    """Get current import object styles from family document."""
    categories = family_doc.Settings.Categories
    import_OSTs = filter(lambda x: "Imports in Families" in x.Name, categories)
    if len(import_OSTs) == 0:
        return []
    import_OSTs = list(import_OSTs[0].SubCategories)
    return import_OSTs


def clean_import_object_style(family_doc, existing_OSTs):
    """Remove imported object styles that weren't there before import."""
    import_OSTs = get_current_import_object_styles(family_doc)

    for import_OST in import_OSTs:
        if not import_OST or not hasattr(import_OST, 'Id'):
            # Silently skip NULL or invalid import object styles
            continue
        if import_OST not in existing_OSTs:
            try:
                family_doc.Delete(import_OST.Id)
                # Silently skip or log as needed
            except Exception:
                # Silently skip any deletion errors
                continue


def save_and_load_family(family_doc, file_path, temp_folder, log_messages):
    """Save family to temp location and load into main project."""
    file_name = FOLDER.get_file_name_from_path(file_path)
    file_name_naked = os.path.splitext(file_name)[0]
    safe_name = sanitize_revit_name(file_name_naked)
    
    # Check if family already exists in project
    existing_family = REVIT_FAMILY.get_family_by_name(safe_name, DOC)
    if existing_family:
        log_messages.append("Family '{}' already exists in project - will override with new version".format(safe_name))
    
    # Create temp folder if it doesn't exist
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    # Save family to temp location
    family_path = os.path.join(temp_folder, "{}.rfa".format(file_name_naked))
    
    try:
        # Save family document
        options = DB.SaveAsOptions()
        options.OverwriteExistingFile = True
        family_doc.SaveAs(family_path, options)
        
        # Load family into main project using EnneadTab pattern
        with ErrorSwallower() as swallower:
            REVIT_FAMILY.load_family(family_doc, DOC)
            
            # Check for swallowed errors
            errors = swallower.get_swallowed_errors()
            if errors:
                log_messages.append("Warnings/errors swallowed during family loading: {}".format(errors))
        
        # Close family document
        family_doc.Close(False)
        
        if existing_family:
            log_messages.append("Successfully overrode existing family '{}'".format(safe_name))
        else:
            log_messages.append("Successfully loaded new family '{}'".format(safe_name))
        
        return family_path
        
    except Exception as e:
        log_messages.append("Failed to save/load family: {}".format(str(e)))
        try:
            family_doc.Close(False)
        except:
            pass
        return None


def move_family_to_origin(family_symbol, log_messages):
    """Move family instance to origin point."""
    try:
        # Get levels for hosting
        levels = DB.FilteredElementCollector(DOC).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()
        if not levels:
            log_messages.append("No levels found in project")
            return None
        
        # Use the first level (usually ground level)
        level = levels[0]
        
        # Activate family symbol if needed
        if not family_symbol.IsActive:
            family_symbol.Activate()
        
        # Create family instance at origin
        with ErrorSwallower() as swallower:
            instance = DOC.Create.NewFamilyInstance(
                DB.XYZ(0, 0, 0),
                family_symbol,
                level,
                DB.Structure.StructuralType.NonStructural
            )
            
            # Check for swallowed errors
            errors = swallower.get_swallowed_errors()
            if errors:
                log_messages.append("Warnings/errors swallowed during family instance creation: {}".format(errors))
        
        # Adjust elevation if level is not at 0
        if level.Elevation != 0:
            offset = level.Elevation
            for para_name in ["Elevation from Level", "Offset from Host"]:
                para = instance.LookupParameter(para_name)
                if para:
                    para.Set(-offset)
                    break
        
        return instance
        
    except Exception as e:
        log_messages.append("Failed to move family to origin: {}".format(str(e)))
        return None


def process_single_file(file_path, temp_folder, log_messages):
    """Process a single file and return success status."""
    family_doc = None
    try:
        file_name = FOLDER.get_file_name_from_path(file_path)
        log_messages.append("\n\nProcessing: {}".format(file_name))
        
        # Create family from template
        family_doc = create_family_from_template()
        if not family_doc:
            log_messages.append("Failed to create family document for: {}".format(file_name))
            return False
        
        # Convert file to family elements
        t = DB.Transaction(family_doc, "Convert file to family elements")
        t.Start()
        converted_elements = convert_file_to_family_elements(family_doc, file_path, log_messages)
        t.Commit()
        
        if not converted_elements:
            log_messages.append("No elements converted from: {}".format(file_name))
            if family_doc:
                try:
                    family_doc.Close(False)
                except:
                    pass
            return False
        
        # Save and load family
        family_path = save_and_load_family(family_doc, file_path, temp_folder, log_messages)
        if not family_path:
            log_messages.append("Failed to save/load family for: {}".format(file_name))
            return False

        # Find the loaded family symbol
        family_symbols = DB.FilteredElementCollector(DOC).OfClass(DB.FamilySymbol).ToElements()
        target_symbol = None
        file_name_naked = os.path.splitext(file_name)[0]
        safe_name = sanitize_revit_name(file_name_naked)
        
        for symbol in family_symbols:
            if symbol.Family.Name == safe_name:
                target_symbol = symbol
                break
        
        if not target_symbol:
            log_messages.append("Could not find loaded family symbol for: {}".format(file_name))
            return False
        
        # Move family to origin
        t_main = DB.Transaction(DOC, "Place family instance for {}".format(safe_name))
        t_main.Start()
        instance = move_family_to_origin(target_symbol, log_messages)
        success = instance is not None
        t_main.Commit()
        
        return success
            
    except Exception as e:
        log_messages.append("Error processing {}: {}".format(file_path, str(e)))
        log_messages.append(traceback.format_exc())
        return False
    finally:
        # Ensure family document is closed even if there's an error
        if family_doc:
            try:
                family_doc.Close(False)
            except:
                pass


def label_func(file_path):
    """Generate label for progress bar showing current file being processed."""
    file_name = FOLDER.get_file_name_from_path(file_path)
    return "Processing: {}".format(file_name)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def bigrhino2revit(doc):
    """Main function to process recent Rhino2Revit output files."""
    log_messages = []  # Collect all log messages here
    
    # Check if we're in project document
    if doc.IsFamilyDocument:
        log_messages.append("This tool must be used in project environment, not family environment")
        NOTIFICATION.messenger("This tool must be used in project environment, not family environment")
        REVIT_FORMS.notification(
            main_text="Must be in project environment",
            sub_text="This tool creates families and loads them into the project. It cannot be used in family environment.",
            window_title="EnneadTab",
            button_name="Close",
            self_destruct=5
        )
        print("\n".join(log_messages))
        return
    
    # Get recent output files
    recent_files = get_recent_output_files()
    if not recent_files:
        log_messages.append("No recent Rhino2Revit output files found")
        NOTIFICATION.messenger("No recent Rhino2Revit output files found")
        print("\n".join(log_messages))
        return
    
    # Debug: Show material mapping data
    recent_out_data = DATA_FILE.get_data("rhino2revit_out_paths")
    if recent_out_data and recent_out_data.get("layer_material_mapping"):
        print("Available material mapping keys:")
        for key in recent_out_data["layer_material_mapping"].keys():
            print("  - '{}'".format(key))
    else:
        print("No material mapping data found")
    
    # Temp folder for saving families
    temp_folder = ENVIRONMENT.PUBLIC_TEMP_FOLDER
    
    # Process files with progress bar
    tool_start_time = time.time()
    
    # Create a class to handle progress tracking (avoids nonlocal issues in IronPython)
    class ProgressTracker:
        def __init__(self):
            self.processed_count = 0
            self.failed_count = 0
        
        def process_file(self, file_path):
            success = process_single_file(file_path, temp_folder, log_messages)
            if success:
                self.processed_count += 1
            else:
                self.failed_count += 1
    
    tracker = ProgressTracker()
    
    # Use progress bar to process files
    with ErrorSwallower() as swallower:
        UI.progress_bar(
            items=recent_files,
            func=tracker.process_file,
            label_func=label_func,
            title="BigRhino2Revit - Processing Files"
        )
        
        # Check for any swallowed errors from the overall process
        errors = swallower.get_swallowed_errors()
        if errors:
            log_messages.append("Warnings/errors swallowed during overall process: {}".format(errors))
    
    # Final notification
    tool_time_span = time.time() - tool_start_time
    REVIT_FORMS.notification(
        main_text="Bigrhino2Revit Finished",
        sub_text="Processed: {} files\nFailed: {} files\nTotal time: {}".format(tracker.processed_count, tracker.failed_count, TIME.get_readable_time(tool_time_span)),
        window_title="EnneadTab",
        button_name="Close",
        self_destruct=10
    )

    
    output = script.get_output()
    output.close_others(True)
    
    # Print all log messages at the end
    print("\n".join(log_messages))


################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others(True)
    bigrhino2revit(DOC)






