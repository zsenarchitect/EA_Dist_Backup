import subprocess
import os
import sys
import re


import ENVIRONMENT

"""Python Engine Management for EnneadTab.

This module provides functionality to run Python scripts using the embedded Python engine 
in the _engine folder, allowing scripts to be executed on computers without Python installed.

Key Features:
- Script execution using the embedded Python engine
- Path resolution for script files
- Error handling and diagnostic capabilities
- Automatic module installation for missing dependencies

Designed to work in IronPython environments and distribute with the EnneadTab package,
enabling Python 3 functionality without requiring Python installation on the host machine.

Usage:
    import ENGINE
    
    # Run a script by path
    success, stdout, stderr = ENGINE.cast_python("path/to/script.py", wait=True)
    
    # Or by name (will look in APP_FOLDER)
    success, stdout, stderr = ENGINE.cast_python("Messenger", wait=True)
    
    # Check if Python engine is available
    is_available = ENGINE.ensure_engine_installed()
    
    # Get information about a Python engine issue
    error_info = ENGINE.diagnose_engine_issue()
"""

# Special case modules that are built-in and can't be installed via pip
BUILTIN_MODULES = {
    "tkinter": "Tkinter is a built-in module that comes with Python. If missing, it's likely because you're using an embedded Python without UI components.",
    "_tkinter": "The _tkinter module is a built-in module that comes with Python. If missing, it's likely because you're using an embedded Python without UI components.",
    "tk": "The tk module is part of tkinter, a built-in module that comes with Python."
}

def install_module(module_name):
    """Install a Python module using pip into the engine's site-packages folder.
    
    Args:
        module_name (str): Name of the module to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    # Check if it's a built-in module that can't be installed
    if module_name in BUILTIN_MODULES:
        print("Note: {} cannot be installed via pip. {}".format(
            module_name, BUILTIN_MODULES[module_name]))
        return False
    
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    
    if not os.path.exists(engine_path):
        return False
    
    # Make sure pip is available
    ensure_pip_installed()
    
    # Set up environment variables
    env = os.environ.copy()
    env["PYTHONHOME"] = ENVIRONMENT.ENGINE_FOLDER
    
    # Install the module
    try:
        process = subprocess.Popen(
            [engine_path, "-m", "pip", "install", module_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=ENVIRONMENT.ENGINE_FOLDER
        )
        
        stdout, stderr = process.communicate()
        return process.returncode == 0
    except Exception as e:
        print("Error installing module {}: {}".format(module_name, str(e)))
        return False

def ensure_pip_installed():
    """Ensure pip is installed in the engine environment.
    
    Returns:
        bool: True if pip is available, False otherwise
    """
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    
    # Check if pip is already installed
    env = os.environ.copy()
    env["PYTHONHOME"] = ENVIRONMENT.ENGINE_FOLDER
    
    try:
        process = subprocess.Popen(
            [engine_path, "-m", "pip", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=ENVIRONMENT.ENGINE_FOLDER
        )
        
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return True
    except:
        pass
    
    # If we get here, pip is not installed or not working
    # Try to enable site packages first
    enable_site_packages()
    
    # Download get-pip.py
    get_pip_path = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "get-pip.py")
    try:
        import urllib.request
        urllib.request.urlretrieve(
            "https://bootstrap.pypa.io/get-pip.py", 
            get_pip_path
        )
    except:
        try:
            # Fallback to using the engine Python to download it
            script = """
