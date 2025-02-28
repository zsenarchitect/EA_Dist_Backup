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
"""

import time
import os

from ENVIRONMENT import DUMP_FOLDER, USER_DESKTOP_FOLDER, SHARED_DUMP_FOLDER
import COPY

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
    safe_copy = get_EA_dump_folder_file("save_copy_{}_".format(time.time()) + file)
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
        os.mkdir(target_folder)
    COPY.copyfile(original_path, new_path)


def copy_file_to_folder(original_path, target_folder):
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
        os.mkdir(folder)
    return folder


def get_user_document_folder():
    """Get current user's Documents folder path.

    Returns:
        str: Path to user's Documents folder
    """
    return "{}\\Documents".format(os.environ["USERPROFILE"])


def get_file_name_from_path(file_path, include_extension=True):
    """Extract filename from full path.

    Args:
        file_path (str): Full path to file
        include_extension (bool, optional): If True, includes file extension.
            Defaults to True.

    Returns:
        str: Extracted filename
    """
    head, tail = os.path.split(file_path)
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


def get_EA_dump_folder_file(file_name):
    """Get full path for file in EA dump folder.

    Args:
        file_name (str): Name of file including extension

    Returns:
        str: Full path in EA dump folder
    """
    return "{}\\{}".format(DUMP_FOLDER, file_name)


def get_shared_dump_folder_file(file_name):
    """Get full path for file in shared dump folder.

    Args:
        file_name (str): Name of file including extension

    Returns:
        str: Full path in shared dump folder
    """
    return "{}\\{}".format(SHARED_DUMP_FOLDER, file_name)


def copy_file_to_local_dump_folder(original_path, file_name=None, ignore_warning=False):
    """Copy file to local EA dump folder.

    Creates a local copy of a file in the EA dump folder, optionally with
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

    local_path = get_EA_dump_folder_file(file_name)
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

            backup_folder = get_EA_dump_folder_file("backup_" + backup_folder_title)
            if not os.path.exists(backup_folder):
                os.mkdir(backup_folder)

            latest_backup_date = None
            for filename in os.listdir(backup_folder):
                if not filename.endswith(".sexyDuck"):
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

                if os.path.exists(get_EA_dump_folder_file(data_file_name)):
                    COPY.copyfile(
                        get_EA_dump_folder_file(data_file_name), backup_file_path
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

if __name__ == "__main__":
    pass
