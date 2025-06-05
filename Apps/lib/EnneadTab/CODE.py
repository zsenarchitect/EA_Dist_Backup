#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Code editing and remote debugging utilities for EnneadTab.

This module provides functionality for emergency code fixes and remote editing
using VS Code Dev (https://vscode.dev/), supporting both CPython and IronPython 2.7.

Key Features:
- Remote code editing through VS Code Dev
- Cross-platform compatibility (CPython/IronPython)
- Emergency code fix capabilities
"""

import os
import sys
import webbrowser

import ENVIRONMENT
import NOTIFICATION


def is_ironpython():
    """Check if running under IronPython.
    
    Returns:
        bool: True if running under IronPython, False otherwise
    """
    return sys.platform == "cli" or "IronPython" in sys.version


def emergency_fix_code():
    """Launch emergency code fix interface.
    
    This function provides a quick way to access remote editing capabilities
    for fixing code issues, especially useful when local development environment
    has problems.
    """
    print("=== EnneadTab Emergency Code Fix ===")
    print("Python Version: {}".format(sys.version))
    print("Platform: {}".format(sys.platform))
    print("IronPython: {}".format(is_ironpython()))
    
    try:
        # Open VS Code Dev
        print("Opening VS Code Dev for remote editing...")
        webbrowser.open("https://vscode.dev/")
        
        # Show notification
        NOTIFICATION.duck_pop("Emergency Code Fix launched!\nVS Code Dev is now open in your browser.")
        
    except Exception as e:
        print("Emergency code fix failed: {}".format(str(e)))


def unit_test():
    """Run unit tests for the CODE module."""
    print("=== CODE Module Unit Test ===")
    
    # Test environment detection
    print("IronPython check: {}".format(is_ironpython()))
    print("Python version: {}".format(sys.version))
    
    print("Unit test completed")


if __name__ == "__main__":
    emergency_fix_code()
