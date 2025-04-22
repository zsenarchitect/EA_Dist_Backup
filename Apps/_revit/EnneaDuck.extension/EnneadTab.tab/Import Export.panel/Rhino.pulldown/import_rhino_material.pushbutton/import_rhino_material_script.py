#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Import material definitions from Rhino into Revit. Creates new materials or updates existing ones based on Rhino material properties."
__title__ = "Import Rhino Material"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

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
    material.Shininess = int(color_data["shininess"] * 128)  # Scale to 0-128 range
    print("Material properties updated:\nDiffuse: {}-{}-{}, Transparency: {}, Shininess: {}".format(
        r, g, b, material.Transparency, material.Shininess))

def assign_materials_to_subcategories(doc, material_data, existing_materials):
    """Assign materials to subcategories based on Rhino data.
    
    Args:
        doc (Document): The active Revit document
        material_data (dict): Material data from Rhino
        existing_materials (dict): Dictionary of existing materials
    """
    for category in doc.Settings.Categories:
        for sub_category in category.SubCategories:
            material_name = material_data.get(sub_category.Name, {}).get("name")
            if not material_name:
                continue
                
            material = existing_materials.get(material_name)
            if material:
                print("Updating material for sub category: {}, new material: {}".format(
                    sub_category.Name, material.Name))
                sub_category.Material = material

def sanitize_material_name(name):
    """Remove prohibited characters from material name.
    
    Args:
        name (str): Original material name
        
    Returns:
        str: Sanitized material name
    """
    name = name.replace("[imported]", '')
    prohibited_chars = '{}[]|;<>?`~'
    for char in prohibited_chars:
        name = name.replace(char, '_')
    name = name.strip()
    return name

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
    
    # Process each material from Rhino
    for _, mat_data in material_data.items():
        original_name = mat_data["name"]
        material_name = sanitize_material_name(original_name)
        if material_name != original_name:
            print("Material name sanitized: '{}' -> '{}'".format(original_name, material_name))
            
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







