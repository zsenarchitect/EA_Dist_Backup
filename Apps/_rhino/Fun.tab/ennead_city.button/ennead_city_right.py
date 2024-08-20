
__title__ = "EnneadCity"
__doc__ = "Load all city plots to a session."

import rhinoscriptsyntax as rs
import scriptcontext as sc

import os
import sys
from EnneadTab import ERROR_HANDLE, LOG
# get current script file directory
my_directory = os.path.dirname(os.path.realpath(__file__))

sys.path.append(my_directory)
import city_utility # pyright: ignore


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def ennead_city():
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
  
    
if __name__ == "__main__":
    ennead_city()
