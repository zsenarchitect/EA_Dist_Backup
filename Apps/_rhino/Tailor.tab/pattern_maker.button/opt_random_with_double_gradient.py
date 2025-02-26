import random

import pattern_maker_left
reload(pattern_maker_left)
from pattern_maker_left import TYPE_DEFINITIONS

def get_location_map(max_x, max_y):
    """Return a dict of location and type based on TYPE_DEFINITIONS ratios with gradient effect.
    
    The probability distribution considers both:
    1. Original type ratios from TYPE_DEFINITIONS
    2. Bottom-to-middle (rank_from_bm) ranking: 
       - rank_from_bm=1: strongly favored at bottom (row 0)
       - rank_from_bm=5: strongly favored at top (last row)
    3. Each pair of rows (0-1, 2-3, etc.) shares identical pattern
    
    Args:
        max_x (int): Maximum x coordinate
        max_y (int): Maximum y coordinate
        
    Returns:
        dict: Key is (x,y) tuple, value is type string
    """
    types = list(TYPE_DEFINITIONS.keys())
    base_weights = [TYPE_DEFINITIONS[t].get('ratio', 1/len(types)) for t in types]
    bm_ranks = [TYPE_DEFINITIONS[t].get('rank_from_bm', 3) for t in types]  # Default to middle (3) if not specified
    
    location_map = {}
    for row in range(0, max_y, 2):  # Iterate by steps of 2
        # Adjust weights based on bm ranking and position
        adjusted_weights = []

        # Calculate preferred rank (1 at bottom, 5 at top)
        if row == 0:
            prefered_rank = 1  # Bottom rows always prefer rank 1
        elif row >= max_y - 2:
            prefered_rank = 5  # Top rows prefer rank 5
        else:
            # Linear interpolation for middle rows (excluding top two rows)
            prefered_rank = 1 + (5-1) * row/(max_y - 3)  # Maps remaining rows between 1 and 5

        for base_w, bm_rank in zip(base_weights, bm_ranks):
            # Exponential scaling for much stronger effect
            rank_difference = abs(prefered_rank-bm_rank)
            a = 0.35 # the smaller the a, the more forced grdient. You will lose some randomness. # 0.05 is almost pure gradient, 0.1 is total ramdonize
            weight_multiplier = (a ** rank_difference)  # Steeper exponential decay
            adjusted_weights.append(base_w * weight_multiplier)
    
        
        # Create weighted population
        weighted_population = []
        
        for t, w in zip(types, adjusted_weights):
            weighted_population.extend([t] * int(w * 1000))
        print ("############")
        print(prefered_rank)
        print (types)
        print(adjusted_weights)
        
        # Apply pattern to both current row and next row
        for col in range(max_x):
            chosen_type = random.choice(weighted_population)
            location_map[(col, row)] = chosen_type
            if row + 1 < max_y:  # Check if next row exists
                location_map[(col, row + 1)] = chosen_type
    
    # Print row-by-row type distribution
    print("\nRow-by-row type distribution (bottom to top):")
    print("-" * 40)
    for row in range(0, max_y, 2):
        row_types = [location_map[(col, row)] for col in range(max_x)]
        row_types_str = "".join(row_types)
        print("Row {}: {}".format(row, row_types_str))
        
        if row + 1 < max_y:
            next_row_types = [location_map[(col, row + 1)] for col in range(max_x)]
            next_row_types_str = "".join(next_row_types)
            print("Row {}: {}".format(row + 1, next_row_types_str))
            
            # Check for differences between paired rows
            differences = sum(1 for a, b in zip(row_types_str, next_row_types_str) if a != b)
            if differences > 0:
                print("WARNING: Found {} differences between rows {} and {}".format(
                    differences, row, row + 1))
        
        # Print type counts for current row
        type_counts = ""
        for t in types:
            type_counts += "{}: {}, ".format(t, row_types.count(t))
        print("    Count: {}".format(type_counts))
        print("-" * 40)

    
    return location_map

