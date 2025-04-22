#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities for color manipulation and conversion"""

import random
import json
import io


try:
    from System.Drawing import Color # pyright: ignore
    BLACK = Color.FromArgb(0,0,0)
    from colorsys import hsv_to_rgb, rgb_to_hsv
   
except:
    pass

# define before other customs import to avoid circular reference break in ironpython. 
# #cpython seem to be ok with this kind of circular ref
class TextColorEnum:
    Red = "red"
    Green = "green"
    Blue = "blue"
    Yellow = "yellow"
    Magenta = "magenta"
    Cyan = "cyan"
    White = "white"
ACCENT_COLOR = 70,70,70
PRIMARY_BACKGROUND = 100, 100, 100
DARKER_BACKGROUND = 70,70,70
PRIMARY_TEXT = 218,232,253


import ENVIRONMENT
if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
    from Autodesk.Revit.DB import Color as DB_Color # pyright: ignore
if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Eto # pyright: ignore
import NOTIFICATION
import FOLDER




def darken_color(color, amount):
    """Darken a color.

    Args:
        color (tuple): The color to darken.
        amount (float): The amount to darken the color.
    """
    return tuple(int(max(0, c * (1 - amount))) for c in color)

def lighten_color(color, amount):
    """Lighten a color.

    Args:
        color (tuple): The color to lighten.
        amount (float): The amount to lighten the color.
    """ 
    return tuple(int(min(255, c * (1 + amount))) for c in color)

def from_rgb(r, g, b):
    """Generate a color object from rgb values.

    Args:
        r (int): The red value.
        g (int): The green value.
        b (int): The blue value.

    Returns:
        System.Drawing.Color: The resulting color object.
    """
    return Color.FromArgb(r, g, b)

def get_random_color(return_tuple = True):
    """Generate a random color object.

    Args:
        return_tuple (bool, optional): Return as a tuple of 3 ints. Defaults to True.

    Returns:
    if return_tuple is True:
        tuple: The resulting color as a tuple of 3 ints.
    else:
        System.Drawing.Color: The resulting color object.
    """
    
    red = int(255*random.random())
    green = int(255*random.random())
    blue = int(255*random.random())

    color = Color.FromArgb(red, green, blue)

    # Convert RGB values to 0-1 range for HSV conversion
    normalized_color = (color.R/256.0, color.G/256.0, color.B/256.0)
    
    # Convert RGB to HSV (Hue, Saturation, Value)
    hsv_color = rgb_to_hsv(*normalized_color)
    
    # Create desaturated version by setting saturation to 0.1
    # Keeps original hue and value, but reduces color intensity
    grayed_hsv_color = (hsv_color[0], 0.05, hsv_color[2])
    
    # Convert back to RGB colorspace
    grayed_rgb_color = hsv_to_rgb(*grayed_hsv_color)
    
    # Convert back to 0-255 range for RGB values
    denormalized_rgb_color = (int(grayed_rgb_color[0]*256), 
                             int(grayed_rgb_color[1]*256), 
                             int(grayed_rgb_color[2]*256))

    if return_tuple:
        return denormalized_rgb_color
    return Color.FromArgb(*denormalized_rgb_color)

def tuple_to_color(tuple):
    """Convert 3 ints to color object

    Args:
        tuple (tuple of 3 int): The tuple of 3 ints.

    Returns:
        System.Drawing.Color: The resulting color object.
    """
    red,green,blue = tuple
    if any([red is None, green is None, blue is None]):
        print ("tuple_to_color: ", tuple)
        if red is None:
            red = 0
        if green is None:
            green = 0
        if blue is None:
            blue = 0
            
    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return DB_Color(red,green,blue)
    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        
        return Eto.Drawing.Color(red/256.0,
                                green/256.0,
                                blue/256.0)
    
    return Color.FromArgb(red,green,blue)


def invert_color(color, return_tuple = False):
    """Invert a color.

    Args:
        color (tuple): The color to invert.
        return_tuple (bool, optional): Return as a tuple of 3 ints. Defaults to False.

    Returns:
    if return_tuple is True:
        tuple: The resulting color as a tuple of 3 ints.
    else:
        System.Drawing.Color: The resulting color object.
    """
    R, G, B = color[0], color[1], color[2]
    inverted_color = 255 - R, 255 - G, 255 - B
    if return_tuple:
        return inverted_color
    else:
        return Color.FromArgb(*inverted_color)
    
def rgb_to_hex(rgb_tuple):
    """Convert rgb to hex.

    Args:
        rgb_tuple (tuple): The rgb tuple.

    Returns:
        str: The resulting hex string.
    """
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_tuple[0]),int(rgb_tuple[1]),int(rgb_tuple[2]))