import urllib.request
urllib.request.urlretrieve(
    "https://bootstrap.pypa.io/get-pip.py", 
    "{}"
)
""".format(get_pip_path.replace("\\", "\\\\"))
            
            temp_script = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "download_pip.py")
            with open(temp_script, "w") as f:
                f.write(script)
                
            process = subprocess.Popen(
                [engine_path, temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=ENVIRONMENT.ENGINE_FOLDER
            )
            process.communicate()
            
            if not os.path.exists(get_pip_path):
                return False
        except:
            return False
    
    # Run get-pip.py
    try:
        process = subprocess.Popen(
            [engine_path, get_pip_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=ENVIRONMENT.ENGINE_FOLDER
        )
        
        stdout, stderr = process.communicate()
        return process.returncode == 0
    except:
        return False

def enable_site_packages():
    """Enable site-packages import in the embedded Python environment.
    
    For embedded Python, we need to edit the python3X._pth file to uncomment
    import site for pip to work correctly.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Find the _pth file
    pth_files = [f for f in os.listdir(ENVIRONMENT.ENGINE_FOLDER) 
                if f.startswith("python") and f.endswith("._pth")]
    
    if not pth_files:
        return False
    
    pth_file = os.path.join(ENVIRONMENT.ENGINE_FOLDER, pth_files[0])
    
    try:
        with open(pth_file, "r") as f:
            content = f.read()
            
        # Uncomment the import site line if it's commented
        if "#import site" in content:
            content = content.replace("#import site", "import site")
            
            with open(pth_file, "w") as f:
                f.write(content)
        
        return True
    except:
        return False

def extract_module_name(error_text):
    """Extract the missing module name from a ModuleNotFoundError message.
    
    Args:
        error_text (str): Error message from Python
        
    Returns:
        str or None: The name of the missing module, or None if not found
    """
    # Pattern for standard ModuleNotFoundError
    pattern = r"No module named ['\"]([^'\"]+)['\"]"
    match = re.search(pattern, error_text)
    
    if match:
        return match.group(1)
    
    return None

