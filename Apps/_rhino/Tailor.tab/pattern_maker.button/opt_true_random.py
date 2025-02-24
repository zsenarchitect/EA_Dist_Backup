

import random

from pattern_maker_left import TYPE_DEFINITIONS

def get_location_map():
    """return a dict of location and type, key is x,y tuple, value is type"""
    location_map = {}
    for i in range(10):
        for j in range(10):
            location_map[(i, j)] = random.choice(list(TYPE_DEFINITIONS.keys()))
    return location_map

