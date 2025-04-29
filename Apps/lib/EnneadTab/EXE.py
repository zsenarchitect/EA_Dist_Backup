"""Run apps from the EnneadTab app library.

This module provides functionality to safely execute applications from the EnneadTab library,
with support for legacy versions and temporary file handling.
"""

import os
import time
import random
import ENVIRONMENT
import USER
import NOTIFICATION
import COPY
import ERROR_HANDLE
import threading
import traceback
import subprocess

ENGINE_FOLDER = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "_engine")
if not os.path.exists(ENGINE_FOLDER):
    os.makedirs(ENGINE_FOLDER)

SITE_PACKAGES_FOLDER = os.path.join(ENGINE_FOLDER, "Lib", "site-packages")
if not os.path.exists(SITE_PACKAGES_FOLDER):
    os.makedirs(SITE_PACKAGES_FOLDER)

def _unzip_engine_thread(zip_file, engine_folder):
    """Thread function to handle unzipping process.
    
    Args:
        zip_file (str): Path to the zip file
        engine_folder (str): Path to extract to
    """
    print("Starting unzip thread...")
    print("Zip file:", zip_file)
    print("Engine folder:", engine_folder)
    
    try:
        # Try CPython's zipfile first
        try:
            print("Attempting to use CPython's zipfile...")
            import zipfile
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                print("Extracting files...")
                zip_ref.extractall(engine_folder)
                print("Extraction complete!")
            return
        except ImportError as e:
            print("CPython zipfile import failed:", str(e))
            
        # Fallback to .NET's System.IO.Compression for IronPython
        try:
            print("Attempting to use .NET's System.IO.Compression...")
            import clr
            clr.AddReference('System.IO.Compression')
            clr.AddReference('System.IO.Compression.FileSystem')
            from System.IO.Compression import ZipFile as DotNetZipFile
            print("Extracting files...")
            DotNetZipFile.ExtractToDirectory(zip_file, engine_folder)
            print("Extraction complete!")
        except Exception as e:
            print("Failed to unzip engine:", str(e))
            ERROR_HANDLE.print_note("Failed to unzip engine: {}".format(str(e)))
    except Exception as e:
        print("Unzip engine thread failed:", str(e))
        ERROR_HANDLE.print_note("Unzip engine thread failed: {}".format(str(e)))

def download_python_distribution():
    """Download and extract the Python embeddable zip distribution.
    Returns:
        bool: True if download was successful, False otherwise
    """
    import clr
    clr.AddReference('System')
    from System.Net import WebClient
    import zipfile
    import time
    import os

    python_version = "3.10.11"
    zip_url = "https://www.python.org/ftp/python/{}/python-{}-embed-amd64.zip".format(python_version, python_version)
    install_path = ENGINE_FOLDER
    zip_path = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, "python-{}-embed-amd64.zip".format(python_version))

    if not os.path.exists(install_path):
        os.makedirs(install_path)

    print("Downloading embeddable Python zip to: {}".format(zip_path))
    if not os.path.exists(zip_path):
        client = WebClient()
        client.DownloadFile(zip_url, zip_path)
        print("Download complete!")
    else:
        print("Zip file already exists, skipping download.")

    print("Extracting to: {}".format(install_path))
    try:
        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall(install_path)
        zip_ref.close()
        print("Extraction complete!")
    except Exception as e:
        print("Failed to extract zip: {}".format(str(e)))
        return False

    # Check for python.exe
    python_exe = os.path.join(install_path, "python.exe")
    if os.path.exists(python_exe):
        print("Python installed successfully!")
        return True
    else:
        print("Python installation failed.")
        return False

