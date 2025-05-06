"""Comprehensive test suite for EnneadTab's ENGINE.py module.

This script tests all major functionality of the ENGINE module:
1. Executing Python scripts
2. Automatic module installation
3. Handling built-in modules
4. Error diagnostics and reporting
"""

import os
import sys
import time
import ENGINE
import ENVIRONMENT

def test_standard_execution():
    """Test basic script execution with standard library modules."""
    print("\n1. TESTING STANDARD EXECUTION")
    print("============================")
    
    test_script = """
import os
import sys
import datetime
import json
import random

print("Standard library modules imported successfully.")
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current time:", datetime.datetime.now())
print("Random number:", random.randint(1, 100))
"""
    
    test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "standard_test.py")
    with open(test_file, "w") as f:
        f.write(test_script)
    
    print("Running standard library test...")
    success, stdout, stderr = ENGINE.cast_python(test_file, wait=True)
    
    print("Success:", success)
    print("Output:", stdout)
    if stderr:
        print("Errors:", stderr)
    
    if os.path.exists(test_file):
        os.remove(test_file)

def test_module_installation():
    """Test automatic installation of missing modules."""
    print("\n2. TESTING MODULE INSTALLATION")
    print("=============================")
    
    test_script = """
import os
import sys

# This should trigger auto-installation if not present
print("Attempting to import requests...")
import requests
print("Successfully imported requests!")
print("Requests version:", requests.__version__)

# Try a real HTTP request
print("Making HTTP request to google.com...")
response = requests.get("https://www.google.com")
print("Response status:", response.status_code)
"""
    
    test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "module_install_test.py")
    with open(test_file, "w") as f:
        f.write(test_script)
    
    print("Running module installation test...")
    success, stdout, stderr = ENGINE.cast_python(test_file, wait=True)
    
    print("Success:", success)
    print("Output:", stdout)
    if stderr:
        print("Errors:", stderr)
    
    if os.path.exists(test_file):
        os.remove(test_file)

def test_builtin_module_handling():
    """Test handling of built-in modules that can't be installed via pip."""
    print("\n3. TESTING BUILT-IN MODULE HANDLING")
    print("=================================")
    
    test_script = """
import os
import sys

# This should trigger a special error message
print("Attempting to import tkinter...")
import tkinter
print("Successfully imported tkinter!")
"""
    
    test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "builtin_test.py")
    with open(test_file, "w") as f:
        f.write(test_script)
    
    print("Running built-in module test...")
    success, stdout, stderr = ENGINE.cast_python(test_file, wait=True)
    
    print("Success:", success)
    print("Output:", stdout)
    if stderr:
        print("Errors:", stderr)
    
    if os.path.exists(test_file):
        os.remove(test_file)

def test_diagnostic_tools():
    """Test the diagnostic tools in the ENGINE module."""
    print("\n4. TESTING DIAGNOSTIC TOOLS")
    print("=========================")
    
    print("Engine installed:", ENGINE.ensure_engine_installed())
    
    print("\nRunning engine diagnostics...")
    diagnostics = ENGINE.diagnose_engine_issue()
    
    print("Engine exists:", diagnostics["engine_exists"])
    print("Python.exe exists:", diagnostics["python_exe_exists"])
    print("Lib folder exists:", diagnostics["lib_folder_exists"])
    print("Standard library exists:", diagnostics["standard_library_exists"])
    print("DLL files exist:", diagnostics["dll_files_exist"])
    
    if diagnostics["issues"]:
        print("\nIssues detected:")
        for issue in diagnostics["issues"]:
            print("- " + issue)
    
    if diagnostics["recommendations"]:
        print("\nRecommendations:")
        for rec in diagnostics["recommendations"]:
            print("- " + rec)

if __name__ == "__main__":
    print("COMPREHENSIVE ENGINE.py TEST SUITE")
    print("=================================")
    print("Engine path:", os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe"))
    
    # Test all functionality
    test_standard_execution()
    test_module_installation()
    test_builtin_module_handling()
    test_diagnostic_tools()
    
    print("\nAll tests completed.") 