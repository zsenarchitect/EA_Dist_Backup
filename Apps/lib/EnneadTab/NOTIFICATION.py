#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EnneadTab Notification System

A sophisticated notification system providing customizable user alerts through
various channels including popups, sounds, and animated notifications. This module
offers both standard message notifications and fun, interactive notifications like
the signature duck popup.

Key Features:
    - Customizable popup notifications with animations
    - Fun, interactive duck notifications with sound effects
    - User preference management for notification styles
    - Rich text formatting with custom fonts
    - Animation timing control
    - Position and size customization
    - Background and font color customization

Note:
    All notifications respect user preferences and can be disabled through
    configuration settings.
"""

import SOUND
import DATA_FILE
import EXE
import IMAGE
import CONFIG

def is_hate_messenger():
    """Check if standard notifications are disabled.
    
    Retrieves user preference for minimal popup notifications from configuration.

    Returns:
        bool: True if user has opted for minimal notifications
    """
    return  CONFIG.get_setting("radio_bt_popup_minimal", False) 

def is_hate_duck_pop():
    """Check if duck notifications are disabled.
    
    Retrieves user preference for duck popup notifications from configuration.

    Returns:
        bool: True if duck notifications are disabled
    """
    return not CONFIG.get_setting("toggle_bt_is_duck_allowed", False)

FUNFONTS = [
    "Berlin Sans FB"
    "Ravie", 
    "Small Fonts",
    "Snap ITC",
    "Viner Hand ITC",
    "BankGothic Lt BT",
    "Bauhaus 93",
    "Bradley Hand ITC",
    "Broadway",
    "Chiller",
    "CityBlueprint",
    "Comic Sans MS",
    "CountryBlueprint"
    ]

def get_random_font():
    """Select a random decorative font.
    
    Chooses from a curated list of fun, decorative fonts suitable for
    notifications.

    Returns:
        str: Name of randomly selected font
    """
    import random
    return random.choice(FUNFONTS)

def messenger(main_text,
             width=None,
             height=None,
             image=None,
             animation_in_duration=None,
             animation_stay_duration=None,
             animation_fade_duration=None,
             x_offset=None,
             background_color=None,
             font_size=None,
             font_color=None,
             font_family=None):
    """Display a customizable popup notification.
    
    Creates an animated notification window with rich customization options
    for appearance and timing. Notifications automatically fade after display.

    Args:
        main_text (str): Message to display (supports line breaks)
        width (int, optional): Maximum width in pixels. Defaults to 1200.
        height (int, optional): Maximum height in pixels. Defaults to 150.
        image (str, optional): Path to image to display
        animation_in_duration (int, optional): Fade-in duration in milliseconds
        animation_stay_duration (int, optional): Display duration in milliseconds
        animation_fade_duration (int, optional): Fade-out duration in milliseconds
        x_offset (int, optional): Horizontal position offset
        background_color (str, optional): Background color in hex or RGB format
        font_size (int, optional): Text size in points
        font_color (str, optional): Text color in hex or RGB format
        font_family (str, optional): Font name from FUNFONTS or system fonts

    Note:
        If notifications are disabled via user preferences, this function
        returns without action.
    """

    if is_hate_messenger():
        return
    
    if not isinstance(main_text, str):
        main_text = str(main_text)

    data = {}
    data["main_text"] = main_text
    if animation_in_duration is not None:
        data["animation_in_duration"] = animation_in_duration
    if animation_stay_duration is not None:
        data["animation_stay_duration"] = animation_stay_duration
    if animation_fade_duration is not None:
        data["animation_fade_duration"] = animation_fade_duration
    if width is not None:
        data["width"] = width
    if height is not None:
        data["height"] = height 
    if image is not None:
        data["image"] = image
    if x_offset is not None:
        data["x_offset"] = x_offset
    if font_color:
        data["font_color"] = font_color
    if font_family:
        data["font_family"] = font_family
    if font_size:
        data["font_size"] = font_size
    if background_color:
        data["background_color"] = background_color



    DATA_FILE.set_data(data, "messenger_data.sexyDuck")

    EXE.try_open_app("Messenger")


def duck_pop(main_text=None):
    """Display an animated duck notification with sound.
    
    Creates a fun, interactive notification featuring an animated duck
    with sound effects. Falls back to standard notification if duck
    notifications are disabled.

    Args:
        main_text (str, optional): Message to display. Defaults to "Quack!"

    Note:
        - Uses randomly selected duck images and sounds
        - Includes explosion animation effect
        - Falls back to messenger() if duck notifications are disabled
    """
    if is_hate_duck_pop():
   
        messenger(main_text)
        return
    
    if not main_text:
        main_text = "Quack!"

    data = {}
    data["main_text"] = main_text

    # when the ranking is ready, can progress to make better ranked duck
    data["duck_image"] = IMAGE.get_one_image_path_by_prefix("duck_pop")
    data["explosion_gif"] = IMAGE.get_image_path_by_name("duck_explosion.gif")
    data["audio"] = SOUND.get_one_audio_path_by_prefix("duck")
    DATA_FILE.set_data(data, "DUCK_POP.sexyDuck") 

    EXE.try_open_app("DuckPop", legacy_name="Duck_Pop")
  

def unit_test():
    """Run comprehensive tests of notification system.
    
    Tests both standard and duck notifications with default settings.
    """
    duck_pop("Hello, Ennead!")
    messenger("Hello Ennead!")

if __name__ == "__main__":
    font = get_random_font()
    messenger("Hello world with bigger text\nUsing [{}]".format(font), font_size=30, font_family=font)

    