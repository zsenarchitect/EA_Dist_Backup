
# import pylnk
# shortcut = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Documents\Tutorials\ENNEAD GRASSHOPPER TEMPLATE.gh - Shortcut.lnk"
# link = pylnk.parse(shortcut)
# print link.description
# print link.path


import time

try: #when in decoder not need to search those func
    import FOLDER
    import DATA_FILE
    import EXE
except:
    pass

def get_decoder_data_file():
    from EnneadTab import FOLDER
    return FOLDER.get_EA_dump_folder_file("SHORTCUT_DECODER.json")


def parse_shortcut(shortcut_path):
    pass

    # save shortcut path to a json file in local dump folder. there should be stage: in, shortcut_path: shortcut_path, target_path:None.
    data = {
        "stage": "in",
        "shortcut_path": shortcut_path,
        "target_path": None}
    DATA_FILE.save_dict_to_json(data, get_decoder_data_file())


    # call abstract PY2 machine to run decoder()
    #EXE.call_py_machine(script_path = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EnneadTab\SHORTCUT.py", func_name = "decoder")
    exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\SHORTCUT\SHORTCUT.exe - Shortcut"
    print exe_location
    EXE.open_file_in_default_application(exe_location)

    # in whle loop check if the stage of this dump file is out, and target_path is no longer None, then break, and return the target_path
    attemp = 0
    max_attemp = 10
    while attemp < max_attemp:
        data = DATA_FILE.read_json_file_safely(get_decoder_data_file())
        if data["stage"] == "out" and data["target_path"] != None:
            return data["target_path"]
        attemp += 1
        print "waiting for shortcut decoder...{}/{}".format(attemp+1, max_attemp)
        time.sleep(1)

def decoder():
    import sys
    sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')

    print get_decoder_data_file()
    from EnneadTab import DATA_FILE
    # read the json file from local dump folder
    data = DATA_FILE.read_json_as_dict(get_decoder_data_file())
    shortcut_path = data["shortcut_path"]


    # use win32com.client to parse the shortcut_path and target_path, set the json value. Also set the stage to out.


    import win32com.client 


    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    print shortcut.Targetpath
    data["target_path"] = shortcut.Targetpath
    data["stage"] = "out"
    DATA_FILE.save_dict_to_json(data, get_decoder_data_file())



if __name__ == "__main__":
    import traceback
    try:
        decoder()
        print "Done"
    except:
        
        error = traceback.format_exc()

        error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
        error_file = "{}\error_log.txt".format("{}\Documents\EnneadTab Settings".format(os.environ["USERPROFILE"]))
        with open(error_file, "w") as f:
            f.write(error)
        import os
        os.startfile(error_file)
    finally:
        print "Done"