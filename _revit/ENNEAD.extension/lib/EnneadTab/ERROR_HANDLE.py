#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import EXE
import ENVIRONMENT_CONSTANTS
import FOLDER
import EMAIL
import USER
import NOTIFICATION

def try_catch_error(func, is_silent=False, is_pass = False):

    def wrapper(*args, **kwargs):

        # print_note ("Wrapper func for EA Log -- Begin: {}".format(func.__name__))
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            # print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            if is_pass:
                return
            print_note(str(e))
            print_note("Wrapper func for EA Log -- Error: " + str(e))
            error = traceback.format_exc()

            subject_line = "EnneadTab Auto Error Log"
            if is_silent:
                subject_line += "(Silent)"
            try:
                EMAIL.email_error(error, func.__name__, USER.get_user_name(
                ), subject_line=subject_line)
            except Exception as e:
                print_note("Cannot send email: {}".format(e))

            if not is_silent:

                error += "\n\n######If you have EnneadTab UI window open, just close the original EnneadTab window(not this textnote). Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
                error_file = "{}\error_log.txt".format(
                    FOLDER.get_user_folder())
                try:
                    with open(error_file, "w") as f:
                        f.write(error)
                except IOError as e:
                    print_note(e)
           
                EXE.open_file_in_default_application(error_file)

            if ENVIRONMENT_CONSTANTS.is_Revit_environment() and not is_silent:
                NOTIFICATION.messenger(
                    main_text="!Critical Warning, close all Revit UI window from EnneadTab and reach to Sen Zhang.")

    return wrapper


def try_catch_error_silently(func):
    return try_catch_error(func, is_silent=True)

def try_pass(func):
    return try_catch_error(func, is_silent=True, is_pass=True)

def print_note(string):
    # show_note = USER.is_enneadtab_developer() # wait until Colin fix the bug

    if USER.is_SZ():
        try:
            from pyrevit import script
            string = str(string)
            script.get_output().print_md(
                "***[DEBUG NOTE]***:{}".format(string))
        except Exception as e:

            print("[DEBUG NOTE]:{}".format(string))
            # print "--Cannot use markdown becasue: {}".format(e)
