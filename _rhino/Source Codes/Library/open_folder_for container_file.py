import sys
sys.path.append("..\lib")
import EnneadTab
#import os
#path = r"file:\\L:\4b_Applied Computing\03_Rhino\02_Savanna3D_Block Library\00_Original Files"


#import subprocess
#subprocess.Popen(r'explorer /select, {}'.format(path))

@EnneadTab.ERROR_HANDLE.try_catch_error
def open_folder_for_container_file():

    import webbrowser

    playlist = r"https://download.muuto.com/MediaLibrary/Architect-Files-3D"
    webbrowser.open_new(playlist)
    playlist = r"https://www.hermanmiller.com/resources/3d-models-and-planning-tools/product-models/"
    webbrowser.open_new(playlist)
    playlist = r"https://www.knoll.com/design-plan/resources/furniture-symbols/showcase-symbols"
    webbrowser.open_new(playlist)




if __name__ == "__main__":
    open_folder_for_container_file()
