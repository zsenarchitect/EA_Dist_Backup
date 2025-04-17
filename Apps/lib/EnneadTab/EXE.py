"""Run apps from the EnneadTab app library.

This module provides functionality to safely execute applications from the EnneadTab library,
with support for legacy versions and temporary file handling.
"""

import os
import time
import ENVIRONMENT
import USER
import NOTIFICATION
import COPY
import ERROR_HANDLE
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
        if USER.IS_DEVELOPER:
            NOTIFICATION.messenger("Failed to open file: {}".format(file_path))
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
        if USER.IS_DEVELOPER:
            print("[Developer only log] No exe found in the location.")
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
                    if USER.IS_DEVELOPER:
                        print("[Developer only log] Removing temporary file: {}".format(file_path))
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    if USER.IS_DEVELOPER:
                        print("[Developer only log] Removing temporary directory: {}".format(file_path))
                    os.rmdir(file_path)
            except OSError as e:
                # This typically happens when file is still in use
                if USER.IS_DEVELOPER:
                    print("[Developer only log] File in use, will remove later: {}".format(file_path))
                continue
            except Exception as e:
                ERROR_HANDLE.print_note("Error removing {}: {}".format(file_path, e))
