
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT

if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc





def get_rhino_project_data():
    """Retrieve project data from document dictionary.
    
    Returns:
        dict: Project data dictionary from document dictionary
    """
    pass


def set_rhino_project_data(data):
    """Save project data to document dictionary.
    
    Args:
        data: Dictionary containing project data to save
    """
    pass






