"""File and folder management utilities for EnneadTab.

This module provides comprehensive file and folder operations across the EnneadTab
ecosystem, including file copying, backup management, and path manipulation.

Key Features:
- Safe file copying and backup creation
- Path manipulation and formatting
- Folder security and creation
- File extension management
- Local and shared dump folder operations
- Automated backup scheduling

Compatible with Python 2.7 and Python 3.x
"""

import time
import os
import re
from datetime import datetime
import shutil

from ENVIRONMENT import DUMP_FOLDER, USER_DESKTOP_FOLDER, SHARED_DUMP_FOLDER, ONE_DRIVE_DOCUMENTS_FOLDER, PLUGIN_EXTENSION
try:
    import COPY
except Exception as e:
    print(e)

def purge_powershell_folder():
    """Clean up PowerShell transcript folders that match YYYYMMDD pattern.
    
    This function:
    1. Scans Documents folder for YYYYMMDD pattern folders
    2. Checks for PowerShell_transcript files inside
    3. Deletes matching folders
    4. Runs once per day using timestamp check
    """
    # Get the documents folder path
    docs_folder = ONE_DRIVE_DOCUMENTS_FOLDER
    if not os.path.exists(docs_folder):
        return
    
    # Check if we already ran today
    timestamp_file = get_local_dump_folder_file("last_ps_cleanup.txt")
    
    try:
        
        with open(timestamp_file, 'r') as f:
            last_run = f.read().strip()
            if last_run == datetime.now().strftime("%Y%m%d"):
                # print("Already ran cleanup today")
                return
    except:
        pass
        
    # Pattern for YYYYMMDD folders
    date_pattern = re.compile(r"^\d{8}$")
    
    folders_to_delete = []
    
    # Scan for matching folders
    for folder_name in os.listdir(docs_folder):
        folder_path = os.path.join(docs_folder, folder_name)
        
        # Check if it's a directory and matches date pattern
        if os.path.isdir(folder_path) and date_pattern.match(folder_name):
            # Check if contains PowerShell transcripts
            has_ps_transcript = False
            for file in os.listdir(folder_path):
                if "PowerShell_transcript" in file:
                    has_ps_transcript = True
                    break
            if len(os.listdir(folder_path)) == 0:
                folders_to_delete.append(folder_path)
                # print("Found empty folder: {}".format(folder_path))
                    
            if has_ps_transcript:
                folders_to_delete.append(folder_path)
                # print("Found matching folder: {}".format(folder_path))
    
    # Actual deletion
    # print("\nDeleting these folders:")
    deleted_count = 0
    for folder in folders_to_delete:
        try:
            # Try to delete entire folder tree first
            shutil.rmtree(folder)
            deleted_count += 1
        except Exception as e:
            # If folder deletion fails, try deleting individual files
            try:
                files = os.listdir(folder)
                for file in files:
                    file_path = os.path.join(folder, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception:
                        continue
                # Try deleting empty folder again
                os.rmdir(folder)
                deleted_count += 1
            except Exception as e:
                # If folder deletion fails, skip it
                # print("Failed to delete folder {}: {}".format(folder, e))
                continue
    # print("\nSuccessfully deleted {} out of {} folders".format(deleted_count, len(folders_to_delete)))
        
    # Update timestamp file
    with open(timestamp_file, 'w') as f:
        f.write(datetime.now().strftime("%Y%m%d"))
    
    return folders_to_delete



def get_safe_copy(filepath, include_metadata=False):
    """Create a safe copy of a file in the dump folder.

    Creates a timestamped copy of the file in the EA dump folder to prevent
    file conflicts and data loss.

    Args:
        filepath (str): Path to the source file
        include_metadata (bool, optional): If True, preserves file metadata.
            Defaults to False.

    Returns:
        str: Path to the safe copy
    """
    _, file = os.path.split(filepath)
    safe_copy = get_local_dump_folder_file("save_copy_{}_".format(time.time()) + file)
    COPY.copyfile(filepath, safe_copy, include_metadata)
    return safe_copy

def copy_file(original_path, new_path):
    """Copy file to new location, creating directories if needed.

    Args:
        original_path (str): Source file path
        new_path (str): Destination file path

    Note:
        Creates parent directories if they don't exist.
    """
    target_folder = os.path.dirname(new_path)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    COPY.copyfile(original_path, new_path)


def copy_file_to_folder(original_path, target_folder, handle_BW_file = False):
    """Copy file to target folder, preserving filename.

    Args:
        original_path (str): Source file path
        target_folder (str): Destination folder path

    Returns:
        str: Path to the copied file

    Note:
        Creates target folder if it doesn't exist.
    """

    new_path = original_path.replace(os.path.dirname(original_path), target_folder)
    if handle_BW_file:
        new_path = new_path.replace("_BW", "")
    try:
        COPY.copyfile(original_path, new_path)
    except Exception as e:
        print(e)

    return new_path


def secure_folder(folder):
    """Create folder if it doesn't exist.

    Args:
        folder (str): Path to folder to create/verify

    Returns:
        str: Path to secured folder
    """

    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder



def get_file_name_from_path(file_path, include_extension=True):
    """Extract filename from full path.

    Args:
        file_path (str): Full path to file
        include_extension (bool, optional): If True, includes file extension.
            Defaults to True.

    Returns:
        str: Extracted filename
    """
    _, tail = os.path.split(file_path)
    if not include_extension:
        tail = tail.split(".")[0]
    return tail


def get_file_extension_from_path(file_path):
    """Extract file extension from path.

    Args:
        file_path (str): Full path to file

    Returns:
        str: File extension including dot (e.g. '.txt')
    """
    return os.path.splitext(file_path)[1]

def secure_legal_file_name(file_name):
    """Ensure file name is legal for all operating systems.
    
    Args:
        file_name (str): Original filename
        
    """
    return file_name.replace("::", "_").replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace("\\", "-").replace("<", "-").replace(">", "-").replace("|", "-")

def _secure_file_name(file_name):
    """Ensure file has proper extension.
    
    If file has no extension, append PLUGIN_EXTENSION.
    If file already has an extension, use it as is.
    
    Args:
        file_name (str): Original filename
        
    Returns:
        str: Filename with proper extension
    """
    current_extension = get_file_extension_from_path(file_name)
    if current_extension:
        return file_name
    
    return file_name + PLUGIN_EXTENSION


def _get_internal_file_from_folder(folder, file_name):
    """this construct the path but DO NOT garatee exist."""
    return os.path.join(folder, _secure_file_name(file_name))
  

def get_EA_dump_folder_file(file_name):
    """TO-DO:this is for backward compatibility, will remove after May 20 2025"""
    return get_local_dump_folder_file(file_name)

def get_local_dump_folder_file(file_name):
    """Get full path for file in EA dump folder.

    Args:
        file_name (str): Name of file including extension

    Returns:
        str: Full path in EA dump folder
    """
    return _get_internal_file_from_folder(DUMP_FOLDER, file_name)

def get_local_dump_folder_folder(folder_name):
    """Get full path for folder in EA dump folder.

    Args:
        folder_name (str): Name of folder

    Returns:    
        str: Full path in EA dump folder
    """
    return os.path.join(DUMP_FOLDER, folder_name)

def get_shared_dump_folder_file(file_name):
    """Get full path for file in shared dump folder.

    Args:
        file_name (str): Name of file including extension

    Returns:
        str: Full path in shared dump folder
    """
    return _get_internal_file_from_folder(SHARED_DUMP_FOLDER, file_name)



def copy_file_to_local_dump_folder(original_path, file_name=None, ignore_warning=False):
    """Copy file to local dump folder.

    Creates a local copy of a file in the dump folder, optionally with
    a new name.

    Args:
        original_path (str): Source file path
        file_name (str, optional): New name for copied file.
            Defaults to original filename.
        ignore_warning (bool, optional): If True, suppresses file-in-use warnings.
            Defaults to False.

    Returns:
        str: Path to copied file

    Raises:
        Exception: If file is in use and ignore_warning is False
    """
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]

    local_path = get_local_dump_folder_file(file_name)
    try:
        COPY.copyfile(original_path, local_path)
    except Exception as e:
        if not ignore_warning:
            if "being used by another process" in str(e):
                print("Please close opened file first.")
            else:
                raise e

    return local_path


