import os
import sys
import json
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT

if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc



class DocKeys:
    """standardlize the keys for the document data"""
    PreferredGrasshopperFile = "Preferred Grasshopper File"
    GrasshopperInput = "Grasshopper Input"
    

def inspect_document_data():
    """Print all document data sections and entries in the current Rhino file.
    
    Displays data in format: [section]entry : value
    Returns None if no document data is found.
    """
    if not rs.IsDocumentData():
        print ("No document data found")
        return 
    all_sections = rs.GetDocumentData()
    for section in all_sections:
        all_entries = rs.GetDocumentData(section)
        for entry in all_entries:
            print ("[{}]{} : {}".format(section, entry, rs.GetDocumentData(section, entry)))


def get_rhino_project_data():
    """Retrieve and parse all document data from the current Rhino file.
    
    Returns:
        dict: Nested dictionary containing all document data organized by sections.
            Structure: {section: {entry: value}}
            Values are automatically parsed in following order:
            1. JSON dictionary
            2. Boolean (true/false)
            3. Numeric (float/integer)
            4. String (default)
            
        Returns empty dict if no document data exists.
    """
    if not rs.IsDocumentData():
        return dict()

    data = dict()
    all_sections = rs.GetDocumentData()
    for section in all_sections:
        data[section] = dict()  # Initialize nested dictionary for each section
        all_entries = rs.GetDocumentData(section)
        for entry in all_entries:
            value = rs.GetDocumentData(section, entry)
            try:
                # Try parsing as JSON (dict)
                value = json.loads(value)
            except:
                # Try parsing as bool
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                else:
                    try:
                        # Try parsing as float
                        value = float(value)
                        # Convert to int if no decimal places
                        if value.is_integer():
                            value = int(value)
                    except:
                        # Keep as string if all other parsing fails
                        pass
            data[section][entry] = value
    return data


def set_rhino_project_data(data):
    """Store project data into the Rhino document dictionary.
    
    Args:
        data (dict): Nested dictionary containing project data to save.
            Expected structure: {section: {entry: value}}
            Dictionary values are automatically converted to JSON strings.
            All other values are converted to strings.
    """
    for section in data:
        for entry in data[section]:
            value = data[section][entry]
            if isinstance(value, dict):
                value = json.dumps(value)
            else:
                value = str(value)
            rs.SetDocumentData(section, entry, value)



def get_enneadtab_data():
    """Retrieve EnneadTab-specific data from the document dictionary.
    
    Returns:
        dict: Dictionary containing EnneadTab data.
            Returns empty dict if no EnneadTab section exists.
    """
    data = get_rhino_project_data()
    return data.get("EnneadTab", dict())


def set_enneadtab_data(data):
    """Store EnneadTab-specific data in the document dictionary.
    
    Args:
        data (dict): Dictionary containing EnneadTab data to save.
            Data will be stored under the 'EnneadTab' section.
            Existing EnneadTab data will be overwritten.
    """
    project_data = get_rhino_project_data()
    project_data["EnneadTab"] = data
    set_rhino_project_data(project_data)


