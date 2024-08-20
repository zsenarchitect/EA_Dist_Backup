

#!/usr/bin/python
# -*- coding: utf-8 -*-


import rhinoscriptsyntax as rs
import scriptcontext as sc

import os
import sys

# get current script file directory
my_directory = os.path.dirname(os.path.realpath(__file__))

sys.path.append(my_directory)
import city_utility # pyright: ignore

from EnneadTab import ERROR_HANDLE, NOTIFICATION

@ERROR_HANDLE.try_catch_error()
def export_from_masterplan():
    used_plots = city_utility.get_occupied_plot_names()
    print("Used plots = " + str(used_plots))
    
    # get groups that is currently visible in view
    for group in rs.GroupNames():


        contents = rs.ObjectsByGroup(group)
        if not contents:
            continue
        is_group_hidden = False
        for content in contents:
            if not rs.IsVisibleInView(content):
                is_group_hidden = True
                
                break
            if rs.IsTextDot(content):
                break
        if is_group_hidden:
            continue
        plot_name = rs.TextDotText(content)#.zfill(3)
        #print plot_name

        rs.UnselectAllObjects()
        rs.SelectObjects(contents)

        if plot_name in used_plots:
            NOTIFICATION.toast(main_text = "Skipping plot {}. File already been claimmed.".format(plot_name))
            print(plot_name)
            continue
        """
        if os.path.exists(filepath):
            NOTIFICATION.toast(main_text = "Skipping plot {}. File already exists".format(plot_name))
            continue
        """
        filepath = "{}\{}.3dm".format(city_utility.PLOT_FILES_FOLDER, plot_name)
        #print filepath
        rs.Command("!_-Export \"{}\" -Enter -Enter".format(filepath))


    rs.UnselectAllObjects()



   
   
    pass




      




######################  main code below   #########
if __name__ == "__main__":

    export_from_masterplan()


