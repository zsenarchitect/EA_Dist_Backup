__title__ = "InspectEnscapeSetting"
__doc__ = "Inspect and compare Enscape setting files for differences"


import rhinoscriptsyntax as rs
import os
import json
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import FOLDER
from EnneadTab import ENVIRONMENT


def inspect_setting_file(path):
    """Extract settings from an Enscape setting file.
    
    Args:
        path (str): Path to the Enscape setting file
        
    Returns:
        list: List of tuples containing (setting_name, setting_value)
    """
    settings = []
    with open(path) as f:
        data = json.load(f)
        
        for key in sorted(data.keys()):
            if isinstance(data[key], int):
                settings.append((key, data[key]))
                continue
            
            if not data[key].values():
                settings.append((key, "???"))
                continue
            
            for inner_key in sorted(data[key].keys()):
                settings.append((inner_key, data[key][inner_key]["Value"]))

    return settings


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def inspect_enscape_setting():
    """Compare multiple Enscape setting files and report differences.
    
    Opens a file dialog to select Enscape setting files, then compares
    their settings and displays any differences found.
    """
    # Get files to compare
    file_collection = list(rs.OpenFileNames(
        filter="Enscape setting file|*.{}".format(ENVIRONMENT.PLUGIN_EXTENSION)
    ))
    
    if not file_collection:
        return
        
    # Extract settings from each file
    detail_collection = [inspect_setting_file(x) for x in file_collection]
    file_names = [
        FOLDER.get_file_name_from_path(x).replace(ENVIRONMENT.PLUGIN_EXTENSION, "")
        for x in file_collection
    ]
    
    # Check for invalid settings
    for i, settings in enumerate(detail_collection):
        if "???" in str(settings):
            rs.MessageBox(
                "<{}> has some invalid or empty settings. "
                "Check the .json file with a text editor.".format(file_names[i])
            )
            return
    
    # Compare settings and build output
    output = ""
    for item in zip(*detail_collection):
        if all(x == item[0] for x in item):
            continue
            
        output += "\n\nThere are different settings detected in <{}>".format(item[0][0])
        for i, content in enumerate(item):
            output += "\n\t\t[ {} ]: {}".format(file_names[i], content[1])
    
    if output:
        rs.TextOut(output)
    else:
        rs.MessageBox("No differences found between the selected setting files.")


if __name__ == "__main__":
    inspect_enscape_setting()   