def backup_data(data_file_name, backup_folder_title, max_time=60 * 60 * 24 * 1):
    """Create scheduled backups of data files.

    Decorator that creates timestamped backups of data files at specified intervals.
    Backups are stored in a dedicated backup folder within the EA dump folder.

    Args:
        data_file_name (str): Name of file to backup
        backup_folder_title (str): Name for backup folder
        max_time (int, optional): Backup interval in seconds.
            Defaults to 1 day (86400 seconds).

    Returns:
        function: Decorated function that performs backup
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            out = func(*args, **kwargs)

            backup_folder = get_local_dump_folder_file("backup_" + backup_folder_title)
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            latest_backup_date = None
            for filename in os.listdir(backup_folder):
                if not filename.endswith(PLUGIN_EXTENSION):
                    continue
                backup_date_str = filename.split("_")[0]
                backup_date = time.strptime(backup_date_str, "%Y-%m-%d")
                if not latest_backup_date or backup_date > latest_backup_date:
                    latest_backup_date = backup_date

            today = time.strftime("%Y-%m-%d")
            if (
                not latest_backup_date
                or (
                    time.mktime(time.strptime(today, "%Y-%m-%d"))
                    - time.mktime(latest_backup_date)
                )
                > max_time
            ):
                backup_file_path = os.path.join(
                    backup_folder, "{}_{}".format(today, data_file_name)
                )

                if os.path.exists(get_local_dump_folder_file(data_file_name)):
                    COPY.copyfile(
                        get_local_dump_folder_file(data_file_name), backup_file_path
                    )

            return out

        return wrapper

    return decorator


def cleanup_folder_by_extension(folder, extension, old_file_only=False):
    """Delete files with specified extension from folder.

    Args:
        folder (str): Target folder path
        extension (str): File extension to match (with or without dot)
        old_file_only (bool, optional): If True, only deletes files older than 10 days.
            Defaults to False.

    Returns:
        int: Number of files deleted
    """
    filenames = os.listdir(folder)

    if "." not in extension:
        extension = "." + extension

    count = 0
    for current_file in filenames:
        ext = os.path.splitext(current_file)[1]
        if ext.upper() == extension.upper():
            full_path = os.path.join(folder, current_file)

            if old_file_only:
                if time.time() - os.path.getmtime(full_path) > 60 * 60 * 24 * 10:
                    continue
            try:
                os.remove(full_path)
                count += 1
            except Exception as e:
                print(
                    "Cannot delete file [{}] becasue error: {}".format(current_file, e)
                )
    return count


def secure_filename_in_folder(output_folder, desired_name, extension):
    """Format and secure filename in output folder.

    Ensures proper file naming in output folder, particularly useful for
    Revit exports where filenames may be modified.
    Note that with the new Revit API PDF exporter, this is no longer needed since revit 2022.
    But for image export, this is still needed. Becasue ti always export with e a -Sheet- thing in file name.

    Args:
        output_folder (str): Target folder path
        desired_name (str): Desired filename without extension
        extension (str): File extension including dot (e.g. '.jpg')

    Returns:
        str: Properly formatted filename
    """

    try:
        os.remove(os.path.join(output_folder, desired_name + extension))
    except:
        pass

    # print keyword
    keyword = " - Sheet - "

    for file_name in os.listdir(output_folder):
        if desired_name in file_name and extension in file_name.lower():
            new_name = desired_name

            # this prefix allow longer path limit
            old_path = "\\\\?\\{}\\{}".format(output_folder, file_name)
            new_path = "\\\\?\\{}\\{}".format(output_folder, new_name + extension)
            try:
                os.rename(old_path, new_path)

            except:
                try:
                    os.rename(
                        os.path.join(output_folder, file_name),
                        os.path.join(output_folder, new_name + extension),
                    )

                except Exception as e:
                    print(
                        "filename clean up failed: skip {} becasue: {}".format(
                            file_name, e
                        )
                    )


def wait_until_file_is_ready(file_path):
    """Wait until a file is ready to use.

    Args:
        file_path (str): Path to the file to check

    Returns:
        bool: True if file is ready, False otherwise
    """
    max_attemp = 100
    
    for _ in range(max_attemp):
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb"):
                    return True
            except:
                time.sleep(0.15)
        else:
            time.sleep(0.15)

    return False


if __name__ == "__main__":
    purge_powershell_folder()
    print( "input: test.txt, should return test.txt")
    print ("actual return: {}".format(_secure_file_name("test.txt")))
    print ("\n")
    print( "input: test.sexyDuck, should return test.sexyDuck")
    print ("actual return: {}".format(_secure_file_name("test.sexyDuck")))
    print ("\n")
    print( "input: test, should return test.sexyDuck")
    print ("actual return: {}".format(_secure_file_name("test")))
    print ("\n")
    print( "PLUGIN_EXTENSION: {}".format(PLUGIN_EXTENSION))
