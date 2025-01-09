import os
import io
import traceback
import time
import json
import shutil
import socket


GLOBAL_SETTING_FILE = 'setting_{}.sexyDuck'.format(os.environ["USERPROFILE"].split("\\")[-1])

ECOSYSTEM_FOLDER = "{}\\Documents\\EnneadTab Ecosystem".format(os.environ["USERPROFILE"])
DUMP_FOLDER = "{}\\Dump".format(ECOSYSTEM_FOLDER)
DIST_FOLDER = os.path.join(ECOSYSTEM_FOLDER, "EA_Dist")
CORE_LIB_FOLDER = os.path.join(DIST_FOLDER, "Apps","lib")
EXE_PRODUCT_FOLDER = os.path.join(CORE_LIB_FOLDER, "ExeProducts")
for _folder in [ECOSYSTEM_FOLDER, DUMP_FOLDER]:
    if not os.path.exists(_folder):
        os.makedirs(_folder)

DB_FOLDER = "L:\\4b_Applied Computing\\EnneadTab-DB"
USER_NAME = os.environ["USERPROFILE"].split("\\")[-1]

def is_avd():
    computer_name = socket.gethostname()
    return "avd" in computer_name.lower() or "gpupd" in computer_name.lower()


     
def find_main_repo():
    for root, dirs, files in os.walk(os.environ['USERPROFILE']):
        if 'EnneadTab-OS' in dirs:
            return os.path.join(root, 'EnneadTab-OS')
    return os.path.join(ECOSYSTEM_FOLDER, 'EA_Dist')

def try_catch_error(func):

    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out

        except PermissionError:
            print ("[WinError 32] The process cannot access the file because it is being used by another process")
        except EOFError:
            print ("fine.....")
        except Exception as e:
            error = traceback.format_exc()

            error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
            error_file = get_file_in_dump_folder("error_log_{}.txt".format(func.__name__))

            with open(error_file, "w") as f:
                f.write(error)

            username = os.environ["USERPROFILE"].split("\\")[-1]
            if username in ["szhang"]:
                os.startfile(error_file)

    return wrapper


def get_file_in_dump_folder(file_name):
    return "{}\\{}".format(DUMP_FOLDER, file_name)

def get_data(file_name):
    filepath = get_file_in_dump_folder(file_name)
    

    if not os.path.exists(filepath):
        return {}

    temp_file = get_file_in_dump_folder("_temp_exe_data_" + file_name)
    shutil.copyfile(filepath, temp_file)
    try:
        with open(temp_file, "r", encoding='utf-8') as f:
            dict = json.load(f)
        return dict
    except:
        print(traceback.format_exc())
        return {}

def set_data(dict, file_name):
    filepath = get_file_in_dump_folder(file_name)
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)



def show_splash_screen(image):
    """create the data bit file and call SpalshScreen.exe"""
    dict = {"image":image}
    set_data(dict, "splash_data.sexyDuck")
    exe = "{}\\EA_Dist\\Apps\\lib\\ExeProducts\\SplashScreen.exe"
    if os.path.exists(exe):
        os.startfile(exe)

def hide_splash_screen():
    """delete the data bit file"""
    data_file = get_file_in_dump_folder("splash_data.sexyDuck")
    if os.path.exists(data_file):
        os.remove(data_file)



def get_setting(key, default_value=None):
    data = get_data(GLOBAL_SETTING_FILE)
    return data.get(key, default_value)


def get_username():
    return os.environ["USERPROFILE"].split("\\")[-1]




def get_list(filepath):
    extention = os.path.split(filepath)[1]
    local_path = get_file_in_dump_folder("exe_temp{}".format(extention))
    shutil.copyfile(filepath, local_path)


    with io.open(local_path, encoding="utf8") as f:
        lines = f.readlines()
  
    return map(lambda x: x.replace("\n", ""), lines)


def try_open_app(app_name):
    
    exe_product_folder = os.path.join(CORE_LIB_FOLDER, "ExeProducts")


    app_name = app_name.replace(".exe", "")
    app_address = app_name + ".exe"
    if exe_product_folder not in app_address:
        app_address = os.path.join(exe_product_folder, app_address)

    if not os.path.exists(app_address):
        print ("App not found: {}".format(app_address))
        return
    
    temp_exe_name = "_temp_exe_{}_{}.exe".format(app_name, int(time.time()))
    temp_exe = DUMP_FOLDER + "\\" + temp_exe_name
    shutil.copyfile(app_address, temp_exe)
    os.startfile(temp_exe)
    for file in os.listdir(DUMP_FOLDER):
        if file.startswith("_temp_exe_"):
            # ignore if this temp file is less than 1 day old
            if time.time() - os.path.getmtime(os.path.join(DUMP_FOLDER, file)) < 86400:
                continue
            try:
                os.remove(os.path.join(DUMP_FOLDER, file))
            except:
                pass

def messenger(note):
    data = {}
    data["main_text"] = note
    data["animation_in_duration"] = 0.5
    data["animation_stay_duration"] = 5
    data["animation_fade_duration"] = 2
    data["width"] = 1200
    data["height"] =  150 + str(note).count("\n") * 40

    data["x_offset"] = 0

    set_data(data, "messenger_data.sexyDuck")

    try_open_app("Messenger")

if __name__ == "__main__":
    messenger("Hello, world!")
