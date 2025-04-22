__title__ = "ExportMaterialByLayer"
__doc__ = "Export material definitions for each layer using legal file names as dictionary keys."

import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab import ERROR_HANDLE, LOG, FOLDER

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
    
    for layer in all_layers:
            
        # Get material index for the layer
        material_index = rs.LayerMaterialIndex(layer)
        if material_index == -1:
            continue
            
        # Get material properties
        material = sc.doc.Materials[material_index]
        material_def = {
            "name": material.Name,
            "diffuse": material.DiffuseColor,
            "transparency": material.Transparency,
            "shininess": material.Shine
        }
        
        # Create legal file name as key
        legal_name = FOLDER.secure_legal_file_name(layer)
        layer_materials[legal_name] = material_def
    

    import pprint
    pprint.pprint(layer_materials)

if __name__ == "__main__":
    export_material_by_layer()
    
