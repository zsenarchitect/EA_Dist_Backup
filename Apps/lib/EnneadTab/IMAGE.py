"""Utilities for image retrieval and manipulation."""

import os
import random
import time
import ENVIRONMENT
import FOLDER

try:
    import System.Drawing as SD  # pyright: ignore
except Exception as e:
    pass


def get_image_path_by_name(file_name):
    """Get the full path for a specified image in the EnneadTab image library.

    Args:
        file_name (str): The name of the image file to retrieve, including extension.

    Returns:
        str: The full path to the image file.
    """
    path = "{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)
    if os.path.exists(path):
        return path
    print("A ha! {} is not valid or accessibile. Better luck next time.".format(path))


def get_one_image_path_by_prefix(prefix):
    """Will return a random image file from the EnneadTab image library that starts with the specified prefix.

    Args:
        prefix (str): The prefix to search for in the image file names.

    Returns:
        str: The full path to the image file.
    """
    files = [
        os.path.join(ENVIRONMENT.IMAGE_FOLDER, f)
        for f in os.listdir(ENVIRONMENT.IMAGE_FOLDER)
        if f.startswith(prefix)
    ]
    file = random.choice(files)
    return file


def average_RGB(R, G, B):
    """Average the RGB values of a pixel to simplify it to greyscale.

    Args:
        R (int): Red. 0-255.
        G (int): Blue. 0-255.
        B (int): Green. 0-255.

    Returns:
        int: Average of the RGB values.
    """
    return (R + G + B) / 3


def convert_image_to_greyscale(original_image_path, new_image_path=None):
    """Convert an image to greyscale.

    Args:
        original_image_path (str): The full path to the image to convert.
        new_image_path (str): The full path to save the new image. If None, the original image will be overwritten. Careful: defaults to None!
    """
    if new_image_path is None:
        new_image_path = original_image_path
    image = SD.Image.FromFile(original_image_path)
    for x in range(image.Width):
        for y in range(image.Height):
            pixel_color = image.GetPixel(x, y)
            R = pixel_color.R
            G = pixel_color.G
            B = pixel_color.B
            A = pixel_color.A
            new_color = SD.Color.FromArgb(
                A, average_RGB(R, G, B), average_RGB(R, G, B), average_RGB(R, G, B)
            )
            image.SetPixel(x, y, new_color)
    image.Save(new_image_path)
    return image


def create_bitmap_text_image(text, size = (64, 32), bg_color = (0, 0, 0), font_size = 9):

    if random.random() < 0.2:
        purge_old_temp_bmp_files()


    image = SD.Bitmap(size[0], size[1])
    graphics = SD.Graphics.FromImage(image)
    font = SD.Font("Arial", font_size)
    brush = SD.SolidBrush(SD.Color.FromArgb(bg_color[0], bg_color[1], bg_color[2]))
    text_size = graphics.MeasureString(text, font)
    text_x = (size[0] - text_size.Width) / 2
    text_y = (size[1] - text_size.Height) / 2
    graphics.DrawString(text, font, brush, text_x, text_y)
    output_path = FOLDER.get_EA_dump_folder_file("_temp_text_bmp_{}_{}.bmp".format(text, time.time()))
    image.Save(output_path)
    return output_path


def purge_old_temp_bmp_files():
    """Purge old temporary bmp files in the EA dump folder."""
    for file in os.listdir(FOLDER.DUMP_FOLDER):
        if file.endswith(".bmp") and file.startswith("_temp_text_bmp_"):
            file_path = os.path.join(FOLDER.DUMP_FOLDER, file)
            if time.time() - os.path.getmtime(file_path) > 60 * 60 * 24*2:
                os.remove(file_path)

if __name__ == "__main__":
    image = create_bitmap_text_image("qwert", size = (64, 32), bg_color = (0, 99, 0), font_size = 9)
    os.startfile(image)