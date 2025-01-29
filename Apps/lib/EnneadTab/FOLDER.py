"""Utility functions for file and folder operations. Read and write to local and shared dump folders. Format filenames within a folder."""

import time
import os

from ENVIRONMENT import DUMP_FOLDER, USER_DESKTOP_FOLDER, SHARED_DUMP_FOLDER
import COPY

def get_safe_copy(filepath, include_metadata=False):
    _, file = os.path.split(filepath)
    safe_copy = get_EA_dump_folder_file("save_copy_{}_".format(time.time()) + file)
    COPY.copyfile(filepath, safe_copy, include_metadata)
    return safe_copy

def copy_file(original_path, new_path):
    """Copy file from original path to new path. If the new path does not exist, it will be created.

    Args:
        original_path (str): The path of the original file.
        new_path (str): The path of the new file.
    """
    target_folder = os.path.dirname(new_path)
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    COPY.copyfile(original_path, new_path)


def copy_file_to_folder(original_path, target_folder):
    """Copy a file to a specified folder. If the folder does not exist, it will be created.

    Args:
        original_path (str): The path of the original file.
        target_folder (str): The path of the target folder.

    Returns:
        str: The new path of the copied file.
    """

    new_path = original_path.replace(os.path.dirname(original_path), target_folder)
    try:
        COPY.copyfile(original_path, new_path)
    except Exception as e:
        print(e)

    return new_path


def secure_folder(folder):
    """Create a folder if it does not exist.

    Args:
        folder (str): The path of the folder to secure.

    Returns:
        str: The path of the folder.
    """

    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder


def get_user_document_folder():
    """Get the path of the current user's document folder.

    Returns:
        str: The path of the document folder.
    """
    return "{}\\Documents".format(os.environ["USERPROFILE"])


def get_file_name_from_path(file_path, include_extension=True):
    """Extract the file name from a full path.

    Args:
        file_path (str): The full path of the file.
        include_extension (bool, optional): Whether to include the file extension. Defaults to True.

    Returns:
        str: The file name.
    """
    head, tail = os.path.split(file_path)
    if not include_extension:
        tail = tail.split(".")[0]
    return tail


def get_file_extension_from_path(file_path):
    """Extract the file extension from a full path.

    Args:
        file_path (str): The full path of the file.

    Returns:
        str: The file extension.
    """
    return os.path.splitext(file_path)[1]


def get_EA_dump_folder_file(file_name):
    """Get the path of a file in the EA dump folder.

    Args:
        file_name (str): The name of the file, including the extension.

    Returns:
        str: The full path of the file.
    """
    return "{}\\{}".format(DUMP_FOLDER, file_name)


def get_shared_dump_folder_file(file_name):
    """Get the path of a file in the shared dump folder.

    Args:
        file_name (str): The name of the file, including the extension.

    Returns:
        str: The full path of the file.
    """
    return "{}\\{}".format(SHARED_DUMP_FOLDER, file_name)


def copy_file_to_local_dump_folder(original_path, file_name=None, ignore_warning=False):
    """Copy a file to the local EA dump folder.

    Args:
        original_path (str): The path of the original file.
        file_name (str, optional): The name of the file in the dump folder. If not provided, the original file name will be used. Defaults to None.
        ignore_warning (bool, optional): Whether to ignore any warnings. Defaults to False.

    Raises:
        Error: If the file is being used by another process.
        

    Returns:
        str: The path of the copied file.
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
    """Backup data file to a specified folder. 
    The backup folder is created if it does not exist.
    The backup is only performed if the last backup is older than the specified time.

    Args:
        data_file_name (str): The name of the data file to backup.
        backup_folder_title (str): The title of the backup folder.
        max_time (str, optional): The backup interval in seconds. Default is 1 day.
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
    """Delete all files with the specified extension in the specified folder.

    Args:
        folder (str, optional): The path of the folder.
        extension (str, optional): The extension of the files to delete. The dot can be included optionally.
        old_file_only (bool, optional): Whether to delete files older than 10 days. Defaults to False.

    Returns:
        int: The number of files deleted.
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
    """Ensure proper formatting of file name in output folder.
    Commonly used with Revit jpg exports, as Revit will change the file names.

    Args:
        output_folder (str): Folder to search.
        desired_name (str): The desired name of the file. Will use this name in search pattern. Do not include extension!
        extension (str): File extension to lock search to. Include DOT! (e.g. ".jpg")
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
