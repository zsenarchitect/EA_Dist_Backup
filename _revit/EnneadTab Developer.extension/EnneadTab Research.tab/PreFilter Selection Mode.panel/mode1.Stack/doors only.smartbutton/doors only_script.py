from pyrevit.userconfig import user_config
from pyrevit import script,revit
from pyrevit.coreutils.ribbon import ICON_MEDIUM

__title__ = "doors"
__doc__ = 'xxxxxxxxxxx'






def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    button_icon = script_cmp.get_bundle_file('off.png')
    ui_button_cmp.set_icon(button_icon, icon_size=ICON_MEDIUM)
    script.set_envvar("prefilter_doors", False)
    return True

"""
output = script.get_output()
output.self_destruct(30)

"""




def toggle_state():
    new_state = not script.get_envvar("prefilter_doors")
    # remove last datafile on start

    """
    if new_state:
        # try:
        data_filename = script.get_data_file("prefilter_c", "tmp")
        print(data_filename)
        if os.path.exists(data_filename):
            os.remove(data_filename)
        # except Exception:
        #     pass

    """
    script.set_envvar("prefilter_doors", new_state)
    script.toggle_icon(new_state)

state = True
state = False
icon_on_path = script.get_bundle_file('on.png')
icon_off_path = script.get_bundle_file('off.png')
#print state, icon_on_path, icon_off_path


######### main ##########
if __name__ == '__main__':
    toggle_state()
