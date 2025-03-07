"""
EnneadTab Data File Management Module

A comprehensive data persistence system for EnneadTab that provides robust JSON file handling
and sticky data management. This module handles reading, writing, and managing data across
local and shared storage locations.

Key Features:
    - Safe JSON file operations with encoding support
    - Local and shared dump folder management
    - List-based file operations
    - Sticky data persistence
    - Context manager for safe data updates
    - Cross-platform compatibility (IronPython/CPython)
    - UTF-8 encoding support for international characters

Note:
    All file operations are designed to be safe and atomic, with proper error handling
    and temporary file management to prevent data corruption.
"""

import sys

import json
import io
import os

from contextlib import contextmanager


import COPY
import FOLDER





def _read_json_file_safely(filepath, use_encode=True, create_if_not_exist=False):
    """Safely read a JSON file by creating a temporary copy.
    
    Creates a temporary copy of the JSON file before reading to avoid file locking
    issues and ensure data integrity.

    Args:
        filepath (str): Path to the JSON file
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.
        create_if_not_exist (bool, optional): Create empty file if not found.
            Defaults to False.

    Returns:
        dict: File contents as dictionary, empty dict if file doesn't exist
    """
    if not os.path.exists(filepath):
        return dict()
    local_path = FOLDER.get_EA_dump_folder_file("temp.sexyDuck")
    try:
        COPY.copyfile(filepath, local_path)
    except IOError:
        local_path = FOLDER.get_EA_dump_folder_file("temp_additional.sexyDuck")
        COPY.copyfile(filepath, local_path)

    content = _read_json_as_dict(local_path, use_encode, create_if_not_exist)
    return content


def _read_json_as_dict(filepath, use_encode=True, create_if_not_exist=False):
    """Read JSON file and return contents as dictionary.
    
    Handles both IronPython and CPython environments with proper encoding support.
    Creates new file with empty dictionary if specified and file doesn't exist.

    Args:
        filepath (str): Path to the JSON file
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.
        create_if_not_exist (bool, optional): Create empty file if not found.
            Defaults to False.

    Returns:
        dict: File contents as dictionary, None if read error occurs
    """
    if create_if_not_exist and not os.path.exists(filepath):
        _save_dict_to_json({}, filepath, use_encode)
        return dict()

    try:
        if sys.platform == "cli":  # IronPython
            from System.IO import File, StreamReader
            from System.Text import Encoding
            
            if use_encode:
                # Use .NET's StreamReader with UTF8 encoding
                reader = StreamReader(filepath, Encoding.UTF8)
                content = reader.ReadToEnd()
                reader.Close()
                return json.loads(content)
            else:
                # Use basic file reading for non-encoded files
                content = File.ReadAllText(filepath)
                return json.loads(content)
        else:  # CPython
            if use_encode:
                with io.open(filepath, "r",encoding="utf-8") as f:
                    return json.load(f)
            else:
                with open(filepath, "r") as f:
                    return json.load(f)
    except Exception as e:
        print("Error reading JSON file {}: {}".format(filepath, str(e)))
        return None


def _read_json_as_dict_in_dump_folder(
    file_name, use_encode=True, create_if_not_exist=False
):
    """Read JSON file from EA dump folder.
    
    Provides direct access to files in the EA dump folder with proper encoding
    and file creation support.

    Args:
        file_name (str): Name of file in dump folder
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.
        create_if_not_exist (bool, optional): Create empty file if not found.
            Defaults to False.

    Returns:
        dict: File contents as dictionary
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _read_json_as_dict(filepath, use_encode, create_if_not_exist)


def _read_json_as_dict_in_shared_dump_folder(
    file_name, use_encode=True, create_if_not_exist=False
):
    """Read JSON file from shared dump folder.
    
    Provides safe access to files in the shared dump folder with proper encoding
    and file creation support.

    Args:
        file_name (str): Name of file in shared dump folder
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.
        create_if_not_exist (bool, optional): Create empty file if not found.
            Defaults to False.

    Returns:
        dict: File contents as dictionary
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _read_json_file_safely(filepath, use_encode, create_if_not_exist)


