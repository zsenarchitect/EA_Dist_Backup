#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Defines the primary error handling function for EnneadTab."""

import traceback
import ENVIRONMENT
import FOLDER
import EMAIL
import USER
import TIME
import NOTIFICATION
import OUTPUT


def try_catch_error(is_silent=False, is_pass = False):
    """Decorator for catching exceptions and sending automated error log emails.

    Args:
        is_silent (bool, optional): If True, email will be sent but no e msg will be visible to user. Defaults to False.
        is_pass (bool, optional): If True, the error will be ignored, user will not be paused and no email will be sent. Defaults to False.
    """
    def decorator(func):
        def error_wrapper(*args, **kwargs):

            try:
                out = func(*args, **kwargs)
                return out
            except Exception as e:
                if is_pass:
                    return
                print_note(str(e))
                print_note("error_Wrapper func for EA Log -- Error: " + str(e))
                error_time = "Oops at {}\n\n".format(TIME.get_formatted_current_time())
                try:
                    error = traceback.format_exc()
                except:
                    error = str(e)

                subject_line = "EnneadTab Auto Error Log"
                if is_silent:
                    subject_line += "(Silent)"
                try:
                    EMAIL.email_error(error_time + error, func.__name__, USER.USER_NAME, subject_line=subject_line)
                except Exception as e:
                    print_note("Cannot send email: {}".format(e))

                if not is_silent:

                    error += "\n\n######If you have EnneadTab UI window open, just close the original EnneadTab window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
                    error_file = FOLDER.get_EA_dump_folder_file("error_general_log.txt")
                    try:
                        import io
                        with io.open(error_file, "w", encoding="utf-8") as f:
                            f.write(error)
                    except IOError as e:
                        print_note(e)

                    output = OUTPUT.get_output()
                    output.write(error_time, OUTPUT.Style.SubTitle)
                    output.write(error)
                    output.insert_division()
                    output.plot()

                if ENVIRONMENT.IS_REVIT_ENVIRONMENT and not is_silent:
                    NOTIFICATION.messenger(
                        main_text="!Critical Warning, close all Revit UI window from EnneadTab and reach to Sen Zhang.")
                    
        error_wrapper.original_function = func
        return error_wrapper
    return decorator



def print_note(*args):
    """For non-developers this is never printed.
    Can handle one or more inputs and shows their types.
    
    Example:
    print_note("hello", 123, ["a", "b"])
    -> [Dev Debug Only Note] 
       str: hello
       int: 123
       list: ['a', 'b']
    """
    if not USER.is_EnneadTab_developer():
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


