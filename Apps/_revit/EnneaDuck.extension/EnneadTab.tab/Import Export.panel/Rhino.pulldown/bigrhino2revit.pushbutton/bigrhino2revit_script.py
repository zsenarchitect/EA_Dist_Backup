#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Convert recent Rhino2Revit output jobs into Revit families and load them into the project.

This tool processes all recent output jobs from Rhino2Revit and:
1. Creates new generic families from template
2. Converts job files to Revit elements using filename as subcategory
3. Saves families to temp location and loads into main project
4. Moves newly loaded families to origin point

Best used after running Rhino2Revit to batch process multiple output files.
"""
__title__ = "BigRhino2Revit"
__tip__ = ["Process multiple Rhino2Revit output files at once",
           "Creates families from template and loads into project",
           "Automatically moves families to origin"]
__is_popular__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION, FOLDER, TIME, ENVIRONMENT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS, REVIT_UNIT, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 
import clr # pyright: ignore 
import os
import time
import traceback
from pyrevit.forms import ProgressBar

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


def create_family_from_template(template_path, family_name):
    """Create a new family document from template."""
    try:
        # Create new family document from template
        family_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(template_path)
        return family_doc
    except Exception as e:
        NOTIFICATION.messenger("Failed to create family from template: {}".format(str(e)))
        return None


def convert_file_to_family_elements(family_doc, file_path):
    """Convert file to Revit elements in family document."""
    file_name = FOLDER.get_file_name_from_path(file_path)
    file_name_naked = file_name.split(".")[0]
    extension = FOLDER.get_file_extension_from_path(file_path).lower()
    
    # Create subcategory for this file
    parent_category = family_doc.OwnerFamily.FamilyCategory
    try:
        new_subc = family_doc.Settings.Categories.NewSubcategory(parent_category, file_name_naked)
    except Exception as e:
        # Subcategory might already exist
        pass
    
    converted_elements = []
    
    if extension == ".3dm":
        # Convert 3dm file using ShapeImporter
        try:
            geos = DB.ShapeImporter().Convert(family_doc, file_path)
            for geo in geos:
                try:
                    converted_elements.append(DB.FreeFormElement.Create(family_doc, geo))
                except Exception as e:
                    print("Cannot import this part of file, skipping: {}".format(geo))
        except Exception as e:
            print("Failed to convert 3dm file: {}".format(str(e)))
            
    elif extension == ".dwg":
        # Convert DWG file
        try:
            options = DB.DWGImportOptions()
            cad_import_id = clr.StrongBox[DB.ElementId]()
            
            # Import CAD file and check for success
            if not family_doc.Import(file_path, options, family_doc.ActiveView, cad_import_id):
                print("Failed to import DWG file. It might be empty, contain unsupported geometry, or be corrupt. File: {}".format(file_path))
                return []

            if cad_import_id.Value == DB.ElementId.InvalidElementId:
                print("Imported DWG has an invalid ID, indicating a problem with the import. File: {}".format(file_path))
                return []

            cad_import = family_doc.GetElement(cad_import_id.Value)
            if not cad_import:
                print("Could not retrieve the imported DWG instance from the document. File: {}".format(file_path))
                return []

            # Get geometry from CAD import
            geo_elem = cad_import.get_Geometry(DB.Options())
            geo_elements = []
            for geo in geo_elem:
                if isinstance(geo, DB.GeometryInstance):
                    geo_elements.extend([x for x in geo.GetSymbolGeometry()])
            
            # Convert solids to FreeForm elements
            for gel in geo_elements:
                if isinstance(gel, DB.Solid):
                    try:
                        converted_elements.append(DB.FreeFormElement.Create(family_doc, gel))
                    except Exception as e:
                        print("Cannot convert solid from file '{}': {}".format(file_path, str(e)))
            
            # Delete the CAD import
            family_doc.Delete(cad_import.Id)
                
        except Exception as e:
            error_message = str(e)
            if "Index was out of range" in error_message:
                error_message += "\nThis might be due to an empty or invalid DWG file."
            print("Failed to convert DWG file '{}'.\nError: {}".format(file_path, error_message))
            traceback.print_exc()
    
    # Assign subcategory to converted elements
    subC = get_subC_by_name(family_doc, file_name_naked)
    if subC:
        for element in converted_elements:
            try:
                element.Subcategory = subC
            except Exception as e:
                print("Cannot assign subcategory: {}".format(str(e)))
    
    return converted_elements


def get_subC_by_name(family_doc, name):
    """Get subcategory by name from family document."""
    parent_category = family_doc.OwnerFamily.FamilyCategory
    subCs = parent_category.SubCategories
    for subC in subCs:
        if subC.Name == name:
            return subC
    return None


def save_and_load_family(family_doc, file_path, temp_folder):
    """Save family to temp location and load into main project."""
    file_name = FOLDER.get_file_name_from_path(file_path)
    file_name_naked = file_name.split(".")[0]
    
    # Create temp folder if it doesn't exist
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    # Save family to temp location
    family_path = os.path.join(temp_folder, "{}.rfa".format(file_name_naked))
    
    try:
        # Save family document
        family_doc.SaveAs(family_path)
        
        # Load family into main project using EnneadTab pattern
        REVIT_FAMILY.load_family(family_doc, DOC)
        
        # Close family document
        family_doc.Close(False)
        
        return family_path
        
    except Exception as e:
        print("Failed to save/load family: {}".format(str(e)))
        try:
            family_doc.Close(False)
        except:
            pass
        return None


def move_family_to_origin(family_symbol):
    """Move family instance to origin point."""
    try:
        # Get levels for hosting
        levels = DB.FilteredElementCollector(DOC).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()
        if not levels:
            NOTIFICATION.messenger("No levels found in project")
            return None
        
        # Use the first level (usually ground level)
        level = levels[0]
        
        # Activate family symbol if needed
        if not family_symbol.IsActive:
            family_symbol.Activate()
        
        # Create family instance at origin
        instance = DOC.Create.NewFamilyInstance(
            DB.XYZ(0, 0, 0),
            family_symbol,
            level,
            DB.Structure.StructuralType.NonStructural
        )
        
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
        print("Failed to move family to origin: {}".format(str(e)))
        return None


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def bigrhino2revit(doc):
    """Main function to process recent Rhino2Revit output files."""
    
    # Check if we're in project document
    if doc.IsFamilyDocument:
        NOTIFICATION.messenger("This tool must be used in project environment, not family environment")
        REVIT_FORMS.notification(
            main_text="Must be in project environment",
            sub_text="This tool creates families and loads them into the project. It cannot be used in family environment.",
            window_title="EnneadTab",
            button_name="Close",
            self_destruct=5
        )
        return
    
    # Get recent output files
    recent_files = get_recent_output_files()
    if not recent_files:
        NOTIFICATION.messenger("No recent Rhino2Revit output files found")
        return
    
    # Template path
    template_path = r"L:\4b_Applied Computing\01_Revit\02_Template\01_Imperial\EA_Family Templates_R22\Generic Model.rft"
    if not os.path.exists(template_path):
        NOTIFICATION.messenger("Template file not found: {}".format(template_path))
        return
    
    # Temp folder for saving families
    temp_folder = ENVIRONMENT.PUBLIC_TEMP_FOLDER
    
    # Process each file
    tool_start_time = time.time()
    processed_count = 0
    failed_count = 0
    
    with ProgressBar(title='BigRhino2Revit: Processing models... ({value} of {max})', step=1) as pb:
        for i, file_path in enumerate(recent_files):
            pb.update_progress(i, len(recent_files))
            try:
                file_name = FOLDER.get_file_name_from_path(file_path)
                NOTIFICATION.messenger("Processing: {}".format(file_name))
                
                # Create family from template
                family_doc = create_family_from_template(template_path, file_name)
                if not family_doc:
                    failed_count += 1
                    continue
                
                # Convert file to family elements
                t = DB.Transaction(family_doc, "Convert file to family elements")
                t.Start()
                converted_elements = convert_file_to_family_elements(family_doc, file_path)
                t.Commit()
                
                if not converted_elements:
                    print("No elements converted from: {}".format(file_name))
                    family_doc.Close(False)
                    failed_count += 1
                    continue
                
                # Save and load family
                family_path = save_and_load_family(family_doc, file_path, temp_folder)
                if not family_path:
                    failed_count += 1
                    continue
                
                # Find the loaded family symbol
                family_symbols = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
                target_symbol = None
                file_name_naked = file_name.split(".")[0]
                
                for symbol in family_symbols:
                    if symbol.Family.Name == file_name_naked:
                        target_symbol = symbol
                        break
                
                if not target_symbol:
                    print("Could not find loaded family symbol for: {}".format(file_name))
                    failed_count += 1
                    continue
                
                # Move family to origin
                t_main = DB.Transaction(doc, "Place family instance for {}".format(file_name_naked))
                t_main.Start()
                instance = move_family_to_origin(target_symbol)
                if instance:
                    processed_count += 1
                    NOTIFICATION.messenger("Successfully processed: {}".format(file_name))
                else:
                    failed_count += 1
                t_main.Commit()
                    
            except Exception as e:
                print("Error processing {}: {}".format(file_path, str(e)))
                print(traceback.format_exc())
                failed_count += 1
    
    # Final notification
    tool_time_span = time.time() - tool_start_time
    REVIT_FORMS.notification(
        main_text="Bigrhino2Revit Finished",
        sub_text="Processed: {} files\nFailed: {} files\nTotal time: {}".format(
            processed_count, failed_count, TIME.get_readable_time(tool_time_span)
        ),
        window_title="EnneadTab",
        button_name="Close",
        self_destruct=10
    )


################## main code below #####################
if __name__ == "__main__":
    bigrhino2revit(DOC)







