# https://python-holidays.readthedocs.io/en/latest/index.html

"""
Holiday Greeting System for EnneadTab.

This module provides customized holiday greetings for office employees based on the current date.
Supports multiple cultural and seasonal celebrations with images and sound effects.
"""

from __future__ import print_function, division, absolute_import

import datetime
import os
import random


import FOLDER
import SOUND
import ENVIRONMENT
import NOTIFICATION
import OUTPUT
from __init__ import dream

# Python 2/3 compatibility
try:
    basestring  # Python 2 # pyright: ignore
except NameError:
    basestring = str  # Python 3

class HolidayDateChecker:
    """Utility class to check holiday dates for any year."""
    
    @staticmethod
    def is_valid_date(start_date, end_date):
        """
        Check if current date falls within the given range.
        
        Args:
            start_date (datetime.date): Start date of holiday period
            end_date (datetime.date): End date of holiday period
            
        Returns:
            bool: True if current date is within range
        """
        today = datetime.datetime.now().date()
        return start_date <= today <= end_date

    @staticmethod
    def get_chinese_new_year_dates(year):
        """Get Chinese New Year celebration period for given year."""
        # Dates from Chinese calendar (approximate, can be adjusted)
        dates = {
            2024: (datetime.date(2024, 2, 10), datetime.date(2024, 2, 24)),  # Year of Dragon
            2025: (datetime.date(2025, 1, 29), datetime.date(2025, 2, 8)),   # Year of Snake
            2026: (datetime.date(2026, 2, 17), datetime.date(2026, 3, 3)),   # Year of Horse
            2027: (datetime.date(2027, 2, 6), datetime.date(2027, 2, 20)),   # Year of Goat
            2028: (datetime.date(2028, 1, 26), datetime.date(2028, 2, 9)),   # Year of Monkey
            2029: (datetime.date(2029, 2, 13), datetime.date(2029, 2, 27)),  # Year of Rooster
            2030: (datetime.date(2030, 2, 3), datetime.date(2030, 2, 17)),   # Year of Dog
            2031: (datetime.date(2031, 1, 23), datetime.date(2031, 2, 6)),   # Year of Pig
            2032: (datetime.date(2032, 2, 11), datetime.date(2032, 2, 25)),  # Year of Rat
            2033: (datetime.date(2033, 1, 31), datetime.date(2033, 2, 14)),  # Year of Ox
            2034: (datetime.date(2034, 2, 19), datetime.date(2034, 3, 5)),   # Year of Tiger
            2035: (datetime.date(2035, 2, 8), datetime.date(2035, 2, 22)),   # Year of Rabbit
            2036: (datetime.date(2036, 1, 28), datetime.date(2036, 2, 11)),  # Year of Dragon
            2037: (datetime.date(2037, 2, 15), datetime.date(2037, 3, 1)),   # Year of Snake
            2038: (datetime.date(2038, 2, 4), datetime.date(2038, 2, 18)),   # Year of Horse
            2039: (datetime.date(2039, 1, 24), datetime.date(2039, 2, 7)),   # Year of Goat
            2040: (datetime.date(2040, 2, 12), datetime.date(2040, 2, 26)),  # Year of Monkey
            2041: (datetime.date(2041, 2, 1), datetime.date(2041, 2, 15)),   # Year of Rooster
            2042: (datetime.date(2042, 1, 22), datetime.date(2042, 2, 5)),   # Year of Dog
            2043: (datetime.date(2043, 2, 10), datetime.date(2043, 2, 24)),  # Year of Pig
            2044: (datetime.date(2044, 1, 30), datetime.date(2044, 2, 13)),  # Year of Rat
            # Add more years as needed
        }
        return dates.get(year, (None, None))

    @staticmethod
    def get_mid_autumn_dates(year):
        """Get Mid-Autumn Festival dates for given year."""
        dates = {
            2024: (datetime.date(2024, 9, 17), datetime.date(2024, 9, 30)),
            2025: (datetime.date(2025, 10, 6), datetime.date(2025, 10, 19)),
            2026: (datetime.date(2026, 9, 25), datetime.date(2026, 10, 8)),
            2027: (datetime.date(2027, 9, 15), datetime.date(2027, 9, 28)),
            2028: (datetime.date(2028, 10, 3), datetime.date(2028, 10, 16)),
            2029: (datetime.date(2029, 9, 22), datetime.date(2029, 10, 5)),
            2030: (datetime.date(2030, 9, 12), datetime.date(2030, 9, 25)),
            2031: (datetime.date(2031, 10, 1), datetime.date(2031, 10, 14)),
            2032: (datetime.date(2032, 9, 19), datetime.date(2032, 10, 2)),
            2033: (datetime.date(2033, 9, 8), datetime.date(2033, 9, 21)),
            2034: (datetime.date(2034, 9, 28), datetime.date(2034, 10, 11)),
            2035: (datetime.date(2035, 9, 17), datetime.date(2035, 9, 30)),
            2036: (datetime.date(2036, 10, 5), datetime.date(2036, 10, 18)),
            2037: (datetime.date(2037, 9, 24), datetime.date(2037, 10, 7)),
            2038: (datetime.date(2038, 9, 13), datetime.date(2038, 9, 26)),
            2039: (datetime.date(2039, 10, 2), datetime.date(2039, 10, 15)),
            2040: (datetime.date(2040, 9, 20), datetime.date(2040, 10, 3)),
            2041: (datetime.date(2041, 9, 10), datetime.date(2041, 9, 23)),
            2042: (datetime.date(2042, 9, 29), datetime.date(2042, 10, 12)),
            2043: (datetime.date(2043, 9, 18), datetime.date(2043, 10, 1)),
            2044: (datetime.date(2044, 10, 7), datetime.date(2044, 10, 20)),
            # Add more years as needed
        }
        return dates.get(year, (None, None))

    @staticmethod
    def get_xmas_dates(year):
        """Get Christmas celebration period."""
        return (
            datetime.date(year, 12, 20),
            datetime.date(year, 12, 31)
        )

    @staticmethod
    def get_pi_day_dates(year):
        """Get Pi Day celebration period."""
        return (
            datetime.date(year, 3, 13),
            datetime.date(year, 3, 15)
        )

    @staticmethod
    def get_april_fools_dates(year):
        """Get April Fools' Day celebration period."""
        return (
            datetime.date(year, 4, 1),
            datetime.date(year, 4, 1)
        )

    @staticmethod
    def get_may_force_dates(year):
        """Get Star Wars Day celebration period."""
        return (
            datetime.date(year, 5, 4),
            datetime.date(year, 5, 4)
        )

    @staticmethod
    def get_halloween_dates(year):
        """Get Halloween celebration period."""
        return (
            datetime.date(year, 10, 25),
            datetime.date(year, 10, 31)
        )


