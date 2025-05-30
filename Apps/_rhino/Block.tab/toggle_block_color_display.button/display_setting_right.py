__title__ = "ToggleBlockColorDisplay_Setting"
__doc__ = "Toggle the on/off of block names."


import scriptcontext as sc

from EnneadTab import ENVIRONMENT, LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def display_setting():

    key = "{}_color_block_display_conduit_show_text".format(ENVIRONMENT.PLUGIN_ABBR)
    if not sc.sticky.has_key(key):
        sc.sticky[key] = False
    else:
        sc.sticky[key] = not sc.sticky[key]

    sc.doc.Views.Redraw()



if __name__ == "__main__":
    display_setting()