def ensure_engine_installed():
    """Ensure the Python engine is installed.
    
    This function checks for the Python engine, downloads it if necessary,
    and installs it. Works in both CPython and IronPython environments.
    
    Returns:
        bool: True if engine is installed or successfully installed, False otherwise.
    """
    # Check for critical files that indicate a complete installation
    critical_files = [
        os.path.join(ENGINE_FOLDER, "python.exe"),
        os.path.join(ENGINE_FOLDER, "pythonw.exe"),
        os.path.join(ENGINE_FOLDER, "Lib", "tkinter", "__init__.py"),
        os.path.join(ENGINE_FOLDER, "DLLs", "_tkinter.pyd"),
        os.path.join(ENGINE_FOLDER, "tcl", "tcl8.6", "init.tcl"),
        os.path.join(ENGINE_FOLDER, "tcl", "tk8.6", "tk.tcl")
    ]
    
    # If all critical files exist, we're good
    if all(os.path.exists(f) for f in critical_files):
        return True
        
    # Install Python distribution and wait for completion
    success = download_python_distribution()
    if success:
        # Double check installation
        return all(os.path.exists(f) for f in critical_files)
    return False

def cast_python(exe_name, wait = False):
    """Run a Python script using the engine's Python interpreter.
    
    Args:
        exe_name (str): Name of the script to run (without .py extension)
        wait (bool): Whether to wait for the script to complete
        
    Returns:
        bool: True if script ran successfully, False otherwise
    """
    script_path = os.path.join(ENVIRONMENT.ROOT, "DarkSide", "exes", "source code", "{}.py".format(exe_name))
    if not os.path.exists(script_path):
        ERROR_HANDLE.print_note("Script not found: {}".format(script_path))
        return False

    python_exe = os.path.join(ENGINE_FOLDER, "python.exe")
    if not os.path.exists(python_exe):
        ERROR_HANDLE.print_note("Python engine not found: {}".format(python_exe))
        return False

    def ensure_pip():
        """Ensure pip is available in the Python environment."""
        import subprocess
        try:
            # Check if pip is available
            result = subprocess.run([python_exe, "-m", "pip", "--version"],
                                  capture_output=True,
                                  text=True)
            if result.returncode == 0:
                return True
                
            # If pip is not available, try to install it
            print("Installing pip...")
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = os.path.join(ENGINE_FOLDER, "get-pip.py")
            
            # Download get-pip.py
            import urllib.request
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Run get-pip.py
            result = subprocess.run([python_exe, get_pip_path],
                                  capture_output=True,
                                  text=True)
            
            # Clean up
            if os.path.exists(get_pip_path):
                os.remove(get_pip_path)
                
            return result.returncode == 0
            
        except Exception as e:
            ERROR_HANDLE.print_note("Failed to ensure pip: {}".format(str(e)))
            return False

    def handle_missing_module(module_name):
        """Handle missing module installation with special cases."""
        print("Missing module detected: {}".format(module_name))
        
        # Special case handling
        if module_name == 'tkinter':
            print("Note: tkinter is a built-in module that must be included in Python installation")
            ERROR_HANDLE.print_note("Please use a Python distribution that includes tkinter")
            return False
            
        # Ensure pip is available for other modules
        if not ensure_pip():
            print("Failed to ensure pip is available")
            return False
        
        print("Installing missing module: {}".format(module_name))
        # Try to install the missing module
        ret = subprocess.call([python_exe, "-m", "pip", "install", module_name])
        
        if ret == 0:
            print("Successfully installed {}".format(module_name))
            return True
        else:
            print("Failed to install {}: {}".format(module_name, ret))
            return False

    def run_script():
        try:
            # Set up environment for tkinter
            env = os.environ.copy()
            env["PATH"] = os.path.join(ENGINE_FOLDER, "DLLs") + os.pathsep + env.get("PATH", "")
            env["PYTHONPATH"] = os.path.join(ENGINE_FOLDER, "Lib") + os.pathsep + env.get("PYTHONPATH", "")
            env["TCL_LIBRARY"] = os.path.join(ENGINE_FOLDER, "tcl", "tcl8.6")
            env["TK_LIBRARY"] = os.path.join(ENGINE_FOLDER, "tcl", "tk8.6")
            
            # First attempt to run the script
            proc = subprocess.Popen([python_exe, "-v", script_path], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print("STDOUT:", out)
            print("STDERR:", err)
            print("Return code:", proc.returncode)
            
            # Check for ModuleNotFoundError in output
            if proc.returncode != 0 and "ModuleNotFoundError" in str(err):
                # Extract module name from error message
                import re
                match = re.search(r"No module named '([^']+)'", str(err))
                if match:
                    missing_module = match.group(1)
                    if handle_missing_module(missing_module):
                        # Try running the script again
                        return subprocess.call([python_exe, script_path], env=env)
            
            return proc.returncode
            
        except Exception as e:
            ERROR_HANDLE.print_note("Failed to run script: {}".format(str(e)))
            print (traceback.format_exc())
            return None

    if wait:
        result = run_script()
        return result == 0
    else:
        import threading
        thread = threading.Thread(target=run_script)
        thread.start()
        return True



######################### conveionsla functions############################



def open_document_file(file_path):
    """Open a document file using the system's default application.
    
    Args:
        file_path (str): Path to the document file.
        
    Returns:
        bool: True if file was opened successfully, False otherwise.
    """
    try:
        os.startfile(file_path)
        return True
    except OSError:
        ERROR_HANDLE.print_note("Failed to open file: {}".format(file_path))
        return False

def locate_executable(exe_name):
    """Locate an executable in the standard EnneadTab locations.
    
    Args:
        exe_name (str): Name of the executable without extension.
        
    Returns:
        str: Path to the executable if found, None otherwise.
    """
    exe_name = exe_name.replace(".exe", "")
    
    # Check product folder
    exe_path = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{}.exe".format(exe_name)
    if os.path.exists(exe_path):
        return exe_path
        
    # Check standalone folder
    exe_path = ENVIRONMENT.STAND_ALONE_FOLDER + "\\{}.exe".format(exe_name)
    if os.path.exists(exe_path):
        return exe_path
        
    # Check foldered exe in product folder
    foldered_exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{0}\\{0}.exe".format(exe_name)
    if os.path.exists(foldered_exe):
        return foldered_exe
        
    return None

def create_temporary_copy(exe_path, exe_name):
    """Create a temporary copy of an executable for safe execution.
    
    Args:
        exe_path (str): Path to the original executable.
        exe_name (str): Name of the executable.
        
    Returns:
        str or None: Path to the temporary copy if successful, None otherwise.
    """
    temp_exe_name = "_temp_exe_{}_{}.exe".format(exe_name, int(time.time()))
    
    # Ensure the temporary directory exists
    temp_dir = ENVIRONMENT.WINDOW_TEMP_FOLDER
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception as e:
            if USER.IS_DEVELOPER:
                print("[Developer only log] Failed to create temp directory: {}".format(e))
            return None
            
    # Properly join paths to ensure backslash is included
    temp_exe = os.path.join(temp_dir, temp_exe_name)
    
    COPY.copyfile(exe_path, temp_exe)
    if os.path.exists(temp_exe):
        return temp_exe
    else:
        print("Temp exe not found, maybe failed to copy due to permission issue.")
        return None

def try_open_legacy_app(exe_name):
    """Attempt to open a legacy version of an application.
    
    Args:
        exe_name (str): Name of the executable without extension.
        
    Returns:
        bool: True if legacy app was found and opened, False otherwise.
    """
    head = os.path.join(ENVIRONMENT.L_DRIVE_HOST_FOLDER, "01_Revit", "04_Tools", "08_EA Extensions", "Project Settings", "Exe")
    if os.path.exists(os.path.join(head, exe_name + ".exe")):
        os.startfile(os.path.join(head, exe_name + ".exe"))
        return True
    if os.path.exists(os.path.join(head, exe_name, exe_name + ".exe")):
        os.startfile(os.path.join(head, exe_name, exe_name + ".exe"))
        return True
    return False

def try_open_app(exe_name, legacy_name = None, safe_open = False):
    """Attempt to open an executable file from the app library.
    
    Args:
        exe_name (str): Name of the executable file to open. Can include full path.
        legacy_name (str, optional): Name of legacy executable as fallback.
        safe_open (bool, optional): When True, creates a temporary copy before execution
            to allow for updates while the app is running.
    
    Returns:
        bool: True if application was successfully opened, False otherwise.
    
    Note:
        Safe mode creates temporary copies in the system temp folder with automatic cleanup:
        - OS_Installer/AutoStartup files: cleaned up after 12 hours
        - Other executables: cleaned up after 24 hours
    """
    # Handle non-executable files directly
    abs_name = exe_name.lower()
    if abs_name.endswith((".3dm", ".xlsx", ".xls", ".pdf", ".png", ".jpg")):
        return open_document_file(exe_name)

    # Locate the executable
    exe_path = locate_executable(exe_name)
    if not exe_path:
        ERROR_HANDLE.print_note("No exe found in the location.")
        NOTIFICATION.messenger("No exe found!!!\n{}\n Will try to open legacy app.".format(exe_name))
        
        # Try legacy app
        if legacy_name and try_open_app(legacy_name):
            return True
            
        if try_open_legacy_app(exe_name):
            return True
            
        NOTIFICATION.messenger("No legacy app found!!!\n{}".format(exe_name))
        return False

    # Execute the app
    if safe_open:
        temp_path = create_temporary_copy(exe_path, exe_name.replace(".exe", ""))
        if temp_path:
            os.startfile(temp_path)
            clean_temporary_executables()
            return True
        return False
    else:
        os.startfile(exe_path)
        return True

def clean_temporary_executables():
    if random.random() < 0.9:
        return

    """Clean up temporary executables older than a specified age.
    
    This function removes temporary executable files created by the safe_open option.
    Files are only removed if they are older than a specified threshold:
    - OS_Installer/AutoStartup files: cleaned up after 12 hours
    - Other executables: cleaned up after 24 hours
    
    Files that are currently in use will be skipped and logged for debugging purposes.
    """
    
    def get_ignore_age(file):
        """Determine the age threshold for ignoring files."""
        if "OS_Installer" in file or "AutoStartup" in file:
            return 60 * 60 * 12  # 12 hours
        return 60 * 60 * 24  # 24 hours

    # Iterate through files in the temporary folder
    for file in os.listdir(ENVIRONMENT.WINDOW_TEMP_FOLDER):
        if file.startswith("_temp_exe_"):
            # Check the modification time and ignore if too recent
            file_path = os.path.join(ENVIRONMENT.WINDOW_TEMP_FOLDER, file)
            if time.time() - os.path.getmtime(file_path) < get_ignore_age(file):
                continue
            
            try:
                # Remove the file or directory
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except OSError as e:
                # This typically happens when file is still in use
                continue
            except Exception as e:
                ERROR_HANDLE.print_note("Error removing {}: {}".format(file_path, e))

def ensure_module(module_name):
    """Ensure a Python module is available in the portable engine.
    Installs the module to SITE_PACKAGES_FOLDER if missing, and adds it to sys.path.
    """
    import os
    import sys
    import subprocess

    # Add site-packages to sys.path if not already present
    if SITE_PACKAGES_FOLDER not in sys.path:
        sys.path.append(SITE_PACKAGES_FOLDER)

    try:
        __import__(module_name)
        print("Module '{}' is already installed.".format(module_name))
        return True
    except ImportError:
        print("Module '{}' not found. Installing...".format(module_name))

    python_exe = os.path.join(ENGINE_FOLDER, "python.exe")
    pip_args = [
        python_exe,
        "-m", "pip", "install",
        module_name,
        "--target", SITE_PACKAGES_FOLDER
    ]

    # Try to install the module
    try:
        ret = subprocess.call(pip_args)
        if ret == 0:
            print("Module '{}' installed successfully to site-packages.".format(module_name))
            # Try importing again
            if SITE_PACKAGES_FOLDER not in sys.path:
                sys.path.append(SITE_PACKAGES_FOLDER)
            __import__(module_name)
            return True
        else:
            print("Failed to install module '{}'.".format(module_name))
            return False
    except Exception as e:
        print("Error installing module '{}': {}".format(module_name, e))
        return False

if __name__ == "__main__":
    print (ensure_engine_installed())
    cast_python("Messenger", wait = True)
