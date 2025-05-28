"""
data_utils.py

Utility functions for parsing and handling Revit model data.
"""

import json
from typing import Iterator, Dict, Any


def iter_valid_model_dicts(data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    """
    Yields only valid model dictionaries from the provided data.

    Skips any entries where the value is a list (since version info can't be parsed).
    This function is your trusty bouncer at the data club—lists need not apply!

    Args:
        data (dict): The loaded JSON data.

    Yields:
        dict: Model data dictionaries with version info.
    """
    for key, value in data.items():
        if isinstance(value, dict) and "revit_version" in value:
            yield value 