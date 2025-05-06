"""Test EnneadTab's ENGINE.py module functionality.

This script demonstrates how to use ENGINE.py to execute Python scripts 
with automatic dependency installation.
"""

import os
import sys
import ENGINE
import ENVIRONMENT

def test_auto_install():
    """Test the auto-module installation functionality."""
    print("\nTESTING AUTO-INSTALL FUNCTIONALITY")
    print("==================================")
    
    # Create a test script that imports a module that might not be installed
    test_script = """
import os
import sys
print("Python executable:", sys.executable)

# This should trigger auto-installation if not present
print("\\nTrying to import requests...")
import requests
print("Successfully imported requests!")
print("Requests version:", requests.__version__)

# Try a real HTTP request
print("\\nMaking HTTP request to google.com...")
response = requests.get("https://www.google.com")
print("Response status:", response.status_code)
"""
    
    # Write the test script to a temporary file
    test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "auto_install_test.py")
    with open(test_file, "w") as f:
        f.write(test_script)
    
    # Try to execute the script
    print("Running test script...")
    success, stdout, stderr = ENGINE.cast_python(test_file, wait=True)
    
    print("\nRESULTS:")
    print("Success:", success)
    print("\nOutput:", stdout)
    
    if stderr:
        print("\nErrors:", stderr)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    print("ENGINE.py TEST UTILITY")
    print("======================")
    print("Engine path:", os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe"))
    print("Engine exists:", ENGINE.ensure_engine_installed())
    
    # Test auto-install functionality
    test_auto_install() 