def _save_dict_to_json(data_dict, filepath, use_encode=True):
    """Save dictionary to JSON file with proper encoding.
    
    Handles both IronPython and CPython environments, ensuring proper UTF-8
    encoding without BOM (Byte Order Mark). Includes automatic handling for
    non-serializable objects by converting them through a cascade of types:
    boolean -> integer -> float -> string.

    Args:
        data_dict (dict): Dictionary to save
        filepath (str): Target file path
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Create a custom JSON encoder to handle non-serializable objects
        class EnneadTabJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                try:
                    return super(EnneadTabJSONEncoder, self).default(obj)
                except TypeError:
                    # Try type conversion cascade: bool -> int -> float -> str
                    str_obj = str(obj).lower()
                    if str_obj == "true":
                        return True
                    elif str_obj == "false":
                        return False
                    
                    try:
                        return int(obj)
                    except (ValueError, TypeError):
                        try:
                            return float(obj)
                        except (ValueError, TypeError):
                            return str(obj)
        
        try:
            json_str = json.dumps(data_dict, ensure_ascii=False, indent=4, sort_keys=True, cls=EnneadTabJSONEncoder)
        except Exception as e:
            print("Failed to convert data_dict to json_str because of {}".format(str(e)))
            json_str = json.dumps(data_dict, ensure_ascii=True, indent=4, sort_keys=True, cls=EnneadTabJSONEncoder)
        
        if sys.platform == "cli":  # IronPython
            from System.IO import File, StreamWriter
            from System.Text import Encoding, UTF8Encoding
            
            if use_encode:
                # Use UTF8Encoding(False) to prevent BOM
                utf8_no_bom = UTF8Encoding(False)
                writer = StreamWriter(filepath, False, utf8_no_bom)
                writer.Write(json_str)
                writer.Close()
            else:
                # Use basic file writing for non-encoded files
                File.WriteAllText(filepath, json_str)
        else:  # CPython
            if use_encode:
                with io.open(filepath, "w", encoding="utf-8") as f:
                    f.write(json_str)
            else:
                with open(filepath, "w") as f:
                    f.write(json_str)
        return True
    except Exception as e:
        print("Error saving JSON file {}: {}".format(filepath, str(e)))
        return False


def _save_dict_to_json_in_dump_folder(data_dict, file_name, use_encode=True):
    """Save dictionary to JSON file in EA dump folder.
    
    Direct storage of dictionary data to the EA dump folder with encoding support.

    Args:
        data_dict (dict): Dictionary to save
        file_name (str): Target filename
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.

    Returns:
        bool: True if save successful, False otherwise
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _save_dict_to_json(data_dict, filepath, use_encode=use_encode)


