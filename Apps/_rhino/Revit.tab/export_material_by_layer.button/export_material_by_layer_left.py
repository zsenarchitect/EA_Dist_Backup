__title__ = "ExportMaterialByLayer"
__doc__ = "Export material definitions for each layer using legal file names as dictionary keys."

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
from EnneadTab import ERROR_HANDLE, LOG, FOLDER, DATA_FILE, NOTIFICATION


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def export_material_by_layer():
    """Export material definitions for each layer.
    
    Returns:
        dict: Dictionary with legal file names as keys and material definitions as values
    """
    # Get all layers in the document
    all_layers = rs.LayerNames()
    
    # Initialize dictionary to store layer materials
    layer_materials = {}
    cached_convertion = {}
    
    for layer in all_layers:
        # Get material index for the layer
        material_index = rs.LayerMaterialIndex(layer)
        if material_index == -1:
            continue
            
        # Get material properties
        material = sc.doc.Materials[material_index]
        if not material:
            continue

        material_name = material.RenderMaterial.Name
        if material.RenderMaterial.TypeName == "Enscape":
            if material_name not in cached_convertion:
                pb_material = material.RenderMaterial.ConvertToPhysicallyBased(Rhino.Render.RenderTexture.TextureGeneration.Skip)
                cached_convertion[material_name] = pb_material
                note = "temporaryly converting to physically based for material: {}.\nBecasue you can not directly use Enscape material for Revit.".format(material_name)
                NOTIFICATION.messenger(main_text=note)
                print (note)
            else:
                pb_material = cached_convertion[material_name]

            rgb = (255*pb_material.BaseColor.R, 255*pb_material.BaseColor.G, 255*pb_material.BaseColor.B)
            transparency = 1.0 - pb_material.Opacity
            transparency_color = (255*pb_material.BaseColor.R, 255*pb_material.BaseColor.G, 255*pb_material.BaseColor.B)
            shininess = pb_material.Roughness
        else:
            # Convert color to RGB values
            diffuse = material.DiffuseColor
            rgb = (diffuse.R, diffuse.G, diffuse.B)

            if hasattr(material, "TransparencyColor"):
                transparency_color = (material.TransparencyColor.R, material.TransparencyColor.G, material.TransparencyColor.B)
            else:
                transparency_color = (diffuse.R, diffuse.G, diffuse.B)

            transparency = material.Transparency
            shininess = material.Shine

        material_def = {
            "name": material_name,
            "color": {
                "diffuse": rgb,
                "transparency": transparency,
                "transparency_color": transparency_color,
                "shininess": shininess
            }
        }
        
        # Create legal file name as key
        legal_name = FOLDER.secure_legal_file_name(layer)
        layer_materials[legal_name] = material_def
    
    # Save the material data to a file that Revit can read
    DATA_FILE.set_data(layer_materials, "RHINO_MATERIAL_MAP")
    NOTIFICATION.messenger(main_text="Material data exported successfully!")

if __name__ == "__main__":
    export_material_by_layer()
    
