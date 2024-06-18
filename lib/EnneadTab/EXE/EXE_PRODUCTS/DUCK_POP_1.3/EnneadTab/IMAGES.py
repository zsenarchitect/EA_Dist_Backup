#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import System.Drawing as SD
except Exception as e:
    print( e.message)

def get_image_from_file (file):
    return SD.Image.FromFile(file)

def sample_image(file_path, sample_X = None, sample_Y = None, return_color = False):
    """
    sample_X: int, how many division do you want. Default is image width
    samepl_Y: sim as above
    """


    image = SD.Image.FromFile(file_path)
    if sample_X is None:
        sample_X = image.Width
    if sample_Y is None:
        sample_Y = image.Height


    """
    unresolved issue now: prefer to sample the center of the pixel sample box, not the begiing corner
    """
    sample_X_step = int(image.Width / sample_X)
    OUT = []
    for x in range(sample_X_step):
        for y in range(sample_Y):
            pixel_color = image.GetPixel(x * sample_X_step, y)
            R, G, B, A = pixel_color
            print pixel_color
            print (R, G, B, A)
            if return_color:
                OUT.append(pixel_color)
            else:
                OUT.append((R, G, B, A))

            """
            newColor = Color.FromArgb(pixel_color.R, 0, 0)
            image.SetPixel(x, y, newColor)
            """
    return OUT


def map_color_value(color_int, bound_max, bound_min = 0):
    """convert a valid color int to a int in range of [bound_min, bound_max]

    Args:
        color_int (int): _description_
        bound_max (int): _description_
        bound_min (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    if not 0 <= color_int <= 255:
        print "color value need to be 0~255, include ends"
    k = (bound_max - bound_min)/255
    b = bound_min
    return k * color_int + b

def average_RGB(R, G, B):
    """avergae RGB value to simulate a quick greyscale value

    Args:
        R (int): _description_
        G (int): _description_
        B (int): _description_

    Returns:
        int: math average of the RGB int value
    """
    return (R+G+B)/3



#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")