#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Notifications for the user, such as popups and sounds."""

import SOUND
import DATA_FILE
import EXE
import IMAGE
import CONFIG

def is_hate_messenger():
    """Check to see if the user has disabled the messenger.

    Returns:
        bool: True if the user has disabled the messenger.
    """
    return  CONFIG.get_setting("radio_bt_popup_minimal", False) 

def is_hate_duck_pop():
    """Check to see if the user has disabled the duck pop.

    Returns:
        bool: True if the user has disabled the duck pop.
    """
    return not CONFIG.get_setting("toggle_bt_is_duck_allowed", False)

def messenger(main_text,
             width = None,
             height = None,
             image = None,
             animation_in_duration = None,
             animation_stay_duration = None,
             animation_fade_duration = None,
             x_offset = None):
    """Pop a simple message to the user, which disappears after a few seconds. 
    
       It can be used in place of the Windows notification, which is more annoying and has a sound .

    Args:
        main_text (str): the message to show. Better within 2 return lines. If too long, please use line return.
        width (int, optional): how width is the message max width. Defaults to 1200.
        height (int, optional): how tall is the message max height. Defaults to 150.
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



    DATA_FILE.set_data(data, "messenger_data.sexyDuck")

    EXE.try_open_app("Messenger")


def duck_pop(main_text = None):
    """Pop a duck to the user, which disappears after a few seconds.

    Args:
        main_text (str, optional): The message to show. Defaults to "Quack!".
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
    duck_pop("Hello, Ennead!")
    messenger("Hello Ennead!")

if __name__ == "__main__":
    duck_pop("Hello, world!")
    messenger("Hello world")
