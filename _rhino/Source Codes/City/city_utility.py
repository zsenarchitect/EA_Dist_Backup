#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('..\lib')
import EnneadTab


MAIN_FOLDER = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\EnneadCity"
USER_DATA_FILE = r"{}\city_setting.json".format(MAIN_FOLDER)
PLOT_FILES_FOLDER = r"{}\plots".format(MAIN_FOLDER)
CITY_SOURCE_FILE = r"{}\City_Source.3dm".format(MAIN_FOLDER)
CITY_BACKGROUND_FILES = [r"{}\City_Background_Road.3dm".format(MAIN_FOLDER)]


def get_city_data():
    if not os.path.exists(USER_DATA_FILE):
        print("Create empty user data file")
        EnneadTab.DATA_FILE.save_dict_to_json(dict(), USER_DATA_FILE)
    return EnneadTab.DATA_FILE.read_json_as_dict(USER_DATA_FILE)


def get_current_user_plot_file():

    user_name = EnneadTab.USER.get_user_name()
    user_data = get_city_data()
    if user_name not in user_data:
        return False

    return user_data[user_name]["plot_file"]


def set_current_user_plot_file(plot_file):
    user_name = EnneadTab.USER.get_user_name()
    user_data = get_city_data()
    # print user_data
    if user_name not in user_data.keys():
        user_data[user_name] = dict()
    user_data[user_name]["plot_file"] = plot_file
    # print plot_file
    # print user_data
    EnneadTab.DATA_FILE.save_dict_to_json(user_data, USER_DATA_FILE)


def get_all_plot_files():
    return ["{}\{}".format(PLOT_FILES_FOLDER, plot_file) for plot_file in EnneadTab.FOLDER.get_filenames_in_folder(PLOT_FILES_FOLDER) if plot_file.endswith(".3dm")]


def get_empty_plot_files():
    used_plots = get_occupied_plot_files()
    return [plot_file for plot_file in get_all_plot_files() if plot_file not in used_plots]


def get_occupied_plot_files():
    user_data = get_city_data()
    return [user_data[user_name]["plot_file"] for user_name in user_data]


def get_occupied_plot_names():
    used_plots = get_occupied_plot_files()
    return [os.path.split(x)[1].replace(".3dm", "") for x in used_plots]
