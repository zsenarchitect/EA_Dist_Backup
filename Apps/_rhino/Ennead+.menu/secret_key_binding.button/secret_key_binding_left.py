
__title__ = "SecretKeyBinding"
__doc__ = "Setup some secrete shortcut based on Sen's preference."

import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.RHINO import RHINO_ALIAS, RHINO_FORMS

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def secret_key_binding():
    dict = {
        "Control + D": ("Copy", "CtrlD", "_copy"),
        "Control + Q": ("Scale1D", "CtrlQ", "_scale1d"),
        "Control + R": ("Rotate", "CtrlR", "_rotate"),
        "Control + 1": ("Polyline", "Ctrl1", "_polyline"),  
        "F12": ("Search All Commands", "F12", " EA_SearchCommand"),
    }
    selections = RHINO_FORMS.select_from_list(message="Select a shortcut to bind", 
                                              options=sorted(["{}: {}".format(k, v[0]) for k, v in dict.items()]), 
                                              multi_select=True)
    if not selections:
        return
    output_text = "Registered shortcuts:\n\n"
    for selection in selections:
        key = selection.split(": ")[0]
        shortcut = dict[key][1]
        command = dict[key][2]
        RHINO_ALIAS.register_shortcut(shortcut, command)
        print ("Registered shortcut: {} -> {}".format(shortcut, command))
        output_text += "{}: {}\n".format(key, dict[key][0])
    rs.TextOut(output_text)
    
    
if __name__ == "__main__":
    secret_key_binding()
