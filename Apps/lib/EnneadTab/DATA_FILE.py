"""Utilities for writing and reading data to and from JSON files as well as persistent sticky data."""

import sys
import shutil
import json
import io
import os
import traceback
from contextlib import contextmanager


import FOLDER


def _read_json_file_safely(filepath, use_encode=True, create_if_not_exist=False):
    """Duplicate a JSON file then read it to avoid holding the file open status

    Args:
        filepath (str): The path of the file to read.
        use_encode (bool, optional): Might need encoding if there are Chinese characters in the file. Defaults to False.
        create_if_not_exist (bool, optional): Create the file if it does not exist. Defaults to False.

    Returns:
        dict: The contents of the file as a dictionary.
    """
    if not os.path.exists(filepath):
        return dict()
    local_path = FOLDER.get_EA_dump_folder_file("temp.sexyDuck")
    try:
        shutil.copyfile(filepath, local_path)
    except IOError:
        local_path = FOLDER.get_EA_dump_folder_file("temp_additional.sexyDuck")
        shutil.copyfile(filepath, local_path)

    content = _read_json_as_dict(local_path, use_encode, create_if_not_exist)
    return content


def _read_json_as_dict(filepath, use_encode=True, create_if_not_exist=False):
    """Get the data from a JSON file and return it as a dictionary."""
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
                with io.open(filepath, encoding="utf-8") as f:
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
    """Directly access a JSON file in the dump folder and return its contents as a dictionary.

    Args:
        filepath (str): The path of the file to read.
        use_encode (bool, optional): Might need encoding if there are Chinese characters in the file. Defaults to False.
        create_if_not_exist (bool, optional): Create the file if it does not exist. Defaults to False.

    Returns:
        dict: The contents of the file as a dictionary.
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _read_json_as_dict(filepath, use_encode, create_if_not_exist)


def _read_json_as_dict_in_shared_dump_folder(
    file_name, use_encode=True, create_if_not_exist=False
):
    """Directly access a JSON file in the shared dump folder and return its contents as a dictionary.

    Args:
        filepath (str): The path of the file to read.
        use_encode (bool, optional): Might need encoding if there are Chinese characters in the file. Defaults to False.
        create_if_not_exist (bool, optional): Create the file if it does not exist. Defaults to False.

    Returns:
        dict: The contents of the file as a dictionary.
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _read_json_file_safely(filepath, use_encode, create_if_not_exist)


def _save_dict_to_json(data_dict, filepath, use_encode=True):
    """Save a dictionary to a JSON file."""
    try:
        # Convert to JSON string first
        json_str = json.dumps(data_dict, ensure_ascii=False, indent=4)
        
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
    """Direct store a dict to a file in the dump folder.

    Args:
        data_dict (dict): The dictionary to store.
        file_name (str): The name of the file to write to.
        use_encode (bool, optional): Whether to encode the file. Defaults to False.

    Returns:
        bool: Whether the operation was successful or not.
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _save_dict_to_json(data_dict, filepath, use_encode=use_encode)


def _save_dict_to_json_in_shared_dump_folder(data_dict, file_name, use_encode=True):
    """Direct store a dict to a file in shared the dump folder.

    Args:
        data_dict (dict): The dictionary to store.
        file_name (str): The name of the file to write to.
        use_encode (bool, optional): Whether to encode the file. Defaults to False.

    Returns:
        bool: Whether the operation was successful or not.
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _save_dict_to_json(data_dict, filepath, use_encode=use_encode)


def get_list(filepath):
    """Get a list of strings from a file where each line from the file is an element in the list.

    Args:
        filepath (str): The path of the file to read.

    Returns:
        list: A list of strings.
    """
    if not os.path.exists(filepath):
        return []
    extention = FOLDER.get_file_extension_from_path(filepath)
    local_path = FOLDER.get_EA_dump_folder_file("temp{}".format(extention))
    shutil.copyfile(filepath, local_path)

    with io.open(local_path, encoding="utf-8") as f:
        lines = f.readlines()

    return map(lambda x: x.replace("\n", ""), lines)


def set_list(list, filepath, end_with_new_line=False):
    """Write a list of strings to a file where each element in the list is a line in the file.

    Args:
        list (list): A list of strings.
        filepath (str): The path of the file to write to.
        end_with_new_line (bool, optional): Whether to end the file with a new line. Defaults to False.

    Returns:
        bool: Whether the operation was successful or not.
    """
    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(list))
        if end_with_new_line:
            f.write("\n")

    return True


#######################################################################################


def pretty_print_dict(data_dict):
    """Print a dictionary in a pretty format.

    Args:
        data_dict (dict): The dictionary to pretty print.
    """
    pretty_string = json.dumps(data_dict, indent=4)
    print(pretty_string)


def get_data(file_name_or_full_path, is_local=True):
    """Get data from a JSON file and return it as a dictionary.

    Args:
        file_name_or_full_path (str): The name of the file to read, ends with extension, or the full path. The full path is a backward compatiablity feature and is not prefered.
        is_local (bool, optional): Whether the file is in the local dump folder. Defaults to True.

    Returns:
        dict: The contents of the file as a dictionary.
    """
    if os.path.exists(file_name_or_full_path):
        if "ENNEADTAB_DEVELOPERS.secret" not in file_name_or_full_path:
            print("Using full path feature is allowed but not prefered.",file_name_or_full_path)
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
    """Save a dictionary to a JSON file in either the dump folder or the shared dump folder.

    Args:
        data_dict (dict): The dictionary to store.
        file_name_or_full_path (str): The name of the file to write to, ends with extension.
        is_local (bool, optional): Whether the file should be saved to the local dump folder. Defaults to True.
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
    """A context manager that allows you to update data in a JSON file."""
    if os.path.exists(file_name):
        file_name = os.path.basename(file_name)

    try:
        # Set up encoding based on environment
        if sys.platform == "cli":
            from System.Text import Encoding

            encoding = Encoding.UTF8
        else:
            import codecs
            codecs.register(lambda name: codecs.lookup('utf-8') if name == 'utf-8' else None)


        data = get_data(file_name, is_local)



        yield data


        if keep_holder_key is not None:
            data["key_holder"] = keep_holder_key

        set_data(data, file_name, is_local)


    except Exception as e:
        print("Error in update_data at DATA_FILE.py:", str(e))
        print(traceback.format_exc())
        


#######################################


STICKY_FILE = "sticky.SexyDuck"


def get_sticky(sticky_name, default_value_if_no_sticky=None):
    """Get longterm sticky information.

    Args:
        sticky_name (str): The name of the sticky.
        default_value_if_no_sticky (any, optional): The default value to return if the sticky does not exist. Defaults to None.

    Returns:
        any : get the value of the longterm sticky
    """

    data = get_data(STICKY_FILE)
    if sticky_name not in data.keys():
        set_sticky(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    return data[sticky_name]


def set_sticky(sticky_name, value_to_write):
    """Set a long term sticky. The long term sticky will not be cleared after the application is closed.

    Args:
        sticky_name (str): The name of the sticky.
        value_to_write (any): The value to write
    """
    with update_data(STICKY_FILE) as data:
        data[sticky_name] = value_to_write



if __name__ == "__main__":
    import time
    with update_data("last_sync_record_data.sexyDuck") as data:
        data["test1"] = time.time()
        # print (data)

    print (get_data("last_sync_record_data.sexyDuck"))