#!/usr/bin/python
# -*- coding: utf-8 -*-

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import os
import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

# get current script file directory
my_directory = os.path.dirname(os.path.realpath(__file__))

sys.path.append(my_directory)
import city_utility
reload(city_utility)


@EnneadTab.ERROR_HANDLE.try_catch_error
def check_city():

   
    plot_files = city_utility.get_all_plot_files()
    

    file_string_link = ""
    for file in plot_files:
        file_string_link += " Attach \"{}\"".format(file)
    for file in city_utility.CITY_BACKGROUND_FILES:
        file_string_link += " Attach \"{}\"".format(file)
    rs.Command("-WorkSession  {}  Enter".format(file_string_link))

    rs.ZoomExtents(view=None, all=True)
    rs.Command("_SetLinetypeScale 500 _Enter")
    # sc.doc.Linetypes.LinetypeScale = 50.0
  


      




######################  main code below   #########
if __name__ == "__main__":

    check_city()


