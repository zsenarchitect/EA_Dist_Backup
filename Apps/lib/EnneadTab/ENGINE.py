import subprocess
import os
import sys
import re
import time


import ENVIRONMENT
import USER
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

# List of modules required by EnneadTab
REQUIREMENTS = [
    "psutil",       # For process management
    "requests",     # For HTTP requests
    "pillow",       # For image processing
]

# Special case modules that are built-in and can't be installed via pip
BUILTIN_MODULES = {
    "tkinter": "Tkinter is a built-in module that comes with Python. If missing, it's likely because you're using an embedded Python without UI components.",
    "_tkinter": "The _tkinter module is a built-in module that comes with Python. If missing, it's likely because you're using an embedded Python without UI components.",
    "tk": "The tk module is part of tkinter, a built-in module that comes with Python."
}

# Module initialization state tracking
_MODULE_INITIALIZED = False
_MODULE_REQUIREMENTS_CHECKED = False

def is_module_installed(module_name):
    """Check if a module is already installed in the engine environment.
    
    Args:
        module_name (str): Name of the module to check
        
    Returns:
        bool: True if module is already installed, False otherwise
    """
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    
    if not os.path.exists(engine_path):
        return False
    
    # Set up environment variables
    env = os.environ.copy()
    env["PYTHONHOME"] = ENVIRONMENT.ENGINE_FOLDER
    
    # Create a more robust script to check for the module and its version
    check_script = """
try:
    import {}
    # Try to get version info if available
    try:
        version = getattr({}, '__version__', 'unknown')
        if version == 'unknown':
            version = getattr({}, 'VERSION', 'unknown')
        print("OK:{}".format(version))
    except:
        print("OK")
except ImportError:
    print("NOT_INSTALLED")
""".format(module_name, module_name, module_name, module_name)
    
    # Write the check script to a temporary file
    temp_script = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "check_module.py")
    try:
        with open(temp_script, "w") as f:
            f.write(check_script)
        
        # Execute the check script
        process = subprocess.Popen(
            [engine_path, temp_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=ENVIRONMENT.ENGINE_FOLDER
        )
        
        stdout, stderr = process.communicate()
        
        # More detailed output - show the version if available
        if "OK:" in stdout:
            version = stdout.strip().split("OK:")[1]
            print("Module {} is installed (version: {})".format(module_name, version))
            return True
        return "OK" in stdout
    except Exception as e:
        print("Error checking if module is installed: {}".format(e))
        return False
    finally:
        # Clean up
        if os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except:
                pass
    
    return False

def install_module(module_name):
    """Install a Python module using pip into the engine's site-packages folder.
    
    Args:
        module_name (str): Name of the module to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    # Check if the module is already installed
    if is_module_installed(module_name):
        print("Module {} is already installed.".format(module_name))
        return True
    
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
        print("Installing module: {}".format(module_name))
        process = subprocess.Popen(
            [engine_path, "-m", "pip", "install", module_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=ENVIRONMENT.ENGINE_FOLDER
        )
        
        stdout, stderr = process.communicate()
        success = process.returncode == 0
        
        if success:
            print("Successfully installed module: {}".format(module_name))
        else:
            print("Failed to install module {}: {}".format(module_name, stderr))
            
        return success
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

def _install_requirements():
    """Install all required modules using pip.
    
    This function will install all modules listed in REQUIREMENTS using pip.
    It will only install modules that are not already available in the
    engine's site-packages.
    
    Returns:
        bool: True if all modules were installed successfully, False otherwise
    """
    if not USER.IS_DEVELOPER:
        return True

    print("Dev only note: Installing requirements")
    
    global _MODULE_REQUIREMENTS_CHECKED
    
    # Skip if we've already checked requirements
    if _MODULE_REQUIREMENTS_CHECKED:
        return True
        
    # Create a marker file to track installed modules
    marker_file = os.path.join(ENVIRONMENT.DUMP_FOLDER, "installed_modules.txt")
    installed_modules = set()
    
    # Load previously installed modules if marker file exists
    if os.path.exists(marker_file):
        try:
            with open(marker_file, "r") as f:
                for line in f:
                    module = line.strip()
                    if module:
                        installed_modules.add(module)
        except:
            pass
    
    all_success = True
    modules_to_install = []
    
    # First check which modules need installation
    for module in REQUIREMENTS:
        if module in installed_modules:
            print("Module {} already marked as installed (skipping check)".format(module))
            continue
            
        if not is_module_installed(module):
            modules_to_install.append(module)
    
    # Then install them
    for module in modules_to_install:
        success = install_module(module)
        if success:
            installed_modules.add(module)
            # Update marker file immediately after each successful installation
            try:
                with open(marker_file, "w") as f:
                    for m in installed_modules:
                        f.write(m + "\n")
            except:
                pass
        else:
            all_success = False
            print("Failed to install required module: {}".format(module))
    
    _MODULE_REQUIREMENTS_CHECKED = True        
    return all_success

def cast_python(script, wait=False, max_install_attempts=3, show_console=False):
    """Run a Python script using the embedded Python engine from ENVIRONMENT.ENGINE_FOLDER.
    
    Executes the specified script file using the Python interpreter located
    in the configured engine folder. Captures and returns output/errors.
    If a ModuleNotFoundError is detected, the function will attempt to install
    the missing module and retry the script execution.
    
    Args:
        script (str): Path to the Python script to execute
        wait (bool): When True, waits for the process to complete before returning
        max_install_attempts (int): Maximum number of attempts to install missing modules
        show_console (bool): When True, shows console window during execution
        
    Returns:
        tuple: (success, stdout, stderr) indicating execution result and output
    """
    global _MODULE_INITIALIZED, _MODULE_REQUIREMENTS_CHECKED
    
    # Lazy initialization - only do cleanup and requirements check when cast_python is first called
    if not _MODULE_INITIALIZED:
        _cleanup_on_startup()
        _MODULE_INITIALIZED = True
    
    # Only check requirements the first time we actually run a script
    if not _MODULE_REQUIREMENTS_CHECKED and wait:  # Only check on wait=True calls
        _install_requirements()
        _MODULE_REQUIREMENTS_CHECKED = True
    
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
    
    # Before starting a new process, kill any zombie Python processes from previous runs
    # This helps prevent COM server busy dialogs
    try:
        kill_zombie_python_processes()
    except:
        pass
        
    # Keep track of installed modules to avoid infinite loops
    installed_modules = set()
    attempts = 0
    
    while attempts <= max_install_attempts:
        try:
            # Set up environment variables to ensure isolation from system Python
            env = os.environ.copy()
            
            # Ensure we're using ENGINE folder Python
            env["PYTHONHOME"] = ENVIRONMENT.ENGINE_FOLDER
            
            # Clear any existing PYTHONPATH to avoid conflicts with system Python
            if "PYTHONPATH" in env:
                del env["PYTHONPATH"]
                
            # Add site-packages to PYTHONPATH if it exists
            site_packages = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "Lib", "site-packages")
            if os.path.exists(site_packages):
                env["PYTHONPATH"] = site_packages
                
            # Add the lib folder to PYTHONPATH
            lib_folder = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "Lib")
            if os.path.exists(lib_folder):
                if "PYTHONPATH" in env:
                    env["PYTHONPATH"] = lib_folder + os.pathsep + env["PYTHONPATH"]
                else:
                    env["PYTHONPATH"] = lib_folder
                    
            # Add DLLs folder to PATH if it exists
            dlls_folder = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "DLLs")
            if os.path.exists(dlls_folder):
                env["PATH"] = dlls_folder + os.pathsep + env.get("PATH", "")
                
            # Disable Python user site packages to prevent mixing with local user packages
            env["PYTHONNOUSERSITE"] = "1"
            
            # Add COM automation settings to suppress dialog boxes
            env["PYTHONUNBUFFERED"] = "1"  # Unbuffered output
            env["PYTHONIOENCODING"] = "utf-8"  # Ensure proper encoding
            
            # Set COM automation dialog suppression (Windows specific)
            env["COMMODE"] = "STA"  # Single-threaded apartment COM model
            
            # Very important: Set registry environment to suppress COM error dialogs
            # This ensures COM errors don't show modal dialogs
            # These values are used by the Windows API to control error reporting behavior
            env["HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Windows Error Reporting\\DontShowUI"] = "1"
            env["HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\Windows Error Reporting\\DontShowUI"] = "1"
            env["AVOIDUI"] = "1"  # Custom variable our Python code can check to avoid UI
            
            # For console window suppression:
            env["NO_CONSOLE"] = "1"  # Custom environment variable
            
            # Process flags to prevent popups
            # By default (show_console=False), hide the console window
            # If show_console=True, show the console window
            creation_flags = 0 if show_console else subprocess.CREATE_NO_WINDOW
            
            # On Windows, we add these flags to further suppress console windows
            if not show_console and sys.platform == "win32":
                creation_flags |= 0x08000000  # CREATE_NO_WINDOW
                
                # Try additional Windows-specific console hiding
                try:
                    # Import only on Windows
                    import ctypes
                    # Get the Windows kernel32.dll handle
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    # Tell Windows to hide this console window
                    kernel32.FreeConsole()
                except:
                    pass
            
            # Use Popen to capture output
            process = subprocess.Popen(
                [engine_path, "-c", 
                 # Use -c to run inline Python that suppresses any console window
                 """
import sys, os
import runpy

# Disable any UI elements in subprocesses
os.environ['AVOIDUI'] = '1'
os.environ['NO_CONSOLE'] = '1'

# Redirect stdout/stderr through custom handlers to avoid console
class SuppressStream:
    def __init__(self, original):
        self.original = original
    def write(self, text):
        self.original.write(text)
    def flush(self):
        self.original.flush()

if not os.environ.get('SHOW_CONSOLE'):
    sys.stdout = SuppressStream(sys.stdout)
    sys.stderr = SuppressStream(sys.stderr)

# Execute the actual script
runpy.run_path('{}', run_name='__main__')
                 """.format(script.replace("\\", "\\\\"))],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env,
                cwd=ENVIRONMENT.ENGINE_FOLDER,
                creationflags=creation_flags
            )
            
            # If wait is True, wait for completion and capture output
            if wait:
                try:
                    stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
                    success = process.returncode == 0
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    return False, stdout, "Process took too long to complete and was terminated."
                
                # If successful, return results
                if success:
                    return success, stdout, stderr
                
                # Check for common errors
                if "COM Error" in stderr or "Server Busy" in stderr:
                    # Handle COM automation errors
                    error_msg = """
COM Automation Error: Another process may be using the Python engine.
Try the following:
1. Close any running Python processes 
2. Wait a moment and try again
3. If the problem persists, restart the application
"""
                    return False, stdout, error_msg
                
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
                # For non-wait mode, we still need to handle potential COM errors
                try:
                    # Poll the process briefly to catch immediate failures
                    return_code = process.poll()
                    if return_code is not None and return_code != 0:
                        _, stderr = process.communicate()
                        if "COM Error" in stderr or "Server Busy" in stderr:
                            return False, "", "COM Automation Error: Another process may be using the Python engine."
                    # Process is running successfully (for now)
                    return True, "", ""
                except Exception as e:
                    return False, "", "Error starting script: {}".format(str(e))
                
        except Exception as e:
            if "WinError 5" in str(e):
                return False, "", "Access denied error. Try running as administrator."
            elif "WinError 740" in str(e):
                return False, "", "Elevation required. Try running as administrator."
            return False, "", "Error executing script: {}".format(str(e))
        
        attempts += 1
    
    return False, "", "Maximum module installation attempts reached. Script could not be executed."

def kill_zombie_python_processes(only_kill_oldest=False):
    """Kill any zombie Python processes that might be causing COM server busy errors.
    
    This function looks for Python processes using the engine path and terminates them
    if they appear to be lingering zombie processes from previous EnneadTab operations.
    
    Args:
        only_kill_oldest (bool): If True, only kills processes older than 5 minutes
        
    Returns:
        int: Number of processes terminated
    """
    try:
        import psutil
    except ImportError:
        # Try to install psutil if not available
        if not is_module_installed("psutil"):
            if not install_module("psutil"):
                return 0
        
        # Try again after installation
        try:
            import psutil
        except ImportError:
            return 0
        
    engine_path = os.path.join(ENVIRONMENT.ENGINE_FOLDER, "python.exe")
    
    # Normalize path for comparison
    engine_path = os.path.normcase(os.path.normpath(engine_path))
    count = 0
    my_pid = os.getpid()
    
    # Get all processes first, then sort by creation time
    python_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'exe']):
        try:
            # Check if it's a Python process
            if proc.info['name'] == 'python.exe':
                # Check if it's our engine Python and not ourselves
                if proc.pid != my_pid and 'exe' in proc.info and proc.info['exe']:
                    proc_path = os.path.normcase(os.path.normpath(proc.info['exe']))
                    if proc_path == engine_path:
                        python_processes.append((proc, proc.info['create_time']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort by creation time (oldest first)
    python_processes.sort(key=lambda x: x[1])
    
    current_time = time.time()
    
    # Kill processes based on strategy
    for proc, create_time in python_processes:
        try:
            # Calculate age in seconds
            age = current_time - create_time
            
            if only_kill_oldest:
                # Only kill processes older than 5 minutes
                if age > 300:  # 5 minutes in seconds
                    proc.kill()
                    count += 1
            else:
                # Kill all found processes except ourselves
                proc.kill()
                count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    return count

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

# Clean up any Python processes on module import to prevent server busy errors
def _cleanup_on_startup():
    """Run cleanup operations when the module is first imported.
    
    This function is called automatically when the ENGINE module is imported
    to clean up any lingering Python processes and ensure a clean state.
    """
    global _MODULE_INITIALIZED
    
    # Only run initialization once per Python session
    if _MODULE_INITIALIZED:
        return
        
    try:
        # Kill only the oldest processes to avoid conflicts with current operations
        kill_zombie_python_processes(only_kill_oldest=True)
    except:
        pass
    
    # Mark module as initialized
    _MODULE_INITIALIZED = True


def basic_test():
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

if __name__ == "__main__":
    basic_test()