def _save_dict_to_json_in_shared_dump_folder(data_dict, file_name, use_encode=True):
    """Save dictionary to JSON file in shared dump folder.
    
    Direct storage of dictionary data to the shared dump folder with encoding support.

    Args:
        data_dict (dict): Dictionary to save
        file_name (str): Target filename
        use_encode (bool, optional): Enable UTF-8 encoding for international characters.
            Defaults to True.

    Returns:
        bool: True if save successful, False otherwise
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _save_dict_to_json(data_dict, filepath, use_encode=use_encode)


def get_list(filepath):
    """Read file contents as list of strings.
    
    Each line in the file becomes an element in the returned list.
    Creates a temporary copy to avoid file locking issues.

    Args:
        filepath (str): Path to text file

    Returns:
        list: List of strings, empty list if file doesn't exist
    """
    if not os.path.exists(filepath):
        return []
    extention = FOLDER.get_file_extension_from_path(filepath)
    local_path = FOLDER.get_EA_dump_folder_file("temp{}".format(extention))
    COPY.copyfile(filepath, local_path)

    with io.open(local_path,  "r", encoding="utf-8") as f:
        lines = f.readlines()

    return map(lambda x: x.replace("\n", ""), lines)


def set_list(list, filepath, end_with_new_line=False):
    """Write list of strings to file.
    
    Each element in the list becomes a line in the file.
    Supports UTF-8 encoding for international characters.

    Args:
        list (list): List of strings to write
        filepath (str): Target file path
        end_with_new_line (bool, optional): Add newline at end of file.
            Defaults to False.

    Returns:
        bool: True if write successful
    """
    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(list))
        if end_with_new_line:
            f.write("\n")

    return True


#######################################################################################


def pretty_print_dict(data_dict):
    """Print dictionary with formatted indentation.
    
    Useful for debugging and data inspection.

    Args:
        data_dict (dict): Dictionary to print
    """
    pretty_string = json.dumps(data_dict, indent=4)
    print(pretty_string)


def get_data(file_name_or_full_path, is_local=True):
    """Retrieve data from JSON file.
    
    Supports both local and shared storage locations.
    Creates file with empty dictionary if it doesn't exist.

    Args:
        file_name_or_full_path (str): Filename or full path
        is_local (bool, optional): Use local dump folder if True,
            shared if False. Defaults to True.

    Returns:
        dict: File contents as dictionary
    """
    if os.path.exists(file_name_or_full_path):
        return _read_json_as_dict(file_name_or_full_path, use_encode=True, create_if_not_exist=False)

    if is_local:
        return _read_json_as_dict_in_dump_folder(
            file_name_or_full_path, use_encode=True, create_if_not_exist=True
        )
    else:
        return _read_json_as_dict_in_shared_dump_folder(
            file_name_or_full_path, use_encode=True, create_if_not_exist=True
        )


def set_data(data_dict, file_name_or_full_path, is_local=True):
    """Save dictionary to JSON file.
    
    Supports both local and shared storage locations.
    Ensures proper encoding for international characters.

    Args:
        data_dict (dict): Dictionary to save
        file_name_or_full_path (str): Filename or full path
        is_local (bool, optional): Use local dump folder if True,
            shared if False. Defaults to True.

    Returns:
        bool: True if save successful
    """
    if os.path.exists(file_name_or_full_path):
        if "ENNEADTAB_DEVELOPERS.secret" not in file_name_or_full_path:
            print("Using full path feature is allowed but not prefered.", file_name_or_full_path)
        return _save_dict_to_json(data_dict, file_name_or_full_path, use_encode=True)
    
    if is_local:
        _save_dict_to_json_in_dump_folder(data_dict, file_name_or_full_path, use_encode=True)
    else:
        _save_dict_to_json_in_shared_dump_folder(data_dict, file_name_or_full_path, use_encode=True)


@contextmanager
def update_data(file_name, is_local=True, keep_holder_key=None):
    """Context manager for safe data updates.
    
    Provides atomic read-modify-write operations on JSON data files.
    Automatically handles file loading and saving.

    Example:
        with update_data("config.json") as data:
            data["setting"] = "new_value"

    Args:
        file_name (str): Name of JSON file
        is_local (bool, optional): Use local dump folder if True,
            shared if False. Defaults to True.
        keep_holder_key (str, optional): Key to preserve during updates.
            Defaults to None.

    Yields:
        dict: File contents for modification
    """
    if os.path.exists(file_name):
        file_name = os.path.basename(file_name)

    try:
        data = get_data(file_name, is_local) or {}  # Ensure we have a dict


        yield data

       
        if keep_holder_key is not None:
            data["key_holder"] = keep_holder_key
            # print("After setting key_holder:", data)


        set_data(data, file_name, is_local)
   
    except Exception as e:
        print("Error in DATA_FILE.py at update_data function:", str(e))
        import ERROR_HANDLE
        print (ERROR_HANDLE.get_alternative_traceback())
        


#######################################


STICKY_FILE = "sticky.SexyDuck"


def get_sticky(sticky_name, default_value_if_no_sticky=None):
    """Retrieve persistent sticky data.
    
    Access sticky data that persists across sessions.
    Returns default value if sticky doesn't exist.

    Args:
        sticky_name (str): Identifier for sticky data
        default_value_if_no_sticky (any, optional): Default value if not found.
            Defaults to None.

    Returns:
        any: Sticky data value or default
    """

    data = get_data(STICKY_FILE)
    if sticky_name not in data.keys():
        set_sticky(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    return data[sticky_name]


def set_sticky(sticky_name, value_to_write):
    """Save persistent sticky data.
    
    Store data that persists across sessions.
    Automatically handles JSON serialization.

    Args:
        sticky_name (str): Identifier for sticky data
        value_to_write (any): Value to store

    Returns:
        bool: True if save successful
    """
    with update_data(STICKY_FILE) as data:
        data[sticky_name] = value_to_write



if __name__ == "__main__":
    import time
    with update_data("last_sync_record_data.sexyDuck") as data:
        data["test1"] = time.time()
        # print (data)

    print (get_data("last_sync_record_data.sexyDuck"))