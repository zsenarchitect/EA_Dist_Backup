
from pyrevit import script,revit, DB, UI,forms
from pyrevit.coreutils.ribbon import ICON_MEDIUM
import pickle

__title__ = "Dark Mode Color Setting"
__doc__ = 'Personalize the darkmode background color.'


default_dark_color = [12,26,36]
setting_file = script.get_universal_data_file("DARK_MODE_COLOR", file_ext = "txt")

def hex_to_rgb(value):
    value = str(value).lstrip('#')
    lv = len(value)
    return list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def read_data(file):
    try:
        f = open(file, 'r')
        data  = pickle.load(f)
        f.close()
        return data
    except:
        #print "mode color not setup yet"
        f = open(file, 'w')
        pickle.dump(default_dark_color, f)
        f.close()
        return default_dark_color


def pick_color():

    new_color = forms.select_swatch(title = "background color in darkmode", button_name = "Use in NightMode background")
    if new_color == None:
        script.exit()
    new_color = hex_to_rgb(new_color)
    with open(setting_file,"w") as f:
        pickle.dump(new_color,f)
    forms.alert("New background color set as RGB {}-{}-{}.\n\nCycle the Day/Night\nToggle to see effects.".format(new_color[0],\
                                                new_color[1],\
                                                new_color[2]))
######### main ##########
output = script.get_output()
output.close_others()
output.self_destruct(30)

if __name__ == '__main__':
    pick_color()
