#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)


from EnneadTab import FOLDER

def random_loading_message():
    """get some fun message for loading screen

    Returns:
        str: a random line of funny message
    """
    import random
    with open('{}\_loading_screen_message.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    return lines[0].replace("\n", "")