def display_greeting(image_name, title_text="Greeting from EnneadTab", 
                    sound_file=None, md_text=None):
    """
    Display holiday greeting with image and optional sound.
    
    Args:
        image_name (str or list): Filename of image to display, or list of image names to randomly choose from.
                                 Images will be prefixed with 'holiday_' if not already present.
        title_text (str): Window title text
        sound_file (str, optional): Sound file to play
        md_text (str, optional): Markdown text to display
    """
    # Handle list of images by randomly selecting one
    if isinstance(image_name, list):
        if not image_name:  # Empty list check
            return
        image_name = random.choice(image_name)
        
    # Add 'holiday_' prefix if not already present
    if isinstance(image_name, basestring) and not image_name.startswith("holiday_"):
        image_name = "holiday_" + image_name
        
    image_file = "{0}\\{1}".format(ENVIRONMENT.IMAGE_FOLDER, image_name)
    
    output = OUTPUT.get_output()
    output.write(title_text, OUTPUT.Style.Title)
    if os.path.exists(image_file):
        output.write(image_file)
    
    if md_text:
        output.write(md_text)
        
    output.plot()
    
    if sound_file:
        # Check if sound file needs folder prefix for standard location
        if not os.path.isfile(sound_file) and not sound_file.startswith("holiday_"):
            sound_file = "{0}\\{1}".format(ENVIRONMENT.AUDIO_FOLDER, sound_file)
        SOUND.play_sound(sound_file)


def festival_greeting():
    """Check current date and display appropriate holiday greetings."""
    

    
    year = datetime.datetime.now().year
    checker = HolidayDateChecker()
    
    # Dictionary mapping holiday check functions to greeting functions
    holiday_checks = [
        # Chinese New Year
        (checker.get_chinese_new_year_dates(year), greeting_chinese_new_year),
        # Mid-Autumn Festival
        (checker.get_mid_autumn_dates(year), greeting_mid_moon),
        # Christmas
        (checker.get_xmas_dates(year), greeting_xmas),
        # Pi Day
        (checker.get_pi_day_dates(year), greeting_pi),
        # April Fools' Day
        (checker.get_april_fools_dates(year), greeting_april_fools),
        # Star Wars Day
        (checker.get_may_force_dates(year), greeting_may_force),
        # Halloween
        (checker.get_halloween_dates(year), greeting_halloween)
    ]
    
    # Check each holiday and display greeting if date is valid
    for (start, end), greeting_func in holiday_checks:
        if start and checker.is_valid_date(start, end):
            greeting_func()
            return

    # ramdon print dream
    if random.random() < 0.00005:
        output = OUTPUT.get_output()
        output.write(dream(), OUTPUT.Style.MainBody)
        output.plot()


