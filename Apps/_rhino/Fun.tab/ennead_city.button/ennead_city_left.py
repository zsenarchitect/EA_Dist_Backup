
__title__ = "EnneadCity"
__doc__ = "Work on your plot"

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

    """check user name see if the city has been assigned to him, load the city user json file and check if the user is in the keys, if true then return the city file address and open it in rhino. if the name is not exisitng, then get all the available city files and worksession them in current rhino file, then pop a rhinoscriptsyntax window asking for which plot number to be used for the city. this plot number will be saved to the user data file for future and that file is opened in rhino."""
    plot_file_address = city_utility.get_current_user_plot_file()
    if plot_file_address:
        import clr # pyright: ignore
        is_open = clr.StrongBox[bool](False)

        sc.doc.Open(plot_file_address, is_open)
        return
    
    empty_plots_files = city_utility.get_empty_plot_files()
    print(empty_plots_files)
    file_string_link = ""
    for file in empty_plots_files:
        file_string_link += " Attach \"{}\"".format(file)
    rs.Command("-WorkSession  {}  Enter".format(file_string_link))

    rs.ZoomExtents(view=None, all=True)
    plot_short_names = [name.replace("{}\\".format(city_utility.PLOT_FILES_FOLDER), "").replace(".3dm", "") for name in empty_plots_files]
    plot_number = rs.ListBox(plot_short_names, message="Select a plot number from those avalibale plots", title="EnneadCity")
    if not plot_number:
        return
    print(plot_number)
    city_utility.set_current_user_plot_file("{}\{}.3dm".format(city_utility.PLOT_FILES_FOLDER, plot_number))

    import clr # pyright: ignore
    is_open = clr.StrongBox[bool](False)
    # print 9999
    # print city_utility.get_current_user_plot_file()

    sc.doc.Open(city_utility.get_current_user_plot_file(), is_open)
    rs.Command("_SetLinetypeScale 500 _Enter")

    
if __name__ == "__main__":
    ennead_city()
