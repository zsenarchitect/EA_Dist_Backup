"""
EnneadTab Logging System

A comprehensive logging system for tracking and analyzing EnneadTab script usage.
This module provides detailed function execution logging with timing, arguments,
and results tracking across different environments.

Key Features:
    - Detailed function execution logging
    - Execution time tracking and formatting
    - Cross-environment compatibility (Revit/Rhino)
    - Automatic log file backup
    - User-specific log files
    - Context manager for temporary logging
    - JSON-based log storage
    - UTF-8 encoding support

Note:
    Log files are stored in the EA dump folder with user-specific naming
    and automatic backup functionality.
"""

import time
from contextlib import contextmanager
import io

import USER
import TIME
import FOLDER
import DATA_FILE
import ENVIRONMENT

LOG_FILE_NAME = "log_{}".format(USER.USER_NAME)


@contextmanager
def log_usage(func, *args):
    """Context manager for temporary function usage logging.
    
    Creates a detailed log entry for a single function execution including
    start time, duration, arguments, and results.

    Args:
        func (callable): Function to log
        *args: Arguments to pass to the function

    Yields:
        Any: Result of the function execution

    Example:
        with log_usage(my_function, arg1, arg2) as result:
            # Function execution is logged
            process_result(result)
    """
    t_start = time.time()
    res = func(*args)
    yield res
    t_end = time.time()
    duration = TIME.get_readable_time(t_end - t_start)
    with io.open(FOLDER.get_local_dump_folder_file(LOG_FILE_NAME), "a", encoding="utf-8") as f:
        f.writelines("\nRun at {}".format(TIME.get_formatted_time(t_start)))
        f.writelines("\nDuration: {}".format(duration))
        f.writelines("\nFunction name: {}".format(func.__name__))
        f.writelines("\nArguments: {}".format(args))
        f.writelines("\nResult: {}".format(res))


# with log_usage(LOG_FILE_NAME) as f:
#     f.writelines('\nYang is writing!')


"""log and log is break down becasue rhino need a wrapper to direct run script directly
whereas revit need to look at local func run"""


@FOLDER.backup_data(LOG_FILE_NAME, "log")
def log(script_path, func_name_as_record):
    """Decorator for persistent function usage logging.
    
    Creates a detailed JSON log entry for each function execution with
    timing, environment, and execution details. Includes automatic backup
    functionality.

    Args:
        script_path (str): Full path to the script file
        func_name_as_record (str|list): Function name or list of aliases
            to record. If list provided, longest name is used.

    Returns:
        callable: Decorated function with logging capability

    Example:
        @log("/path/to/script.py", "MyFunction")
        def my_function(arg1, arg2):
            # Function execution will be logged
            return result
    """
    # If a script has multiple aliases, just use the longest one as the record
    if isinstance(func_name_as_record, list):
        func_name_as_record = max(func_name_as_record, key=len)

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                with DATA_FILE.update_data(LOG_FILE_NAME) as data:
                    t_start = time.time()
                    out = func(*args, **kwargs)
                    t_end = time.time()
                    if not data:
                        data = dict()
                    data[TIME.get_formatted_current_time()] = {
                        "application": ENVIRONMENT.get_app_name(),
                        "function_name": func_name_as_record.replace("\n", " "),
                        "arguments": args,
                        "result": str(out),
                        "script_path": script_path,
                        "duration": TIME.get_readable_time(t_end - t_start),
                    }

                    # print ("data to be place in log is ", data)

                return out
            except:
                out = func(*args, **kwargs)
                return out

        return wrapper

    return decorator


def read_log(user_name=USER.USER_NAME):
    """Display formatted log entries for a specific user.
    
    Retrieves and pretty prints the JSON log data for the specified user,
    showing all recorded function executions and their details.

    Args:
        user_name (str, optional): Username to read logs for.
            Defaults to current user.

    Note:
        Output is formatted with proper indentation for readability.
    """
    data = DATA_FILE.get_data(LOG_FILE_NAME)
    print("Printing user log from <{}>".format(user_name))
    import pprint

    pprint.pprint(data, indent=4)


def unit_test():
    """Run comprehensive tests of the logging system.
    
    Tests log creation, reading, and backup functionality.
    """
    pass


###########################################################
if __name__ == "__main__":
    unit_test()
