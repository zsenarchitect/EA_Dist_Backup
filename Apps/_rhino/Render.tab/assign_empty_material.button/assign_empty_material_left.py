__title__ = "AssignEmptyMaterial"
__doc__ = """Assigns unique materials to layers without assigned materials.

Key Features:
- Creates a unique material for each layer without materials
- Material names based on layer hierarchy (including parent layers)
- Makes D5 material editing workflow more efficient
- Use the layer color as the material diffuse color
"""


from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # type: ignore

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def assign_empty_material():

    doc = sc.doc
    
    # Get all layers in the document
    all_layers = rs.LayerNames()
    
    # Track how many materials were created
    materials_created = 0
    
    for layer_name in all_layers:
        # Check if layer is visible and not locked
        if not rs.IsLayerVisible(layer_name) or rs.IsLayerLocked(layer_name):
            continue

            
        # Check if any objects on this layer already have materials assigned
        current_layer_material_index = rs.LayerMaterialIndex(layer_name)

        if current_layer_material_index > -1:
            continue

            
        # Create a unique material name based on the layer hierarchy
        material_name = "SampleMat_" + layer_name.replace("::", "_")
        

        # Create the new material
        material = Rhino.DocObjects.Material()
        material.Name = material_name
        material.DiffuseColor = rs.LayerColor(layer_name)
        
        # Add the material to the document
        material_index = doc.Materials.Add(material)
        
        # Assign the material to all objects on this layer
        rs.LayerMaterialIndex(layer_name, material_index)
        
        materials_created += 1
    
    if materials_created > 0:
        message = "Created and assigned {} unique materials to layers without materials.".format(materials_created)
    else:
        message = "No layers found that need materials assigned."
    
    NOTIFICATION.messenger(message)

    
if __name__ == "__main__":
    assign_empty_material()
