#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Error handling and logging utilities for EnneadTab.

This module provides comprehensive error handling, logging, and reporting
functionality across the EnneadTab ecosystem. It includes automated error
reporting, developer debugging tools, and user notification systems.

Key Features:
- Automated error catching and logging
- Developer-specific debug messaging
- Error email notifications
- Stack trace formatting
- Silent error handling options
"""

try:
    import ENVIRONMENT
    import FOLDER
    import EMAIL
    import USER
    import TIME
    import NOTIFICATION
    import OUTPUT
except Exception as e:
    print(e)

# Add recursion depth tracking
_error_handler_recursion_depth = 0
_max_error_handler_recursion_depth = 50  # Set a reasonable limit

def get_alternative_traceback():
    """Generate a formatted stack trace for the current exception.

    Creates a human-readable stack trace including exception type,
    message, and file locations. Output is visible to developers only.

    Returns:
        str: Formatted stack trace information
    """
    import sys
    OUT = ""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    OUT += "Exception Type: {}".format(exc_type)
    OUT += "\nException Message: {}".format(exc_value)
    while exc_traceback:
        OUT += "\nFile: {}, Line: {}".format(exc_traceback.tb_frame.f_code.co_filename,exc_traceback.tb_lineno )
        exc_traceback = exc_traceback.tb_next

    if USER.IS_DEVELOPER:
        print (OUT)
    return OUT

def try_catch_error(is_silent=False, is_pass = False):
    """Decorator for catching exceptions and sending automated error log emails.

    Wraps functions to provide automated error handling, logging, and notification.
    Can operate in silent mode or pass-through mode for different error handling needs.

    Args:
        is_silent (bool, optional): If True, sends error email without user notification.
            Defaults to False.
        is_pass (bool, optional): If True, ignores errors without notification or email.
            Defaults to False.

    Returns:
        function: Decorated function with error handling
    """
    def decorator(func):
        def error_wrapper(*args, **kwargs):
            global _error_handler_recursion_depth, _max_error_handler_recursion_depth
            
            # Check if we've reached max depth
            if _error_handler_recursion_depth >= _max_error_handler_recursion_depth:
                print("Maximum error handler recursion depth reached ({})".format(_max_error_handler_recursion_depth))
                # Just call the function directly without error handling
                return func(*args, **kwargs)
                
            # Increment depth counter
            _error_handler_recursion_depth += 1
            
            try:
                out = func(*args, **kwargs)
                # Decrement depth counter before returning
                _error_handler_recursion_depth -= 1
                return out
            except Exception as e:
                if is_pass:
                    # Ensure we decrement even when passing
                    _error_handler_recursion_depth -= 1
                    return
                print_note(str(e))
                print_note("error_Wrapper func for EA Log -- Error: " + str(e))
                error_time = "Oops at {}\n\n".format(TIME.get_formatted_current_time())
                error = get_alternative_traceback()
                if not error:
                    try:
                        import traceback
                        error = traceback.format_exc()
                    except Exception as new_e:
                        
                        error = str(e)
                        print (new_e)

                subject_line = "EnneadTab Auto Error Log"
                if is_silent:
                    subject_line += "(Silent)"
                try:
                    EMAIL.email_error(error_time + error, func.__name__, USER.USER_NAME, subject_line=subject_line)
                except Exception as e:
                    print_note("Cannot send email: {}".format(get_alternative_traceback()))

                if not is_silent:

                    error += "\n\n######If you have EnneadTab UI window open, just close the original EnneadTab window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
                    error_file = FOLDER.get_local_dump_folder_file("error_general_log.txt")
                    try:
                        import io
                        with io.open(error_file, "w", encoding="utf-8") as f:
                            f.write(error)
                    except IOError as e:
                        print_note(e)

                    output = OUTPUT.get_output()
                    output.write(error_time, OUTPUT.Style.Subtitle)
                    output.write(error)
                    output.insert_divider()
                    output.plot()

                if ENVIRONMENT.IS_REVIT_ENVIRONMENT and not is_silent:
                    NOTIFICATION.messenger(
                        main_text="!Critical Warning, close all Revit UI window from EnneadTab and reach to Sen Zhang.")
                
                # Make sure to decrement the counter even in case of exception
                _error_handler_recursion_depth -= 1
                    
        error_wrapper.original_function = func
        return error_wrapper
    return decorator



def print_note(*args):
    """Print debug information visible only to developers.

    Formats and displays debug information with type annotations.
    Supports single or multiple arguments of any type.

    Args:
        *args: Variable number of items to display

    Example:
        print_note("hello", 123, ["a", "b"])
        Output:
            [Dev Debug Only Note]
            - str: hello
            - int: 123
            - list: ['a', 'b']
    """
    if not USER.IS_DEVELOPER:
        return
        
    try:
        from pyrevit import script
        output = script.get_output()
        
        # If single argument, keep original behavior
        if len(args) == 1:
            output.print_md("***[Dev Debug Only Note]***:{}".format(str(args[0])))
            return
            
        # For multiple arguments, print type and value for each
        output.print_md("***[Dev Debug Only Note]***")
        for arg in args:
            output.print_md("- *{}*: {}".format(type(arg).__name__, str(arg)))
            
    except Exception as e:
        # Fallback to print if pyrevit not available
        if len(args) == 1:
            print("[Dev Debug Only Note]:{}".format(str(args[0])))
            return
            
        print("[Dev Debug Only Note]")
        for arg in args:
            print("- {}: {}".format(type(arg).__name__, str(arg)))


