__title__ = "2128_PatternMaker"
__doc__ = "This button does PatternMaker when left click"


from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
import rhinoscriptsyntax as rs


TYPE_DEFINITIONS = {
    "A1":{
        "color":(129, 163, 154), 
        "ratio":0.2,
        "rank_from_bm":1, 
    },
    "C1":{
        "color":(84, 122, 130),  
        "ratio":0.2,
        "rank_from_bm":2,
    },
    "D2":{
        "color":(137, 173, 194), 
        "ratio":0.2,
        "rank_from_bm":3,
    },
    "D4":{
        "color":(100, 130, 150),  
        "ratio":0.2,
        "rank_from_bm":4,
    },
    "D7":{
        "color":(73, 95, 109),  
        "ratio":0.2,
        "rank_from_bm":5, 
    }
}


def get_type_by_color(color):
    for key, value in TYPE_DEFINITIONS.items():
        #make sure color is a tuple
        if not isinstance(color, tuple):
            color = tuple(color)
        if value['color'] == color:
            return key
    return None

import opt_true_random
import opt_random_with_gradient
import opt_random_with_double_gradient
import opt_from_excel


reload(opt_true_random) # pyright: ignore
reload(opt_random_with_gradient) # pyright: ignore
reload(opt_random_with_double_gradient) # pyright: ignore
reload(opt_from_excel) # pyright: ignore

#make sure all ration add together is 1
total_ratio = sum(TYPE_DEFINITIONS[t].get('ratio', 0) for t in TYPE_DEFINITIONS)
if abs(total_ratio - 1.0) > 0.0001:  # Allow small floating point differences
    NOTIFICATION.messenger("The sum of all ratios must be 1. Current sum: {:.4f}".format(total_ratio))
    raise ValueError("The sum of all ratios must be 1, current sum: {:.4f}".format(total_ratio))

def sorting_blocks(blocks, ref_surface):
    """Sort blocks based on their UV position on reference surface.
    
    Args:
        blocks: List of block references to sort
        ref_surface: Reference surface for UV mapping
    
    Returns:
        - Dictionary with (x,y) indices as keys and block instances as values
        - Number of unique x positions
        - Number of unique y positions
        
    Note:
        Blocks with identical normalized U values will receive the same x index.
        Blocks with identical normalized V values will receive the same y index.
    """
    # Get surface domain for normalization
    u_domain = rs.SurfaceDomain(ref_surface, 0)
    v_domain = rs.SurfaceDomain(ref_surface, 1)
    
    # Round normalized values to handle floating point precision
    def normalize_param(param, domain, precision=3):
        normalized = (param - domain[0]) / (domain[1] - domain[0])
        return round(normalized, precision)
    
    # Collect all UV parameters first
    temp_uvs = []
    for block in blocks:
        point = rs.BlockInstanceInsertPoint(block)
        uv_point = rs.SurfaceClosestPoint(ref_surface, point)
        u_param, v_param = rs.SurfaceParameter(ref_surface, uv_point)
        
        u_normalized = normalize_param(u_param, u_domain)
        v_normalized = normalize_param(v_param, v_domain)
        temp_uvs.append((block, u_normalized, v_normalized))
    
    # Extract unique sorted coordinates
    u_params = sorted(set(uv[1] for uv in temp_uvs))
    v_params = sorted(set(uv[2] for uv in temp_uvs))
    
    # Create index mappings
    u_indices = {val: idx for idx, val in enumerate(u_params)}
    v_indices = {val: idx for idx, val in enumerate(v_params)}
    
    # Create final block dictionary
    block_dict = {}
    for block, u_norm, v_norm in temp_uvs:
        x_index = u_indices[u_norm]
        y_index = v_indices[v_norm]
        block_dict[(x_index, y_index)] = block
    
    return block_dict, len(u_params), len(v_params)

