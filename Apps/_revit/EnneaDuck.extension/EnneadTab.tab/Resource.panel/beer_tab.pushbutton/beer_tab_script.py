#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Designer's break companion that helps you maintain proper work-life balance. This essential utility provides quick access to local refreshment options when you need a mental reset. Perfect for those moments when architectural inspiration requires a change of scenery and a cold beverage."
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

from EnneadTab import ERROR_HANDLE, LOG
import webbrowser

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def beer_tab():
    webbrowser.open("https://beerswithmandy.com/beer-everything-blog/where-to-get-a-beer-in-nyc-financial-district-fidi")


################## main code below #####################


if __name__ == "__main__":
    beer_tab()
