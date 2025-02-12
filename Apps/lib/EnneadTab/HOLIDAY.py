# https://python-holidays.readthedocs.io/en/latest/index.html

"""Used to make customized greetings for all the employees in the office."""

import datetime


try:
    from pyrevit import script
except:
    pass

import os
import sys
import random


import FOLDER
import EXE
import SOUND
import ENVIRONMENT
import NOTIFICATION


class HolidayDateChecker:
    """Utility class to check holiday dates for any year"""
    
    @staticmethod
    def is_valid_date(start_date, end_date):
        """
        Check if current date falls within the given range
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
        """Get Chinese New Year celebration period for given year"""
        # Dates from Chinese calendar (approximate, can be adjusted)
        dates = {
            2024: (datetime.date(2024, 2, 10), datetime.date(2024, 2, 24)),  # Year of Dragon
            2025: (datetime.date(2025, 1, 29), datetime.date(2025, 2, 8)),  # Year of Snake
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
        """Get Mid-Autumn Festival dates for given year"""
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
        """Get Christmas celebration period"""
        return (
            datetime.date(year, 12, 20),
            datetime.date(year, 12, 31)
        )

    @staticmethod
    def get_pi_day_dates(year):
        """Get Pi Day celebration period"""
        return (
            datetime.date(year, 3, 14),
            datetime.date(year, 3, 14)
        )

    @staticmethod
    def get_april_fools_dates(year):
        """Get April Fools' Day celebration period"""
        return (
            datetime.date(year, 4, 1),
            datetime.date(year, 4, 1)
        )

    @staticmethod
    def get_may_force_dates(year):
        """Get Star Wars Day celebration period"""
        return (
            datetime.date(year, 5, 4),
            datetime.date(year, 5, 4)
        )

def festival_greeting():
    """Check and display greetings for all holidays"""
    year = datetime.datetime.now().year
    checker = HolidayDateChecker()
    
    # Chinese New Year
    start, end = checker.get_chinese_new_year_dates(year)
    if start and checker.is_valid_date(start, end):
        greeting_chinese_new_year()
    
    # Mid-Autumn Festival
    start, end = checker.get_mid_autumn_dates(year)
    if start and checker.is_valid_date(start, end):
        greeting_mid_moon()
    
    # Christmas
    start, end = checker.get_xmas_dates(year)
    if checker.is_valid_date(start, end):
        greeting_xmas()
    
    # Pi Day
    start, end = checker.get_pi_day_dates(year)
    if checker.is_valid_date(start, end):
        greeting_pi()
    
    # April Fools' Day
    start, end = checker.get_april_fools_dates(year)
    if checker.is_valid_date(start, end):
        greeting_april_fools()
    
    # Star Wars Day
    start, end = checker.get_may_force_dates(year)
    if checker.is_valid_date(start, end):
        greeting_may_force()

def greeting_april_fools():
    if not HolidayDateChecker.is_valid_date((2024, 3, 31), (2024, 4, 1)):
        return

    import JOKE

    for _ in range(random.randint(1, 5)):
        JOKE.prank_dvd()

    NOTIFICATION.messenger(JOKE.random_loading_message())


def greeting_may_force():
    if not HolidayDateChecker.is_valid_date((2024, 5, 1), (2024, 5, 6)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    image = "may_force.jpg"

    image_file = "{}\\{}".format(
        ENVIRONMENT.IMAGE_FOLDER, image
    )
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    return
    file = "sound effect_xmas_hohoho.wav"
    SOUND.play_sound(file)


def greeting_pi():
    if not HolidayDateChecker.is_valid_date((2024, 3, 13), (2024, 3, 15)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    image = "pi_day.jpeg"

    image_file = "{}\\{}".format(
        ENVIRONMENT.IMAGE_FOLDER, image
    )
    output = script.get_output()
    output.print_image(image_file)
    output.print_md("#Happy Pi Day: 3.14")
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    return
    file = "sound effect_xmas_hohoho.wav"
    SOUND.play_sound(file)


def greeting_xmas():
    if not HolidayDateChecker.is_valid_date((2023, 12, 20), (2024, 1, 3)):
        return

    # this will make every year 12-20-12-31 xmax
    # _, m, d = TIME.get_date_as_tuple()
    # if m != 12 or d < 20:
    #     return

    image = "xmax_tree_drawing.png"

    image_file = "{}\\{}".format(
        ENVIRONMENT.IMAGE_FOLDER, image
    )
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    file = "sound_effect_xmas_hohoho.wav"
    SOUND.play_sound(file)


def greeting_chinese_new_year():
    """Display Chinese New Year greeting"""
    year = datetime.datetime.now().year
    start, end = HolidayDateChecker.get_chinese_new_year_dates(year)
    if not start or not HolidayDateChecker.is_valid_date(start, end):
        return
        
    image = "YEAR OF DRAGON.png"  # Update image name based on year
    image_file = "{}\{}".format(ENVIRONMENT.IMAGE_FOLDER, image)
    
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(900)
    output.set_height(700)
    output.center()
    output.set_title("Greeting from EnneadTab")

    file = "sound effect_chinese_new_year.wav"
    SOUND.play_sound(file)


def greeting_mid_moon():
    d0 = datetime.datetime(2023, 9, 28)
    today = datetime.datetime.now()
    d1 = datetime.datetime(2023, 10, 10)

    if not (d0 < today < d1):
        return

    image = "mid moon.jpg"
    image_file = __file__.split("ENNEAD.extension")[
        0
    ] + "ENNEAD.extension\\bin\{}".format(image)

    image = "moon-cake-drawing.png"
    moon_cake_image_file = __file__.split("ENNEAD.extension")[
        0
    ] + "ENNEAD.extension\\bin\{}".format(image)

    # print image_file
    output = script.get_output()
    output.print_image(image_file)
    output.set_width(1200)
    output.set_height(900)
    output.self_destruct(100)
    output.center()
    output.set_title("Greeting from EnneadTab")
    output.print_md("# Happy Mid-Autumn Festival, everybody!")
    output.print_md(
        "## Also known as the Moon-Festival, it is a family reunion holiday shared in many east asian culture."
    )
    output.print_md(
        "## An important part is the moon-cake. You may find the technical drawing below."
    )
    output.print_image(moon_cake_image_file)

    file = "sound effect_chinese_new_year.wav"
    SOUND.play_sound(file)

    if random.random() > 0.2:
        return
    dest_file = FOLDER.get_EA_dump_folder_file("Moon Festival.html")
    output.save_contents(dest_file)
    output.close()
    os.startfile(dest_file)


if __name__ == "__main__":
    festival_greeting()