def greeting_april_fools():
    """Display April Fool's Day greeting and pranks."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_april_fools_dates(year)
    
    if not HolidayDateChecker.is_valid_date(start, end):
        return

    import JOKE

    for _ in range(random.randint(1, 5)):
        JOKE.prank_dvd()

    # Use some fun sounds for April Fools
    fun_sounds = [
        "meme_bruh.wav",
        "meme_oof.wav",
        "meme_what.wav",
        "sound_effect_mario_die.wav",
        "sound_effect_duck.wav"
    ]
    
    NOTIFICATION.messenger(JOKE.random_loading_message())
    SOUND.play_sound("{0}\\{1}".format(ENVIRONMENT.AUDIO_FOLDER, random.choice(fun_sounds)))


def greeting_may_force():
    """Display Star Wars Day greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_may_force_dates(year)
    
    if not HolidayDateChecker.is_valid_date(start, end):
        return

    display_greeting(
        image_name="may_force.jpg",
        title_text="Happy Star Wars Day: May the Force be with you!",
        sound_file="sound_effect_mario_powerup.wav"  # Use a fun sound for Star Wars Day
    )


def greeting_pi():
    """Display Pi Day greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_pi_day_dates(year)
    
    if not HolidayDateChecker.is_valid_date(start, end):
        return

    display_greeting(
        image_name="pi_day.jpeg",
        title_text="Happy Pi Day: 3.14",
        sound_file="sound_effect_happy_bell.wav"
    )


def greeting_xmas():
    """Display Christmas greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_xmas_dates(year)
    
    if not HolidayDateChecker.is_valid_date(start, end):
        return

    display_greeting(
        image_name="xmax_tree_drawing.png",
        title_text="Merry Christmas!",
        sound_file="holiday_xmas.wav"  # Updated to use the correct holiday sound file
    )


def greeting_chinese_new_year():
    """Display Chinese New Year greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_chinese_new_year_dates(year)
    
    if not start or not HolidayDateChecker.is_valid_date(start, end):
        return
    
    # All available dragon year images
    dragon_images = [
        "YEAR OF DRAGON_1.png",
        "YEAR OF DRAGON_2.png",
        "YEAR OF DRAGON_3.png",
        "YEAR OF DRAGON_4.png",
        "YEAR OF DRAGON_5.png",
        "YEAR OF DRAGON_6.png"
    ]
    
    # For 2023, display the rabbit image instead
    if year == 2023:
        display_greeting(
            image_name="YEAR OF BUNNY.png",
            title_text="Happy Chinese New Year!",
            sound_file="holiday_chinese_new_year.wav"  # Updated to use the correct holiday sound file
        )
    else:
        # Use the list of dragon images for random selection
        display_greeting(
            image_name=dragon_images,
            title_text="Happy Chinese New Year!",
            sound_file="holiday_chinese_new_year.wav"  # Updated to use the correct holiday sound file
        )


def greeting_mid_moon():
    """Display Mid-Autumn Festival greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_mid_autumn_dates(year)
    
    if not start or not HolidayDateChecker.is_valid_date(start, end):
        return

    # Use the display_greeting function for consistency
    display_greeting(
        image_name="mid moon.jpg",
        title_text="Happy Mid-Autumn Festival!"
    )
    
    # Additional moon cake image
    output = OUTPUT.get_output()
    output.write("## Also known as the Moon-Festival, it is a family reunion holiday shared in many east asian culture.", OUTPUT.Style.Subtitle)
    output.write("## An important part is the moon-cake. You may find the technical drawing below.", OUTPUT.Style.Subtitle)
    
    moon_cake_image = "holiday_moon-cake-drawing.png"
    moon_cake_image_file = "{0}\\{1}".format(ENVIRONMENT.IMAGE_FOLDER, moon_cake_image)
    output.write(moon_cake_image_file)
    
    output.plot()
    
    SOUND.play_sound("{0}\\{1}".format(ENVIRONMENT.AUDIO_FOLDER, "holiday_chinese_new_year.wav"))

    # Occasional export to HTML
    if random.random() > 0.2:
        return
        
    dest_file = FOLDER.get_EA_dump_folder_file("Moon Festival.html")
    try:
        output.save_contents(dest_file)
        output.close()
        os.startfile(dest_file)
    except Exception:
        # Handle errors more generically for Python 2 compatibility
        pass


def greeting_halloween():
    """Display Halloween greeting."""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_halloween_dates(year)
    
    if not HolidayDateChecker.is_valid_date(start, end):
        return
    
    # Use duck images for fun Halloween greeting
    halloween_images = [
        "duck.png",
        "duck_pop_green_bg.png",
        "duck_pop_green_bg2.png"
    ]
    
    # Duck-themed Halloween greeting
    display_greeting(
        image_name=halloween_images,
        title_text="Happy Halloween!",
        sound_file="sound_effect_duck.wav",
        md_text="## Trick or Treat! The EnneadTab duck is here to spook you!"
    )


if __name__ == "__main__":
    festival_greeting()
