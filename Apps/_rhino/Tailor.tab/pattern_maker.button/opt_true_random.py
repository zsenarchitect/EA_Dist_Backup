import random

from pattern_maker_left import TYPE_DEFINITIONS

def get_location_map(max_x, max_y):
    """Return a dict of location and type based on TYPE_DEFINITIONS ratios.
    
    Args:
        max_x (int): Maximum x coordinate
        max_y (int): Maximum y coordinate
        
    Returns:
        dict: Key is (x,y) tuple, value is type string, weighted by TYPE_DEFINITIONS ratios
    """
    # Extract types and their weights from TYPE_DEFINITIONS
    types = list(TYPE_DEFINITIONS.keys())
    weights = [TYPE_DEFINITIONS[t].get('ratio', 1/len(types)) for t in types]
    
    # Create a population list based on weights
    population = []
    for t, w in zip(types, weights):
        population.extend([t] * int(w * 100))
    
    location_map = {}
    for col in range(max_x):
        for row in range(max_y):
            location_map[(col, row)] = random.choice(population)
    return location_map

