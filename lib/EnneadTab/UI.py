import sys
import ENVIRONMENT
import os
if ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
    sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
    try:
        # cli platform does not support pyautoGUI
        import pyautogui
    except:
        # to-do: maybe Cpython will allow it
        pass
    

def is_images_on_screen(list_of_image_path, click=False):
    if not isinstance(list_of_image_path, list):
        return is_image_on_screen(list_of_image_path,click)
    
    for image in list_of_image_path:
        if is_image_on_screen(image,click):
            return True
    else:
        return False

def is_image_on_screen(image, click=False):
    location= pyautogui.locateOnScreen(image)
    
    if click:
        pyautogui.leftClick(location)
    if location:
        return True
    return False
    