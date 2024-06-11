
from pyrevit import script,revit, DB, UI
from pyrevit.coreutils.ribbon import ICON_MEDIUM
import pickle

__title__ = "Day Mode\nNight Mode"
__doc__ = 'Change the view background color to dark to ease eye when working at night'

keyword = "VIEW_MODE"
default_dark_color = [12,26,36]
setting_file = script.get_universal_data_file("DARK_MODE_COLOR", file_ext = "txt")

def read_data(file):

    try:
        f = open(file, 'r')
        data  = pickle.load(f)
        f.close()
        return data
    except:
        print("mode color not setup yet")
        print(file)
        with open(file,'w') as f:

            pickle.dump(default_dark_color, f)

        return default_dark_color

def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    button_icon = script_cmp.get_bundle_file('icon.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_MEDIUM)
    #script.set_envvar(keyword, False)
    return True


def toggle_state():
    new_state = not script.get_envvar(keyword)
    # remove last datafile on start


    script.set_envvar(keyword, new_state)
    icon_on_path = script.get_bundle_file('day.png')
    icon_off_path = script.get_bundle_file('night.png')
    script.toggle_icon(new_state, icon_on_path, icon_off_path)
    #print new_state
    change_background_color(new_state)

def change_background_color(state):
    if state:# this is day time, use white
        revit.doc.Application.BackgroundColor = DB.Color(255,255,255)
        UI.UIThemeManager.CurrentTheme = UI.UITheme.Light
    else:# night time use dark color
        #revit.doc.Application.BackgroundColor = DB.Color(30,30,30)#dark gray
        RGB = read_data(setting_file)
        revit.doc.Application.BackgroundColor = DB.Color(RGB[0],RGB[1],RGB[2])#dark blue
        UI.UIThemeManager.CurrentTheme = UI.UITheme.Dark
######### main ##########
if __name__ == '__main__':
    toggle_state()


output = script.get_output()
output.close_others()
output.self_destruct(30)
