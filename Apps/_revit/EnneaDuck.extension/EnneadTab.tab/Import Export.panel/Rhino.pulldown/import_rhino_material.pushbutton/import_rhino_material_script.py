#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Import material definitions from Rhino into Revit. Creates new materials or updates existing ones based on Rhino material properties."
__title__ = "Import Rhino Material"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_MATERIAL, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import script, forms
UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()

def get_existing_materials(doc):
    """Get all existing materials in the document.
    
    Args:
        doc (Document): The active Revit document
        
    Returns:
        dict: Dictionary of material names to material objects
    """
    return {material.Name: material for material in DB.FilteredElementCollector(doc).OfClass(DB.Material)}

def update_material_properties(material, color_data):
    """Update material properties with color data.
    
    Args:
        material (Material): The Revit material to update
        color_data (dict): Color data from Rhino
    """
    r, g, b = color_data["diffuse"]
    material.Color = DB.Color(r, g, b)
    material.Transparency = int(color_data["transparency"] * 100)  # 0-100 range

    transparency_color_R, transparency_color_G, transparency_color_B = color_data["transparency_color"]
    material.SurfaceForegroundPatternColor = DB.Color(transparency_color_R, transparency_color_G, transparency_color_B)
    material.SurfaceForegroundPatternId = REVIT_SELECTION.get_solid_fill_pattern_id(DOC)
    
    # Scale shininess from Rhino's 0-255 range to Revit's 0-128 range
    rhino_shininess = color_data["shininess"]  # 0-255 range
    revit_shininess = int((rhino_shininess / 255.0) * 128)  # Scale to 0-128 range
    revit_shininess = max(0, min(128, revit_shininess))  # Clamp between 0 and 128
    material.Shininess = revit_shininess
    
    print("\nMaterial properties updated:\nDiffuse: {}-{}-{}, Transparency: {}, Shininess: {} (Rhino: {})".format(
        r, g, b, material.Transparency, material.Shininess, rhino_shininess))

def assign_materials_to_subcategories(doc, material_data, existing_materials):
    """Assign materials to subcategories based on Rhino data.
    
    Args:
        doc (Document): The active Revit document
        material_data (dict): Material data from Rhino
        existing_materials (dict): Dictionary of existing materials
    """

    sub_cate_to_process = []
    for category in doc.Settings.Categories:
        for sub_category in category.SubCategories:
            sub_cate_to_process.append(sub_category)
    selected_sub_cate = forms.SelectFromList.show(sub_cate_to_process, 
                                                    title="Select subcategories to process",
                                                    name_attr = "Name", 
                                                    multiselect=True,
                                                    button_name="Select Subcategories")
    if not selected_sub_cate:
        return



    
    print ("\n\nAssigning materials to subcategories\n\n")
    output = script.get_output()
    for category in doc.Settings.Categories:
        for sub_category in category.SubCategories:
            if sub_category.Name not in selected_sub_cate:
                continue
            material_name = material_data.get(sub_category.Name, {}).get("name")
            if not material_name:
                continue
                
            material = existing_materials.get(material_name)
            if material:
                output.print_md("Updating material for sub category: [**{}**], new material: [**{}**]".format(
                    sub_category.Name, material.Name))
                sub_category.Material = material



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def import_rhino_material(doc):
    """Import material definitions from Rhino into Revit.
    
    Args:
        doc (Document): The active Revit document
    """
    material_data = DATA_FILE.get_data("RHINO_MATERIAL_MAP")
    if not material_data:
        NOTIFICATION.messenger(main_text="No material data found. Please export materials from Rhino first.")
        return

    # Get existing materials before starting transaction
    existing_materials = get_existing_materials(doc)

    t = DB.Transaction(doc, __title__)
    t.Start()

    imported_material_names = []
    for _, mat_data in material_data.items():
        original_name = mat_data["name"]
        material_name = REVIT_MATERIAL.sanitize_material_name(original_name)
        if material_name != original_name:
            print("Material name sanitized: '{}' -> '{}'".format(original_name, material_name))
        imported_material_names.append(material_name)
    imported_material_names = list(set(imported_material_names))
    imported_material_names.sort()

    res = forms.SelectFromList.show(imported_material_names, 
                                    title="Select materials to import", 
                                    multiselect=True,
                                    button_name="Import Materials")

    if not res:
        return

    selected_materials = res

        
    # Process each material from Rhino
    for _, mat_data in material_data.items():
        original_name = mat_data["name"]
        material_name = REVIT_MATERIAL.sanitize_material_name(original_name)
        if material_name != original_name:
            print("Material name sanitized: '{}' -> '{}'".format(original_name, material_name))
        if material_name not in selected_materials:
            continue
        
        color_data = mat_data["color"]

        # Check if material already exists
        if material_name in existing_materials:
            material = existing_materials[material_name]
            print("Updating material: {}".format(material_name))
        else:
            # Create new material
            material = doc.GetElement(DB.Material.Create(doc, material_name))
            print("Creating new material: {}".format(material_name))
            material.AppearanceAssetId = DB.ElementId(-1)
            existing_materials[material_name] = material

        # Update material properties
        update_material_properties(material, color_data)

    # Assign materials to subcategories
    
    assign_materials_to_subcategories(doc, material_data, existing_materials)
        
    t.Commit()
    NOTIFICATION.messenger(main_text="Successfully imported materials from Rhino!")
        


################## main code below #####################
if __name__ == "__main__":
    import_rhino_material(DOC)







