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

class MaterialImporter:
    """Handles importing and updating materials from Rhino to Revit."""
    
    def __init__(self, doc):
        """Initialize the MaterialImporter.
        
        Args:
            doc: The active Revit document
        """
        self.doc = doc
        self.existing_materials = self._get_existing_materials()
        self.output = script.get_output()
        
    def _get_existing_materials(self):
        """Get all existing materials in the document.
        
        Returns:
            Dictionary of material names to material objects
        """
        return {material.Name: material for material in DB.FilteredElementCollector(self.doc).OfClass(DB.Material)}
    
    def _update_material_properties(self, material, color_data):
        """Update material properties with color data.
        
        Args:
            material: The Revit material to update
            color_data: Color data from Rhino
        """
        r, g, b = color_data["diffuse"]
        material.Color = DB.Color(r, g, b)
        material.Transparency = int(color_data["transparency"] * 100)  # 0-100 range

        transparency_color_R, transparency_color_G, transparency_color_B = color_data["transparency_color"]
        material.SurfaceForegroundPatternColor = DB.Color(transparency_color_R, transparency_color_G, transparency_color_B)
        material.SurfaceForegroundPatternId = REVIT_SELECTION.get_solid_fill_pattern_id(self.doc)
        
        # Scale shininess from Rhino's 0-255 range to Revit's 0-128 range
        rhino_shininess = color_data["shininess"]  # 0-255 range
        revit_shininess = int((rhino_shininess / 255.0) * 128)  # Scale to 0-128 range
        revit_shininess = max(0, min(128, revit_shininess))  # Clamp between 0 and 128
        material.Shininess = revit_shininess
        
        self.output.print_md("Material properties updated:\nDiffuse: {}-{}-{}, Transparency: {}, Shininess: {} (Rhino: {})".format(
            r, g, b, material.Transparency, material.Shininess, rhino_shininess))
    
    def _get_subcategories_to_process(self, material_data):
        """Get list of subcategories that have material data.
        
        Args:
            material_data: Material data from Rhino
            
        Returns:
            List of subcategory names
        """
        sub_cate_to_process = []
        for category in self.doc.Settings.Categories:
            for sub_category in category.SubCategories:
                if sub_category.Name in material_data:
                    sub_cate_to_process.append(sub_category.Name)
        return sorted(sub_cate_to_process)
    
    def assign_materials_to_subcategories(self, material_data):
        """Assign materials to subcategories based on Rhino data.
        
        Args:
            material_data: Material data from Rhino
        """
        sub_cate_to_process = self._get_subcategories_to_process(material_data)
        if not sub_cate_to_process:
            return
            
        selected_sub_cates = forms.SelectFromList.show(
            sub_cate_to_process,
            title="Select subcategories to process",
            multiselect=True,
            button_name="Select Subcategories"
        )
        
        if not selected_sub_cates:
            return
            
        self.output.print_md("\n\nAssigning materials to subcategories\n\n")
        for category in self.doc.Settings.Categories:
            for sub_category in category.SubCategories:
                if sub_category.Name not in selected_sub_cates:
                    continue
                    
                material_name = material_data.get(sub_category.Name, {}).get("name")
                if not material_name:
                    continue
                    
                material = self.existing_materials.get(material_name)
                if material:
                    self.output.print_md("Updating material assignment for sub category: [**{}**], new material: [**{}**]".format(
                        sub_category.Name, material.Name))
                    sub_category.Material = material
    
    def _get_material_names(self, material_data):
        """Get list of unique material names from Rhino data.
        
        Args:
            material_data: Material data from Rhino
            
        Returns:
            List of unique material names
        """
        imported_material_names = []
        for _, mat_data in material_data.items():
            original_name = mat_data["name"]
            material_name = REVIT_MATERIAL.sanitize_material_name(original_name)
            if material_name != original_name:
                self.output.print_md("Material name sanitized: '{}' -> '{}'".format(original_name, material_name))
            imported_material_names.append(material_name)
        return sorted(list(set(imported_material_names)))
    
    def import_materials(self, material_data):
        """Import materials from Rhino data.
        
        Args:
            material_data: Material data from Rhino
        """
        imported_material_names = self._get_material_names(material_data)
        selected_materials = forms.SelectFromList.show(
            imported_material_names,
            title="Select materials to import",
            multiselect=True,
            button_name="Import Materials"
        )
        
        if not selected_materials:
            return
            
        for _, mat_data in material_data.items():
            original_name = mat_data["name"]
            material_name = REVIT_MATERIAL.sanitize_material_name(original_name)
            if material_name not in selected_materials:
                continue
                
            color_data = mat_data["color"]
            
            if material_name in self.existing_materials:
                material = self.existing_materials[material_name]
                self.output.print_md("Updating material: {}".format(material_name))
            else:
                material = self.doc.GetElement(DB.Material.Create(self.doc, material_name))
                self.output.print_md("Creating new material: {}".format(material_name))
                material.AppearanceAssetId = DB.ElementId(-1)
                self.existing_materials[material_name] = material
                
            self._update_material_properties(material, color_data)
            
        

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def import_rhino_material(doc):
    """Import material definitions from Rhino into Revit.
    
    Args:
        doc: The active Revit document
    """
    material_data = DATA_FILE.get_data("RHINO_MATERIAL_MAP")
    if not material_data:
        NOTIFICATION.messenger(main_text="No material data found. Please export materials from Rhino first.")
        return
        
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    importer = MaterialImporter(doc)
    importer.import_materials(material_data)
    importer.assign_materials_to_subcategories(material_data)
    t.Commit()
    NOTIFICATION.messenger(main_text="Successfully imported materials from Rhino!")

if __name__ == "__main__":
    import_rhino_material(DOC)







