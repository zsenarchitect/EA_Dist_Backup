# run this in py2.7 becasue it is also called from start.py

import os
import json
import io
import logging
import traceback
import codecs

logging.basicConfig(level=logging.INFO)

def get_pyrevit_extension_json():
    username = os.environ.get('USERNAME')
    file_path = "C:\\Users\\{}\\AppData\\Roaming\\pyRevit-Master\\extensions\\extensions.json".format(username)
    return file_path
    
def update_pyrevit_extension_json():
    file_path = get_pyrevit_extension_json()
    ennead_tab_data = {
        "builtin": "False",
        "type": "extension",
        "rocket_mode_compatible": "True",
        "name": "EnneadTab",
        "description": "Ennead collection of tools for Revit.",
        "author": "Sen Zhang",
        "author_profile": "https://ei.ennead.com/page/964/enneadtab-ecosystem",
        "url": "https://github.com/zsenarchitect/EnneadTab.git",
        "website": "https://ei.ennead.com/page/964/enneadtab-ecosystem",
        "image": "",
        "dependencies": []
    }

    if not os.path.exists(file_path):
        return None
    
    with io.open(file_path, encoding='utf8') as f:
        try:
            data = json.load(f)
        except:
            data = {'extensions':[]}

    extensions = data.get('extensions', [])
    found = False

    for ext in extensions:
        if ext['name'] == 'EnneadTab':
            ext.update(ennead_tab_data)
            found = True
            break

    if not found:
        extensions.append(ennead_tab_data)

 


    with codecs.open(file_path, 'w', 'utf-8') as file:  # Use codecs.open with utf-8 encoding
        json.dump(data, file, ensure_ascii=False, indent=4)  # Set ensure_ascii to False


    try: 
        #if i can import Autodesk then I am in revit mode, then should exit
        import Autodesk.Revit
        return
    except:
        # only play sound when in exe or IDE mode
        alert_finish()


def alert_finish():
    #play window alert sound
    import winsound
    duration = 100  # milliseconds
    freqs = [440,
            500,
            600,
            900]# Hz
    for i,f in enumerate(freqs):
        if i == len(freqs)-1:
            duration = 400
        winsound.Beep(f, duration)
    
if __name__ == "__main__":
    try:
        update_pyrevit_extension_json()
    except Exception as e:
        print(traceback.format_exc())

        import shutil

        current_folder = os.path.dirname(os.path.abspath(__file__))
        backup_file = os.path.join(current_folder, 'backup_json\\extensions.json')
        file_path = get_pyrevit_extension_json()
        shutil.copy(backup_file, file_path)


    finally:
        pass
        