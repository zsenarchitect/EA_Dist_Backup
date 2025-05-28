"""
task_template.py

Defines the RevitTask class for managing Revit automation tasks.
"""

from typing import Dict, List

class RevitTask:
    """
    Represents a task to be performed on a Revit model.

    Attributes:
        model_data (dict): The model's metadata.
        scripts (list): List of script names to run.
    """
    def __init__(self, model_data: Dict, scripts: List[str]):
        self.model_data = model_data
        self.scripts = scripts 