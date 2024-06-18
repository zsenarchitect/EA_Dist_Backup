#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import EXE
import ENVIRONMENT
import FOLDER
import EMAIL 
import USER 

def try_catch_error(func, is_silent = False):
    # try:
    #     import os
    #     import NOTIFICATION
    #     if os.environ["USERPROFILE"].split("\\")[-1] == "eshaw" or "szhang":
    #         note = "Ethan you should go rock climbing!"
    #         print (note)
    #         NOTIFICATION.messager(main_text=note)
    #     # print (os.getlogin( ))
    # except Exception as e:
    #     print (e)

    def wrapper(*args, **kwargs):

        #print_note ("Wrapper func for EA Log -- Begin: {}".format(func.__name__))
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            #print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            print_note ( str(e))
            print_note (  "Wrapper func for EA Log -- Error: " + str(e)  )
            error = traceback.format_exc()
            
            try:
                EMAIL.email_error(error, func.__name__, USER.get_user_name(), subject_line = "EnneadTab Auto Email Error Log")
            except Exception as e:
                print_note ( "Cannot send email: {}".format(e))
                
            if not is_silent:
                
                error += "\n\n######If you have EnneadTab UI window open, just close the original EnneadTab window(not this textnote). Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
                error_file = "{}\error_log.txt".format(FOLDER.get_user_folder())
                with open(error_file, "w") as f:
                    f.write(error)
                EXE.open_file_in_default_application(error_file)

    return wrapper


def try_catch_error_silently(func):
    return try_catch_error(func, is_silent = True)

def print_note(string):

    show_note = ENVIRONMENT.is_SZ()
    if show_note:
        try:
            from pyrevit import script
            string = str(string)
            script.get_output().print_md( "***[DEBUG NOTE]***:{}".format(string))
        except Exception as e:

            print ("[DEBUG NOTE]:{}".format(string))
            # print "--Cannot use markdown becasue: {}".format(e)
