#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
try:
    from System.Drawing import Color
    BLACK = Color.FromArgb(0,0,0)
    from colorsys import hsv_to_rgb, rgb_to_hsv
   
except:
    pass


def get_random_color():
    """get random color

    Returns:
       System.Drawing.Color: _description_
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

    return denormalized_rgb_color

def tuple_to_color(tuple):
    """quickly convert 3 int to color object

    Args:
        tuple (tuple of 3 int): _description_

    Returns:
        System.Drawing.Color: _description_
    """
    red,green,blue = tuple
    return Color.FromArgb(red,green,blue)


def invert_color(color, return_tuple = False):
    """_summary_

    Args:
        color (_type_): _description_
        return_tuple (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    R, G, B = color[0], color[1], color[2]
    inverted_color = 255 - R, 255 - G, 255 - B
    if return_tuple:
        return inverted_color
    else:
        return Color.FromArgb(*inverted_color)

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")