#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"

from pyrevit import script #
import proDUCKtion
import DUCK

def beer_tab():
    DUCK.duck()
    print ("ok")

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    beer_tab()
