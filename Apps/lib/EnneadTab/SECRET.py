#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities for referencing secrets, such as API keys and developer identity information."""

import os
import DATA_FILE
import ENVIRONMENT
import NOTIFICATION

import json


def get_acc_key_data():
    api_key_file = "ACC_API_KEY.secret"
    L_drive_file_path = os.path.join(ENVIRONMENT.DB_FOLDER, api_key_file)
    if ENVIRONMENT.IS_OFFLINE_MODE:
        data = DATA_FILE.get_data(api_key_file)
        if not data:
            NOTIFICATION.messenger("API key file not found, do you have L drive connection?")
    else:
        data = DATA_FILE.get_data(L_drive_file_path)

    return data


def get_openai_api_key(app_name):
    """Returns the API key for the specified app.
    Accepted keys:
    "EnneadTabAPI"
    # "chatgpt_api_key"
    # "translator_api_key"
    # "reporter_api_key"
    # "clone_helper"
    # "miro_oauth"

    Args:
        app_name (string): The name of the app to get the API key for.

    Returns:
        string: The API key for the specified app.
    """
    api_key_file = "EA_API_KEY.secret"
    L_drive_file_path = os.path.join(ENVIRONMENT.DB_FOLDER, api_key_file)
    if ENVIRONMENT.IS_OFFLINE_MODE:
        data = DATA_FILE.get_data(api_key_file)
        if not data:
            NOTIFICATION.messenger("API key file not found, do you have L drive connection?")
    else:
        data = DATA_FILE.get_data(L_drive_file_path)

    
    # Try to get value from specified app_name first, fallback to any key if not found
    for key in data:
        if key == app_name:
            return data[key]
    return next(iter(data.values()), None)


def get_dev_info(developer_name, key):
    """Get developer information from the secret file.

    Args:
        developer_name (string): The name of the developer.
        key (string): The key to get the value for.

    Returns:
        string: The value of the key for the developer.
    """
    data = get_dev_dict()
    developer_data = data.get(developer_name)
    if not developer_data:
        return
    return developer_data.get(key)


def get_dev_dict():
    """Get the dictionary of developers from the secret file.

    Returns:
        dict: The dictionary of developers.
    """
    developer_file = "ENNEADTAB_DEVELOPERS.secret"
    L_drive_file_path = os.path.join(ENVIRONMENT.DB_FOLDER, developer_file)
    if ENVIRONMENT.IS_OFFLINE_MODE:
        return DATA_FILE.get_data(developer_file)
    return DATA_FILE.get_data(L_drive_file_path)



def unit_test():
    """Unit test for the SECRET module."""
    import pprint
    
    app_names = [
        "EnneadTabAPI"
    ]

    print("######### API KEY TEST #########")
    for app_name in app_names:
        print("{name}: {key}".format(name=app_name, key=get_openai_api_key(app_name)))
    print("######### DEV DICT TEST #########")
    pprint.pprint(get_dev_dict())
    print("######### DEV INFO TEST #########")
    for dev_name in get_dev_dict().keys():
        for key in get_dev_dict()[dev_name].keys():
            print(
                "{dev_name}: {key}: {value}".format(
                    dev_name=dev_name, key=key, value=get_dev_info(dev_name, key)
                )
            )



if __name__ == "__main__":
    pass
