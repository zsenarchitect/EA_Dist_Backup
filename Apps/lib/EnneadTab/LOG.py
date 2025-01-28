"""Logging functions for recording the usage of EnneadTab scripts."""

import time
from contextlib import contextmanager

import USER
import TIME
import FOLDER
import USER
import DATA_FILE
import ENVIRONMENT

LOG_FILE_NAME = "log_{}.sexyDuck".format(USER.USER_NAME)


@contextmanager
def log_usage(func, *args):
    """Context manager to log the usage of a function.

    Args:
        func (_type_): The function to log.
        *args (_type_): The arguments to pass to the function

    Yields:
        _type_: The result of the function.
        
    """
    t_start = time.time()
    res = func(*args)
    yield res
    t_end = time.time()
    duration = TIME.get_readable_time(t_end - t_start)
    with open(FOLDER.get_EA_dump_folder_file(LOG_FILE_NAME), "a") as f:
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
    """Decorator to log the usage of a function.

    Args:
        script_path (str): The path of the script.
        func_name_as_record (str): The name of the function to record.

    Returns:
        function: The decorated function.        
    """
    # If a script has multiple aliases, just use the lonest one as the record.
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
    """Read the log file of a specific user.

    Args:
        user_name (str, optional): The name of the user. Defaults to current user.
    """
    data = DATA_FILE.get_data(LOG_FILE_NAME)
    print("Printing user log from <{}>".format(user_name))
    import pprint

    pprint.pprint(data, indent=4)


def unit_test():
    pass


###########################################################
if __name__ == "__main__":
    unit_test()
