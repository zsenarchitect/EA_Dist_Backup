#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Display encouraging messages."""

import io
import random
import textwrap


import NOTIFICATION
import DOCUMENTATION
import ENVIRONMENT
import CONFIG

def is_hate_encouraging():
    """Check if the user has enabled encouraging messages.

    Returns:
        bool: True if the user has enabled encouraging messages.
    """
    return not CONFIG.get_setting("radio_bt_popup_full", False)

def get_all_warming_quotes():
    """Get all encouraging quotes from the quote library.

    Returns:
        list: All encouraging quotes.
    """
    with io.open(DOCUMENTATION.get_text_path_by_name('_warming_quotes.txt'), "r", encoding = "utf8") as f:
        lines = f.readlines()
    return [x.replace("\n", "") for x  in lines if x != "\n"]


def random_warming_quote():
    """Get a random encouraging quote from the quote library.

    Returns:
        str: A random encouraging quote
    """
    lines = get_all_warming_quotes()
    random.shuffle(lines)
    return lines[0].replace("\n", "")


def warming_quote():
    """Display a random encouraging quote.
    """
    quote = random_warming_quote()
    

    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = quote, animation_stay_duration = 10)
