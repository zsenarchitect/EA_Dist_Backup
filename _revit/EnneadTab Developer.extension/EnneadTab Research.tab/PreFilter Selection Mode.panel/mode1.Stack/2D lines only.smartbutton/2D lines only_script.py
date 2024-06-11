from pyrevit.userconfig import user_config
from pyrevit import script,revit
from pyrevit.coreutils.ribbon import ICON_MEDIUM
import pickle

__title__ = "2D Lines"
__doc__ = 'xxxxxxxxxxx'

keyword = "prefilter_2d_lines"




def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    button_icon = script_cmp.get_bundle_file('off.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_MEDIUM)
    script.set_envvar(keyword, False)
    return True

"""
output = script.get_output()
output.self_destruct(30)

"""


def update_checker(all_checker):
    
    return all_checker

def toggle_state():
    new_state = not script.get_envvar(keyword)
    # remove last datafile on start


    script.set_envvar(keyword, new_state)
    script.toggle_icon(new_state)

    datafile = script.get_instance_data_file("prefilter_checker")

    f = open(datafile, 'r')
    old_checker = pickle.load(f)
    f.close()

    new_chaker = update_checker(old_checker)


    f = open(datafile, 'w')
    pickle.dump(new_chaker, f)
    f.close()

state = True
state = False
icon_on_path = script.get_bundle_file('on.png')
icon_off_path = script.get_bundle_file('off.png')
#print state, icon_on_path, icon_off_path


######### main ##########
if __name__ == '__main__':
    toggle_state()
