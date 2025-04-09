#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('..\lib')
from EnneadTab import ENVIRONMENT, DATA_FILE, FOLDER, USER


MAIN_FOLDER = "{}\\EnneadCity".format(ENVIRONMENT.DB_FOLDER)
USER_DATA_FILE = "{}\\city_setting".format(MAIN_FOLDER)
PLOT_FILES_FOLDER = "{}\\plots".format(MAIN_FOLDER)
CITY_SOURCE_FILE = "{}\\City_Source.3dm".format(MAIN_FOLDER)
CITY_BACKGROUND_FILES = ["{}\\City_Background_Road.3dm".format(MAIN_FOLDER)]


def get_city_data():
    if not os.path.exists(USER_DATA_FILE):
        print("Create empty user data file")
        DATA_FILE.save_dict_to_json(dict(), USER_DATA_FILE)
    return DATA_FILE.read_json_as_dict(USER_DATA_FILE)


def get_current_user_plot_file():

    user_name = USER.USER_NAME
    user_data = get_city_data()
    if user_name not in user_data:
        return False

    return user_data[user_name]["plot_file"]


def set_current_user_plot_file(plot_file):
    user_name = USER.USER_NAME
    user_data = get_city_data()
    # print user_data
    if user_name not in user_data.keys():
        user_data[user_name] = dict()
    user_data[user_name]["plot_file"] = plot_file
    # print plot_file
    # print user_data
    DATA_FILE.save_dict_to_json(user_data, USER_DATA_FILE)


def get_all_plot_files():
    return ["{}\{}".format(PLOT_FILES_FOLDER, plot_file) for plot_file in FOLDER.get_filenames_in_folder(PLOT_FILES_FOLDER) if plot_file.endswith(".3dm")]


def get_empty_plot_files():
    used_plots = get_occupied_plot_files()
    return [plot_file for plot_file in get_all_plot_files() if plot_file not in used_plots]


def get_occupied_plot_files():
    user_data = get_city_data()
    return [user_data[user_name]["plot_file"] for user_name in user_data]


def get_occupied_plot_names():
    used_plots = get_occupied_plot_files()
    return [os.path.split(x)[1].replace(".3dm", "") for x in used_plots]
