__title__ = "ColorPicker"
__doc__ = "Opens Coolors.co color palette generator in default web browser for color scheme inspiration"

import webbrowser
from EnneadTab import ERROR_HANDLE, LOG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def color_picker():
    webbrowser.open("https://coolors.co/d6f6dd-dac4f7-f4989c-ebd2b4-acecf7")

    
if __name__ == "__main__":
    color_picker()
