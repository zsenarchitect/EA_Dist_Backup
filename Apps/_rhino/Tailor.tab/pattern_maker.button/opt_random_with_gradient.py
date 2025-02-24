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
    for row in range(max_y):
        # Adjust weights based on bm ranking and position
        adjusted_weights = []

        # Calculate preferred rank (1 at bottom, 5 at top)
        if row == 0:
            prefered_rank = 1  # Bottom row always prefers rank 1
        elif row >= max_y - 2:
            prefered_rank = 5  # Top two rows prefer rank 5
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
        
        for col in range(max_x):
            location_map[(col, row)] = random.choice(weighted_population)
    
    # Print row-by-row type distribution
    print("\nRow-by-row type distribution (bottom to top):")
    print("-" * 40)
    for row in range(max_y):
        row_types = [location_map[(col, row)] for col in range(max_x)]
        type_counts = ""
        for t in types:
            type_counts += "{}: {}, ".format(t, row_types.count(t))
        print("Row {}: {}".format(row, type_counts))
    
    return location_map

