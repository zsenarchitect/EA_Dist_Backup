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
    """Convert an image to grayscale.
    Simple and reliable implementation for IronPython 2.7 with aggressive file handling.

    Args:
        original_image_path (str): The full path to the image to convert.
        new_image_path (str): The full path to save the new image. If None, the original image will be overwritten.
    """
    if new_image_path is None:
        new_image_path = original_image_path

    original = None
    bitmap = None
    temp_path = new_image_path + ".temp"  # Use temporary file for saving
    
    try:
        # Load original image
        for attempt in range(5):  # Retry loading original
            try:
                original = SD.Image.FromFile(original_image_path)
                bitmap = SD.Bitmap(original)
                break
            except:
                if attempt == 4:  # Last attempt
                    raise
                time.sleep(0.5)
        
        # Process the image
        for x in range(bitmap.Width):
            for y in range(bitmap.Height):
                color = bitmap.GetPixel(x, y)
                gray = int(color.R * 0.299 + color.G * 0.587 + color.B * 0.114)
                new_color = SD.Color.FromArgb(color.A, gray, gray, gray)
                bitmap.SetPixel(x, y, new_color)
        
        # Save to temporary file first
        if os.path.exists(temp_path):
            FOLDER.force_delete_file(temp_path)
        bitmap.Save(temp_path, SD.Imaging.ImageFormat.Jpeg)
        
        # Clean up resources before file operations
        if original is not None:
            original.Dispose()
        if bitmap is not None:
            bitmap.Dispose()
        original = None
        bitmap = None
        
        # Now do the file swap
        if FOLDER.force_rename_file(temp_path, new_image_path):
            return True
        else:
            print("Warning: Could not rename temporary file to target file")
            return False
            
    except Exception as e:
        print("Error converting image to grayscale: {}".format(str(e)))
        import traceback
        print(traceback.format_exc())
        return False
        
    finally:
        # Clean up resources
        if original is not None:
            try:
                original.Dispose()
            except:
                pass
        if bitmap is not None:
            try:
                bitmap.Dispose()
            except:
                pass
        # Clean up temporary file if it exists
        if os.path.exists(temp_path):
            try:
                FOLDER.force_delete_file(temp_path)
            except:
                pass


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