def hex_to_rgb(hex_str):
    """Convert hex to rgb.

    Args:
        hex_str (str): The hex string.

    Returns:
        tuple: The resulting rgb tuple.
    """
    return tuple(int(str(hex_str).lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def decimal_to_rgb(decimal_color):
    """Convert decimal to rgb.

    Args:
        decimal_color (int): The decimal color.

    Returns:
        tuple: The resulting rgb color.
    """
    red = decimal_color % 256
    green = (decimal_color // 256) % 256
    blue = (decimal_color // 256 // 256) % 256
    return (int(red), int(green), int(blue))



def is_same_color(color1, color2):
    """Checks if the environment is Revit,
    then checks if the colors are the same.

    Args:
        color1 (tuple): The first color.
        color2 (tuple): The second color.

    Returns:
        bool: True if the colors are the same, False otherwise.
    """
    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return color1.Red == color2.Red and color1.Green == color2.Green and color1.Blue == color2.Blue
    

    return color1[0] == color2[0] and color1[1] == color2[1] and color1[2] == color2[2]




def _gather_data(raw_data, key_column, is_zero_indexed):
    """Gather color data from raw data extracted from an Excel file.

    This function processes raw Excel data to extract color information based on a specified
    key column. It handles both zero-indexed and one-indexed data structures.

    Args:
        raw_data (dict): Raw data from Excel structured as {(row,col): {"value": val, "color": color}}.
        key_column (int): The column index to use for subject names/keys.
        is_zero_indexed (bool): Whether the Excel data uses zero-based indexing.

    Returns:
        dict: Structured color data in the format {subject_name: {"abbr": abbreviation, "color": color_value}}.
    """
    out = {}
    
    # Determine the starting row based on indexing (skip 3 header rows)
    start_row = 3 if is_zero_indexed else 4
    
    # Adjust key_column if needed
    lookup_key_column = key_column if is_zero_indexed else key_column + 1
    
    for pointer in sorted(raw_data.keys()):
        row, col = pointer
        
        # Skip non-key columns and header rows
        if str(col) != str(lookup_key_column) or row < start_row:
            continue
        
        # Get subject name from key column
        subject = raw_data[pointer].get("value")
        if not subject:
            continue
        
        # Get abbreviation from next column
        abbr_pointer = (row, col + 1)
        subject_abbr = raw_data.get(abbr_pointer, {}).get("value", "")
        
        # Get color from two columns to the right
        color_pointer = (row, col + 2)
        subject_color = raw_data.get(color_pointer, {}).get("color")
        
        # Skip rows where color is not defined (may be due to merged cells)
        if subject_color is None:
            print ("subject_color is None: ", subject_color, " | for subject: ", subject)
            continue
        
        # If abbreviation is empty, use subject name
        subject_abbr = subject if not subject_abbr else subject_abbr
        
        # Store the data
        out[subject] = {"abbr": subject_abbr, "color": subject_color}



    return out
            
def get_color_template_data(template = None):
    """Get color template data from department standards.

    Args:
        template (str, optional): The template path. Defaults to None.

    Returns:
        dict: The resulting color data.
    """
    if template:
        safe_template = FOLDER.copy_file_to_local_dump_folder(template)
    else:
        safe_template = "OFFICE STANDARD FILE TO BE MADE"
    
    if safe_template.endswith(ENVIRONMENT.PLUGIN_EXTENSION):
        with io.open(safe_template, "r", encoding = "utf-8") as f:
            return json.load(f)
        
    
    if safe_template.endswith(".xls") or safe_template.endswith(".xlsx"):
        import EXCEL
        raw_data = EXCEL.read_data_from_excel(safe_template, 
                                                worksheet = "HEALTHCARE", 
                                                return_dict=True)

        


        first_key = sorted(raw_data.keys())[0]
        is_zero_indexed = first_key[0] == 0
        # print ("is_zero_indexed", is_zero_indexed)


        #column A and D are 0, 3 for key column in a 0-indexed system
        department_data = _gather_data(raw_data, key_column = 0, is_zero_indexed = is_zero_indexed)
        program_data = _gather_data(raw_data, key_column = 3, is_zero_indexed = is_zero_indexed)

        # import pprint
        # print ("department_data")
        # pprint.pprint(department_data, indent = 4)
        # print ("\n\nprogram_data")
        # pprint.pprint(program_data, indent = 4)

            
        return {"department_color_map": department_data, "program_color_map": program_data}
