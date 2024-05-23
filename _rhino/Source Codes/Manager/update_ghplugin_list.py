import sys
sys.path.append("..\lib")
import EnneadTab
import json
import os
import time


def update_gh_plugins_list(directory):
    latest_versions = {}
    latest_versions["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    for plugin in os.listdir(directory):
        if plugin.startswith('00_'):
            continue
        else:
            plugin_path = os.path.join(directory, plugin)
            if os.path.isdir(plugin_path):
                versions = os.listdir(plugin_path)
                # Version folders must be named with numbers only (i.e. 1.0.0)
                versions.sort()
                latest_versions[plugin] = versions[-1] if versions else None
    json_file_path = "{}\\{}.json".format(
        directory, "00_" + directory.split("\\")[-1])
    with open(json_file_path, 'w') as json_file:
        json.dump(latest_versions, json_file, indent=4)


def update_gh_userobjects_list(directory):
    latest_versions = {}
    latest_versions["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    for plugin in os.listdir(directory):
        if plugin.startswith('00_'):
            continue
        else:
            plugin_path = os.path.join(directory, plugin)
            if os.path.isdir(plugin_path):
                user_objects = os.listdir(plugin_path)
                latest_versions[plugin] = user_objects if user_objects else None
    json_file_path = "{}\\{}.json".format(
        directory, "00_" + directory.split("\\")[-1])
    with open(json_file_path, 'w') as json_file:
        json.dump(latest_versions, json_file, indent=4)


if __name__ == "__main__":

    root_directories = [
        "L:\\4b_Applied Computing\\04_Grasshopper\\000_PLUGINS\\EA Standard Grasshopper Plugins\\EnneadPlugins-gha",
        "L:\\4b_Applied Computing\\04_Grasshopper\\000_PLUGINS\\EA Standard Grasshopper User Objects\\EnneadUserObjects-ghuser"
    ]

    update_gh_plugins_list(root_directories[0])
    update_gh_userobjects_list(root_directories[1])