def cast_python(script, wait=False, max_install_attempts=3):
    """Run a Python script using the embedded Python engine from ENVIRONMENT.ENGINE_FOLDER.
    
    Executes the specified script file using the Python interpreter located
    in the configured engine folder. Captures and returns output/errors.
    If a ModuleNotFoundError is detected, the function will attempt to install
    the missing module and retry the script execution.
    
    Args:
        script (str): Path to the Python script to execute
        wait (bool): When True, waits for the process to complete before returning
        max_install_attempts (int): Maximum number of attempts to install missing modules
        
    Returns:
        tuple: (success, stdout, stderr) indicating execution result and output
    """
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    
    # Check if engine exists
    if not os.path.exists(engine_path):
        return False, "", "Python engine not found at: {}".format(engine_path)
    
    # If script is just a name without path, look for it in APP_FOLDER
    if not os.path.exists(script) and not os.path.isabs(script):
        script_path = os.path.join(ENVIRONMENT.APP_FOLDER, script + ".py")
        if os.path.exists(script_path):
            script = script_path
    
    # Check if script exists
    if not os.path.exists(script):
        return False, "", "Script not found at: {}".format(script)
    
    # Keep track of installed modules to avoid infinite loops
    installed_modules = set()
    attempts = 0
    
    while attempts <= max_install_attempts:
        try:
            # Set up environment variables
            env = os.environ.copy()
            env["PYTHONHOME"] = ENVIRONMENT.ENGINE_FOLDER
            
            # Add site-packages to PYTHONPATH if it exists
            site_packages = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "Lib", "site-packages")
            if os.path.exists(site_packages):
                py_path = env.get("PYTHONPATH", "")
                if py_path:
                    env["PYTHONPATH"] = site_packages + os.pathsep + py_path
                else:
                    env["PYTHONPATH"] = site_packages
            
            # Use Popen to capture output
            process = subprocess.Popen(
                [engine_path, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env,
                cwd=ENVIRONMENT.ENGINE_FOLDER
            )
            
            # If wait is True, wait for completion and capture output
            if wait:
                stdout, stderr = process.communicate()
                success = process.returncode == 0
                
                # If successful, return results
                if success:
                    return success, stdout, stderr
                
                # If there's an error, check if it's a missing module
                module_name = extract_module_name(stderr)
                
                if module_name and "ModuleNotFoundError" in stderr:
                    # Check if it's a built-in module
                    if module_name in BUILTIN_MODULES:
                        message = BUILTIN_MODULES[module_name]
                        stderr += "\n\nNote: {} is a built-in module. {}".format(module_name, message)
                        return success, stdout, stderr
                    
                    # If not built-in and not already tried, attempt to install 
                    if module_name not in installed_modules:
                        # Try to install the missing module
                        print("Attempting to install missing module: {}".format(module_name))
                        
                        if install_module(module_name):
                            print("Successfully installed module: {}".format(module_name))
                            installed_modules.add(module_name)
                            attempts += 1
                            continue
                        else:
                            stderr += "\n\nFailed to install missing module: {}".format(module_name)
                
                # If we get here, either it's not a module error or installation failed
                if "ModuleNotFoundError" in stderr:
                    stderr += "\n\nSome modules could not be installed automatically. Please install them manually."
                
                return success, stdout, stderr
            else:
                # For non-wait mode, just return immediately and assume success
                return True, "", ""
                
        except Exception as e:
            return False, "", "Error executing script: {}".format(str(e))
        
        attempts += 1
    
    return False, "", "Maximum module installation attempts reached. Script could not be executed."

def ensure_engine_installed():
    """Check if the Python engine is properly installed.
    
    Returns:
        bool: True if the engine is available, False otherwise
    """
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    return os.path.exists(engine_path)

def diagnose_engine_issue():
    """Diagnose issues with the embedded Python engine.
    
    Performs a thorough check of the engine installation and identifies
    common problems that might prevent it from working properly.
    
    Returns:
        dict: Diagnostic information about the engine installation
    """
    result = {
        "engine_exists": False,
        "python_exe_exists": False,
        "lib_folder_exists": False,
        "standard_library_exists": False,
        "dll_files_exist": False,
        "issues": [],
        "recommendations": []
    }
    
    # Check if engine folder exists
    if not os.path.exists(ENVIRONMENT.ENGINE_FOLDER):
        result["issues"].append("Engine folder not found: {}".format(ENVIRONMENT.ENGINE_FOLDER))
        result["recommendations"].append("Make sure the _engine folder is properly deployed with the EnneadTab package.")
        return result
    
    result["engine_exists"] = True
    
    # Check if python.exe exists
    python_exe = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    result["python_exe_exists"] = os.path.exists(python_exe)
    if not result["python_exe_exists"]:
        result["issues"].append("Python executable not found in engine folder.")
        result["recommendations"].append("The engine folder should contain python.exe.")
    
    # Check for standard library
    # In embeddable package, standard library is typically in a pythonXXX.zip file 
    # and/or in the Lib folder
    
    # Find any python ZIP files (they contain the standard library)
    zip_files = [f for f in os.listdir(ENVIRONMENT.ENGINE_FOLDER) 
                if f.startswith("python") and f.endswith(".zip")]
    zip_lib_exists = len(zip_files) > 0
    
    # Check Lib folder 
    lib_folder = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "Lib")
    lib_exists = os.path.exists(lib_folder)
    result["lib_folder_exists"] = lib_exists
    
    # Consider standard library present if either zip file exists or encodings module is in Lib
    encodings_folder = os.path.join(lib_folder, "encodings") if lib_exists else ""
    encodings_exists = os.path.exists(encodings_folder) if lib_exists else False
    
    # The standard library is available if:
    # - The Lib folder exists and has the encodings module, OR
    # - A Python ZIP file with standard library exists
    result["standard_library_exists"] = encodings_exists or zip_lib_exists
    
    if not result["standard_library_exists"]:
        result["issues"].append("Python standard library not found.")
        result["recommendations"].append(
            "Make sure you're using a complete Python embeddable package. "
            "The standard library should be present either in the Lib folder "
            "or as a zip file (python3XX.zip)."
        )
    
    # Check DLL files
    required_dlls = ["python3.dll"]
    missing_dlls = []
    for dll in required_dlls:
        if not os.path.exists(os.path.join(ENVIRONMENT.ENGINE_FOLDER, dll)):
            missing_dlls.append(dll)
    
    result["dll_files_exist"] = len(missing_dlls) == 0
    if not result["dll_files_exist"]:
        result["issues"].append("Missing required DLL files: {}".format(", ".join(missing_dlls)))
        result["recommendations"].append("Engine folder should contain all required DLL files for Python to run properly.")
    
    return result

