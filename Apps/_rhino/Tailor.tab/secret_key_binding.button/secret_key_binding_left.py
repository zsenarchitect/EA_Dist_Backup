
__title__ = "SecretKeyBinding"
__doc__ = "Setup some secrete shortcut based on Sen's preference."


from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.RHINO import RHINO_ALIAS, RHINO_FORMS

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def secret_key_binding():
    dict = {
        "CtrlD": "_copy",
        "CtrlQ": "_scale1d",
        "CtrlR": "_rotate",
        "Ctrl1": "_polyline",  
        "F12": "_tailor",
    }
    selections = RHINO_FORMS.select_from_list("Select a shortcut to bind", dict.keys(), multi_select=True)
    if not selections:
        return
    for selection in selections:
        RHINO_ALIAS.register_shortcut(selection, dict[selection])
        print ("Registered shortcut: {} -> {}".format(selection, dict[selection]))


    
    
if __name__ == "__main__":
    secret_key_binding()
