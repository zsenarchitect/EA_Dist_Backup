import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)


@EnneadTab.ERROR_HANDLE.try_catch_error
def show_example():
    folder = "L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Environmental Analysis Examples"

    import os
    os.startfile(folder)
    EnneadTab.NOTIFICATION.messenger(
        main_text="You will find many helpful office sample grasshopper files to get your started.")

    diagram = "{}\\Toolkit Diagram.png".format(folder)
    os.startfile(diagram)


######################  main code below   #########
if __name__ == "__main__":

    show_example()
