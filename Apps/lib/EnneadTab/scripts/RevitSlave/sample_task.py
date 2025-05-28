"""
sample_task.py

Defines a sample task for RevitSlave that prints the title of the Revit document.
This is your friendly greeter for every model in the batch!
"""

from .models import RevitModel


def print_title_task(model: RevitModel, **kwargs) -> bool:
    """
    Prints the title (name) of the Revit document/model.

    Args:
        model (RevitModel): The model to print the title for.
    Returns:
        bool: Always True (task succeeded).
    """
    print(f"Document Title: {model.name}")
    return True 