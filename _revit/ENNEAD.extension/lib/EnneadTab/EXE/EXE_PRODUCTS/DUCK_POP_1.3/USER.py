#!/usr/bin/python
# -*- coding: utf-8 -*-
import ENVIRONMENT
import NOTIFICATION
import DATA_FILE
import SPEAK
import os
import FOLDER


def is_rhino_developer():
    if is_SZ():
        return True

    if get_user_name() in ["OtherUserAutodeskId_1", "OtherUserAutodeskId_2"]:
            return True
    return False

def is_revit_developer():
    if is_SZ():
        return True

    if get_autodesk_user_name() in ["OtherUserAutodeskId_1", "OtherUserAutodeskId_2"]:
        return True
    return False


def is_SZ(pop_toast = False, additional_tester_ID = []):
    if ENVIRONMENT.is_Rhino_environment():

        if get_user_name() == "szhang":
            return True
        return False



    if ENVIRONMENT.is_Revit_environment():
        try:
            app = __revit__.Application
        except:
            try:
                app = __revit__
            except:
                if os.environ["USERPROFILE"] == r"C:\Users\szhang":
                    return True
                return False

        if  app.Username == "szhangXNLCX":
            if pop_toast:
                temp_note = "Welcome back! Sen Zhang"
                NOTIFICATION.toast(sub_text = "", main_text = temp_note)
                SPEAK.speak(temp_note)
                # print "#####EnneadTab is operated by Sen Zhang"
            return True

        if app.Username in additional_tester_ID:
            #print "additional test user found = {}".format(app.Username)
            return True

        return False


def get_user_name():
    return os.environ["USERPROFILE"].split("\\")[-1]

def get_autodesk_user_name():
    try:
        import REVIT
        return REVIT.REVIT_APPLICATION.get_application().Username
    except:
        file = DATA_FILE.get_revit_user_file()
        data = DATA_FILE.read_json_file_safely(file)
        key = "Autodesk_ID"
        return data[key]



def get_all_revit_users():
    folder = FOLDER.get_revit_user_folder()
    return [x.replace(".json", "") for x in FOLDER.get_filenames_in_folder(folder) if "Error_Log" not in x]

def get_all_revit_beta_testers(return_email = False, include_SZ = False):
    names = get_all_revit_users()
    names = filter(lambda x: is_revit_beta_tester(x, include_SZ), names)
    if return_email:
        return ["{}@ennead.com".format(x) for x in names]
    return names


def is_revit_beta_tester(name = None, include_SZ = False):

    if include_SZ:
        if get_user_name() == "szhang":
            return True


    if not name:
        name = get_user_name()


    file = DATA_FILE.get_revit_user_file(name)
    
    # for SH people they cannot get a valid setting file, so i will try everyone as Non tester
    if not os.path.exists(file):
        return False
    
    
    data = DATA_FILE.read_json_file_safely(file)
    if not data:
        return False
    key = "is_beta_tester"
    if not data.has_key(key):
        data[key] = False
        set_revit_beta_tester(is_tester = False)
        return False
    return data[key]

def set_revit_beta_tester(is_tester):
    file = DATA_FILE.get_revit_user_file()
    data = DATA_FILE.read_json_file_safely(file)
    key = "is_beta_tester"
    data[key] = is_tester
    DATA_FILE.save_dict_to_json(data, file)




#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")