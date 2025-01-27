import bpy
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nodes = mat.node_tree.nodes
    # Remove ShaderNodeMixShader nodes
    mix = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeMixShader)), None)
    while mix is not None:
        nodes.remove(mix)
        mix = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeMixShader)), None)
    # Remove ShaderNodeEmission nodes
    emission = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeEmission)), None)
    while emission is not None:
        nodes.remove(emission)
        emission = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeEmission)), None)
    # Remove ShaderNodeBsdfTransparent nodes
    transparent = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeBsdfTransparent)), None)
    while transparent is not None:
        nodes.remove(transparent)
        transparent = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeBsdfTransparent)), None)
    # Remove ShaderNodeLightPath nodes
    light_path = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeLightPath)), None)
    while light_path is not None:
        nodes.remove(light_path)
        light_path = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeLightPath)), None)
    # Add a principled shader and link it
    output = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
    if output is None:
        continue
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (output.location[0] - 400, output.location[1] + 100)
    mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
    # Link image texture to the principled shader
    texture = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeTexImage)), None)
    if texture is None:
        continue
    mat.node_tree.links.new(texture.outputs['Color'], principled.inputs['Base Color'])
    # Add a value node for roughness
    valueB = nodes.new('ShaderNodeValue')
    valueB.location = (principled.location[0] - 200, principled.location[1] - 300)
    valueB.outputs[0].default_value = 0.5
    mat.node_tree.links.new(valueB.outputs[0], principled.inputs['Roughness'])
    # Rename the material
    mat.name = "A_" + mat.name
    # Rename the image
    image_node = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeTexImage)), None)
    if image_node is not None and image_node.image is not None:
        image_node.image.name = "A_" + image_node.image.name
