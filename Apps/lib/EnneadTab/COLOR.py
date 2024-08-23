
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities for color manipulation and conversion"""

import random
import json

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


    color =  Color.FromArgb(red,green,blue)

    normalized_color = (color[0]/256.0, color[1]/256.0, color[2]/256.0)
    hsv_color = rgb_to_hsv(*normalized_color)
    grayed_hsv_color = (hsv_color[0], 0.6, hsv_color[2])
    grayed_rgb_color = hsv_to_rgb(*grayed_hsv_color)
    denormalized_rgb_color = (int(grayed_rgb_color[0]*256), int(grayed_rgb_color[1]*256), int(grayed_rgb_color[2]*256))

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




def _gather_data(raw_data, key_column):
    """Gather color data from raw data.

    Args:
        raw_data (dict): The raw data.
        key_column (int): The key column

    Returns:
        dict: The resulting data.
    """
    temp_data = {}
    for pointer in raw_data:
        i,j = pointer # i = row, j = column
        if j != key_column: 
            continue
        
        if i <=2:
            # ignore first two row, those rowsa re reserved for notes and header
            continue
        
        
        pointer_right_right = (i, j+2)
        subject_color = raw_data[pointer_right_right].get("color")
        
        # skip row where color is not defined(maybe due to merged cell), only record by row that define.
        if subject_color is None:
            continue
        
        
        
        subject = raw_data[pointer].get("value")
        if subject in [""]:
            continue
        
        pointer_right = (i, j+1)
        subject_abbr = raw_data[pointer_right].get("value")
        
        # if no abbr(maybe due to merged cell), use subject name as abbr. 
        subject_abbr = subject if subject_abbr == "" else subject_abbr
                                                       
        temp_data[subject] = {"abbr": subject_abbr, "color": subject_color}
        
    return temp_data
            
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
    
    if safe_template.endswith(".sexyDuck"):
        with open(safe_template, "r") as f:
            return json.load(f)
        
    if safe_template.endswith(".xlsx"):
        NOTIFICATION.messenger(main_text="Please save as .xls instead of .xlsx")
        return {}
    
    
    if safe_template.endswith(".xls"):
        import EXCEL
        raw_data = EXCEL.read_data_from_excel(safe_template, 
                                                worksheet = "HEALTHCARE", 
                                                return_dict=True)

        
        #column A and D are 0, 3 for key column
        department_data = _gather_data(raw_data, key_column = 0)
        program_data = _gather_data(raw_data, key_column = 3)
       
            
        return {"department_color_map": department_data, "program_color_map": program_data}