def get_reference_surface():
    """Get the reference surface from the designated layer.
    
    Returns:
        object: Single reference surface object if found
        None: If validation fails
    """
    layer_name = "reference_surface"
    
    # Ensure layer exists
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name)
        NOTIFICATION.messenger("Created new layer: {}".format(layer_name))
        return None
        
    # Get and validate reference surface
    ref_surfaces = rs.ObjectsByLayer(layer_name)
    if not ref_surfaces:
        NOTIFICATION.messenger("No surface found on layer: {}".format(layer_name))
        return None
    if len(ref_surfaces) > 1:
        NOTIFICATION.messenger("Multiple surfaces found. Please keep only one reference surface on layer: {}".format(layer_name))
        return None
        
    return ref_surfaces[0]

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def pattern_maker():
    ref_srf = get_reference_surface()
    if not ref_srf:
        return
        
    blocks = rs.GetObjects("Select blocks", preselect=True, filter=rs.filter.instance)
    if not blocks:
        return
    options = [
        "option: true random", 
        "option: random with gradient",
        "option: random with double gradient",
        "option: from excel(option 1.1)",
        "option: from excel(option 1.2)",
        "option: from excel(option 2.1)",
        ]
    option = rs.ListBox(options, title="Select an option")
    

    block_dict, x_limit, y_limit = sorting_blocks(blocks, ref_srf)

    
    if option == "option: true random":
        location_map = opt_true_random.get_location_map(x_limit, y_limit)
    elif option == "option: random with gradient":
        location_map = opt_random_with_gradient.get_location_map(x_limit, y_limit)
    elif option == "option: random with double gradient":
        location_map = opt_random_with_double_gradient.get_location_map(x_limit, y_limit)
    elif option == "option: from excel(option 1.1)":
        location_map = opt_from_excel.get_location_map(x_limit, y_limit, "option 1.1")
    elif option == "option: from excel(option 1.2)":
        good_sheet = "option 1.2"
        location_map = opt_from_excel.get_location_map(x_limit, y_limit, good_sheet)
        
        header_blocks = rs.ObjectsByName("header")
        header_block_dict, header_x_limit, header_y_limit = sorting_blocks(header_blocks, ref_srf)
        header_location_map = opt_from_excel.get_location_map(header_x_limit, header_y_limit, good_sheet, is_header=True)
    elif option == "option: from excel(option 2.1)":
        location_map = opt_from_excel.get_location_map(x_limit, y_limit, "option 2.1")
    else:
        return
    
    rs.EnableRedraw(False)
    for location in sorted(block_dict.keys(), key=lambda x: (x[1], x[0])): # row first, then column
      
        # if considering header blocks, then skip treatment of header blocks in first run so the guid stay
        if "header_blocks" in locals():
            if rs.ObjectName(block_dict[location]) == "header":
                continue
        block = block_dict[location]
        current_transform = rs.BlockInstanceXform(block)
        block_type = location_map[location]
        new_block = rs.InsertBlock2(block_type, current_transform)
        rs.DeleteObject(block)
        rs.ObjectColorSource(new_block, 1)
        rs.ObjectColor(new_block, TYPE_DEFINITIONS[block_type].get('color', (0, 0, 0)))

    if "header_blocks" in locals():
        import pprint
        print ("header location map is : ")
        print (pprint.pprint(header_location_map))
        print ("################################")
        
        for location in sorted(header_block_dict.keys(), key=lambda x: (x[1], x[0])): # row first, then column
            block = header_block_dict[location]
            current_transform = rs.BlockInstanceXform(block)
            block_type = header_location_map[location]
            new_block = rs.InsertBlock2(block_type, current_transform)
            rs.DeleteObject(block)
            rs.ObjectColorSource(new_block, 1)
            rs.ObjectColor(new_block, TYPE_DEFINITIONS[block_type].get('color', (0, 0, 0)))
            rs.ObjectName(new_block, "header")

    NOTIFICATION.messenger("Pattern made")
if __name__ == "__main__":
    pattern_maker()