def verify_engine():
    """Verify that the Python engine is properly installed and functioning.
    
    This runs a simple test script to check that the Python engine can be
    executed and returns basic information about the environment.
    
    Returns:
        dict: Information about the engine status and environment
    """
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    result = {
        "engine_exists": os.path.exists(engine_path),
        "engine_path": engine_path,
        "engine_folder": ENVIRONMENT.ENGINE_FOLDER,
        "engine_folder_content": [],
        "test_result": None,
        "diagnostics": diagnose_engine_issue(),
        "error": None
    }
    
    # Check engine folder content
    if os.path.exists(ENVIRONMENT.ENGINE_FOLDER):
        try:
            result["engine_folder_content"] = os.listdir(ENVIRONMENT.ENGINE_FOLDER)
        except Exception as e:
            result["error"] = "Error listing engine folder: {}".format(str(e))
    
    # Run a test script if engine exists
    if result["engine_exists"]:
        test_code = """
import sys
import os

print("Test script running")
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Working directory:", os.getcwd())
"""
        test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "engine_test.py")
        try:
            with open(test_file, "w") as f:
                f.write(test_code)
            
            success, stdout, stderr = cast_python(test_file, wait=True)
            result["test_result"] = {
                "success": success,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as e:
            result["error"] = "Error running test: {}".format(str(e))
        finally:
            # Clean up
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:
                    pass
    
    return result

if __name__ == "__main__":
    sample_script = """
import sys
import os

print ("############# this is a test to print some basic info ##############")
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Working directory:", os.getcwd())

import requests
print ("requests module is available")


import tkinter
print ("tkinter module is available")

import tkinter.ttk
print ("ttk module is available")
print ("############# end of test ##############")
"""
    test_file = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "test.py")
    try:
        with open(test_file, "w") as f:
            f.write(sample_script)
        
        print("Engine folder:", ENVIRONMENT.ENGINE_FOLDER)
        print("Engine exists:", os.path.exists(os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")))
        
        success, stdout, stderr = cast_python(test_file, wait=True)
        
        print("Execution successful:", success)
        if stdout:
            print("Output:", stdout)
        if stderr:
            print("Error:", stderr)
            
        # Also run engine verification
        print("\nRunning engine verification...")
        verification = verify_engine()
        for key, value in verification.items():
            if key == "engine_folder_content":
                print("Engine folder content: [{} items]".format(len(value)))
                for item in value:
                    print("  -", item)
            elif key == "diagnostics":
                print("Diagnostics:")
                print("  - Engine exists:", value["engine_exists"])
                print("  - Python.exe exists:", value["python_exe_exists"])
                print("  - Lib folder exists:", value["lib_folder_exists"])
                print("  - Standard library exists:", value["standard_library_exists"])
                print("  - DLL files exist:", value["dll_files_exist"])
                
                if value["issues"]:
                    print("  - Issues detected:")
                    for issue in value["issues"]:
                        print("    * {}".format(issue))
                
                if value["recommendations"]:
                    print("  - Recommendations:")
                    for rec in value["recommendations"]:
                        print("    * {}".format(rec))
            elif key == "test_result" and value:
                print("Test result: {}".format("SUCCESS" if value.get("success") else "FAILED"))
                if value.get("stdout"):
                    print("Test output:", value.get("stdout"))
                if value.get("stderr") and not success:
                    print("Test errors:", value.get("stderr"))
            else:
                print("{}: {}".format(key, value))
            
    except Exception as e:
        print("Test failed: {}".format(str(e)))
    finally:
        # Clean up
        if os.path.exists(test_file):
            try:
                os.remove(test_file)
            except:
                pass
